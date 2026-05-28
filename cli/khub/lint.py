import os
import re
from pathlib import Path

def run_lint(hub_path: Path, topic_name: str):
    topic_dir = hub_path / "topics" / topic_name
    wiki_dir = topic_dir / "wiki"
    
    if not wiki_dir.exists():
        return {"broken_links": [], "orphans": []}

    all_files = []
    id_map = {} # title.lower() -> id, filename.lower() -> id
    
    # Discovery Pass (Same as graph.py)
    for root, _, files in os.walk(wiki_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(wiki_dir)).replace("\\", "/")
                all_files.append((file_path, rel_path))
                id_map[file_path.stem.lower()] = rel_path
                id_map[rel_path.lower()] = rel_path
                id_map[file.lower()] = rel_path

    broken_links = []
    targeted_by = set() # Set of rel_paths that are targets of at least one link

    for file_path, rel_path in all_files:
        content = file_path.read_text(errors="ignore")
        links = re.findall(r'\[\[(.*?)\]\]', content)
        
        for target_text in links:
            t_lower = target_text.lower()
            resolved_id = None
            
            if t_lower in id_map:
                resolved_id = id_map[t_lower]
            elif (t_lower + ".md") in id_map:
                resolved_id = id_map[t_lower + ".md"]
            
            if resolved_id:
                targeted_by.add(resolved_id)
            else:
                broken_links.append({
                    "source": rel_path,
                    "target": target_text
                })

    orphans = []
    for _, rel_path in all_files:
        if rel_path not in targeted_by:
            orphans.append({"id": rel_path})

    return {
        "broken_links": broken_links,
        "orphans": orphans
    }
