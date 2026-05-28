import tempfile
import json
from pathlib import Path
from khub.core import init_topic
from khub.graph import build_graph

def test_build_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "science")
        
        wiki_dir = hub_path / "topics" / "science" / "wiki"
        # Create a dummy markdown file with frontmatter and wikilinks
        md_content = """---
type: concept
tags: [physics]
---
# Quantum Mechanics
Relates to [[Entanglement]] and [[Schrodinger]].
"""
        (wiki_dir / "quantum.md").write_text(md_content)
        
        # Create the target files so they can be resolved
        (wiki_dir / "entanglement.md").write_text("# Entanglement")
        (wiki_dir / "schrodinger.md").write_text("# Schrodinger")
        
        build_graph(hub_path, "science")
        
        graph_file = hub_path / "topics" / "science" / "graph.json"
        assert graph_file.exists()
        
        with open(graph_file, "r") as f:
            data = json.load(f)
            
        assert "nodes" in data
        assert "edges" in data
        # We should have 3 nodes now
        assert len(data["nodes"]) == 3
        
        # Check quantum node
        quantum_node = next(n for n in data["nodes"] if n["id"] == "quantum.md")
        assert quantum_node["title"] == "quantum"
        
        # Check edges
        assert len(data["edges"]) == 2
        edge_targets = [e["target"] for e in data["edges"]]
        assert "entanglement.md" in edge_targets
        assert "schrodinger.md" in edge_targets

def test_build_graph_with_subdirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "science")
        
        wiki_dir = hub_path / "topics" / "science" / "wiki"
        subdir = wiki_dir / "physics"
        subdir.mkdir()
        
        (wiki_dir / "root.md").write_text("Link to [[Subpage]]")
        (subdir / "subpage.md").write_text("I am in a subdir")
        
        build_graph(hub_path, "science")
        
        graph_file = hub_path / "topics" / "science" / "graph.json"
        with open(graph_file, "r") as f:
            data = json.load(f)
            
        edge = data["edges"][0]
        assert edge["source"] == "root.md"
        assert edge["target"] == "physics/subpage.md"

def test_build_graph_circular_dependency():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "science")
        wiki_dir = hub_path / "topics" / "science" / "wiki"
        
        (wiki_dir / "a.md").write_text("Link to [[b]]")
        (wiki_dir / "b.md").write_text("Link to [[a]]")
        
        build_graph(hub_path, "science")
        
        graph_file = hub_path / "topics" / "science" / "graph.json"
        with open(graph_file, "r") as f:
            data = json.load(f)
            
        assert len(data["edges"]) == 2
        sources = [e["source"] for e in data["edges"]]
        targets = [e["target"] for e in data["edges"]]
        assert "a.md" in sources and "b.md" in sources
        assert "a.md" in targets and "b.md" in targets

def test_build_graph_broken_links():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "science")
        wiki_dir = hub_path / "topics" / "science" / "wiki"
        
        (wiki_dir / "a.md").write_text("Link to [[NonExistent]]")
        
        build_graph(hub_path, "science")
        
        graph_file = hub_path / "topics" / "science" / "graph.json"
        with open(graph_file, "r") as f:
            data = json.load(f)
            
        assert len(data["edges"]) == 0

def test_build_graph_frontmatter_extraction():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "science")
        wiki_dir = hub_path / "topics" / "science" / "wiki"
        
        md_content = """---
type: concept
author: Karpathy
---
# Quantum
"""
        (wiki_dir / "quantum.md").write_text(md_content)
        
        build_graph(hub_path, "science")
        
        graph_file = hub_path / "topics" / "science" / "graph.json"
        with open(graph_file, "r") as f:
            data = json.load(f)
            
        quantum_node = data["nodes"][0]
        assert quantum_node["metadata"]["type"] == "concept"
        assert quantum_node["metadata"]["author"] == "Karpathy"
