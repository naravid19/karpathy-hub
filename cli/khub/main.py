import argparse
import sys
from pathlib import Path
from khub.core import init_topic
from khub.graph import build_graph
from khub.lint import run_lint

def cli():
    parser = argparse.ArgumentParser(description="Karpathy Hub CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("topic", help="Name of the topic to initialize")
    init_parser.add_argument("--hub", default=".", help="Path to the wiki hub")
    
    graph_parser = subparsers.add_parser("graph")
    graph_parser.add_argument("topic", help="Topic to build graph for")
    graph_parser.add_argument("--hub", default=".", help="Path to the wiki hub")

    lint_parser = subparsers.add_parser("lint")
    lint_parser.add_argument("topic", help="Topic to lint")
    lint_parser.add_argument("--hub", default=".", help="Path to the wiki hub")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "init":
        hub_path = Path(args.hub)
        init_topic(hub_path, args.topic)
        print(f"Initialized topic: {args.topic} at {hub_path}")
    elif args.command == "graph":
        hub_path = Path(args.hub)
        build_graph(hub_path, args.topic)
        print(f"Built graph.json for topic: {args.topic}")
    elif args.command == "lint":
        hub_path = Path(args.hub)
        report = run_lint(hub_path, args.topic)
        
        print(f"Lint Report for Topic: {args.topic}")
        if not report["broken_links"] and not report["orphans"]:
            print("✅ No issues found.")
            return

        if report["broken_links"]:
            print(f"\n❌ Broken Links ({len(report['broken_links'])}):")
            for bl in report["broken_links"]:
                print(f"  - {bl['source']} -> [[{bl['target']}]]")

        if report["orphans"]:
            print(f"\n⚠️ Orphan Pages ({len(report['orphans'])}):")
            for o in report["orphans"]:
                print(f"  - {o['id']}")

if __name__ == "__main__":
    cli()
