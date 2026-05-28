import os
import json
import tempfile
from pathlib import Path
from khub.core import init_topic

def test_init_topic_creates_structure():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "fitness")
        
        topic_dir = hub_path / "topics" / "fitness"
        assert (topic_dir / "raw").exists()
        assert (topic_dir / "wiki").exists()
        assert (topic_dir / "_index.md").exists()
        assert (topic_dir / "log.md").exists()
        
        # Should also create global files
        assert (hub_path / "wikis.json").exists()

def test_init_topic_updates_registry_safely():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "fitness")
        init_topic(hub_path, "coding")
        
        registry_path = hub_path / "wikis.json"
        assert registry_path.exists()
        
        with open(registry_path, "r") as f:
            registry = json.load(f)
            
        assert "fitness" in registry
        assert "coding" in registry

def test_init_topic_duplicate():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "fitness")
        
        # Modify the index file to see if it gets preserved
        topic_dir = hub_path / "topics" / "fitness"
        (topic_dir / "_index.md").write_text("# Custom Index")
        
        # Re-init
        init_topic(hub_path, "fitness")
        
        # Check if it was preserved
        assert (topic_dir / "_index.md").read_text() == "# Custom Index"
        
        registry_path = hub_path / "wikis.json"
        with open(registry_path, "r") as f:
            registry = json.load(f)
        assert "fitness" in registry
        assert len(registry) == 1

def test_init_topic_corruption_recovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        registry_path = hub_path / "wikis.json"
        
        # Create a malformed JSON file
        registry_path.write_text("{ malformed json")
        
        # Should now handle it gracefully and recreate
        init_topic(hub_path, "fitness")
        
        assert registry_path.exists()
        with open(registry_path, "r") as f:
            registry = json.load(f)
        assert "fitness" in registry
