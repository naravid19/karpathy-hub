import os
import json
from pathlib import Path

def init_topic(hub_path: Path, topic_name: str):
    topic_dir = hub_path / "topics" / topic_name
    
    # Create directories
    (topic_dir / "raw").mkdir(parents=True, exist_ok=True)
    (topic_dir / "wiki").mkdir(parents=True, exist_ok=True)
    
    # Create empty index and log if they don't exist
    index_file = topic_dir / "_index.md"
    if not index_file.exists():
        index_file.write_text(f"# {topic_name.capitalize()} Index\n")
        
    log_file = topic_dir / "log.md"
    if not log_file.exists():
        log_file.write_text(f"# {topic_name.capitalize()} Activity Log\n")
    
    # Update global registry
    registry_path = hub_path / "wikis.json"
    registry = {}
    if registry_path.exists():
        with open(registry_path, "r") as f:
            try:
                registry = json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted registry gracefully by starting fresh
                print(f"Warning: Corrupted registry file {registry_path}. Recreating.")
                registry = {}
                
    registry[topic_name] = {"path": f"topics/{topic_name}"}
    
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)
