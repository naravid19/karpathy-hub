import os
import json
import re
from pathlib import Path

def parse_markdown_links(content: str):
    # Match [[wikilinks]]
    return re.findall(r'\[\[(.*?)\]\]', content)

def parse_frontmatter(content: str):
    """Simple regex-based frontmatter parser for basic key-value pairs."""
    fm_match = re.match(r'^---\s*\r?\n(.*?)\r?\n---\s*\r?\n', content, re.DOTALL)
    metadata = {}
    if fm_match:
        fm_content = fm_match.group(1)
        for line in fm_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, val = line.split(':', 1)
                metadata[key.strip()] = val.strip()
    return metadata

def build_graph(hub_path: Path, topic_name: str):
    topic_dir = hub_path / "topics" / topic_name
    wiki_dir = topic_dir / "wiki"
    
    if not wiki_dir.exists():
        return

    # Pass 1: Collect all valid node IDs and build a resolution map
    all_files = []
    id_map = {} # title.lower() -> id, filename.lower() -> id
    
    for root, _, files in os.walk(wiki_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(wiki_dir)).replace("\\", "/")
                all_files.append((file_path, rel_path))
                
                # Map stem (title) to the ID (e.g., 'quantum' -> 'quantum.md')
                id_map[file_path.stem.lower()] = rel_path
                # Map full relative path (e.g., 'sub/test.md' -> 'sub/test.md')
                id_map[rel_path.lower()] = rel_path
                # Map filename only (e.g., 'test.md' -> 'sub/test.md')
                id_map[file.lower()] = rel_path

    graph = {
        "nodes": [],
        "edges": []
    }
    
    for file_path, rel_path in all_files:
        content = file_path.read_text(errors="ignore")
        
        node = {
            "id": rel_path,
            "title": file_path.stem,
            "metadata": parse_frontmatter(content)
        }
        graph["nodes"].append(node)
        
        links = parse_markdown_links(content)
        for target_text in links:
            # Resolution logic: try to find the matching file ID
            t_lower = target_text.lower()
            resolved_id = None
            
            # Check for matches in id_map
            if t_lower in id_map:
                resolved_id = id_map[t_lower]
            elif (t_lower + ".md") in id_map:
                resolved_id = id_map[t_lower + ".md"]
            
            # Only add edge if it resolves to an existing node
            if resolved_id:
                graph["edges"].append({
                    "source": rel_path,
                    "target": resolved_id
                })
                    
    graph_out = topic_dir / "graph.json"
    with open(graph_out, "w") as f:
        json.dump(graph, f, indent=2)
