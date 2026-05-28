import tempfile
import json
import os
from pathlib import Path
from khub.core import init_topic
from khub.graph import build_graph
from khub.lint import run_lint

def test_full_agent_workflow_simulation():
    """
    Simulates the lifecycle of a topic as an AI agent would manage it:
    1. Init
    2. Ingest (Raw -> Wiki)
    3. Graph Build
    4. Lint
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        topic_name = "programming"
        
        # 1. Initialize Topic
        init_topic(hub_path, topic_name)
        topic_dir = hub_path / "topics" / topic_name
        assert (topic_dir / "wiki").exists()
        
        # 2. Simulate Ingestion
        raw_dir = topic_dir / "raw"
        wiki_dir = topic_dir / "wiki"
        
        # Create a raw source
        (raw_dir / "python-intro.md").write_text("Python is a versatile language.")
        
        # Create Wiki pages (Concepts)
        python_md = """---
type: language
tags: [coding, backend]
---
# Python
A popular programming language. Relates to [[Scripts]].
"""
        scripts_md = """---
type: utility
---
# Scripts
Automate tasks using [[Python]].
"""
        (wiki_dir / "Python.md").write_text(python_md)
        (wiki_dir / "Scripts.md").write_text(scripts_md)
        
        # 3. Build Graph
        build_graph(hub_path, topic_name)
        graph_file = topic_dir / "graph.json"
        assert graph_file.exists()
        
        with open(graph_file, "r") as f:
            data = json.load(f)
        
        # Verify 2 nodes and 2 edges (Python <-> Scripts)
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 2
        
        # Verify metadata extraction
        python_node = next(n for n in data["nodes"] if n["id"] == "Python.md")
        assert python_node["metadata"]["type"] == "language"
        
        # 4. Run Lint
        report = run_lint(hub_path, topic_name)
        assert len(report["broken_links"]) == 0
        assert len(report["orphans"]) == 0
        
        # 5. Break it and check Lint
        (wiki_dir / "Scripts.md").write_text("Broken link to [[NonExistent]]")
        report_broken = run_lint(hub_path, topic_name)
        assert len(report_broken["broken_links"]) == 1
        assert report_broken["broken_links"][0]["target"] == "NonExistent"
        # Python is now an orphan because nothing links to it anymore
        orphan_ids = [o["id"] for o in report_broken["orphans"]]
        assert "Python.md" in orphan_ids
