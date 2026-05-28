import tempfile
import pytest
from pathlib import Path
from khub.core import init_topic
from khub.lint import run_lint

def test_lint_detects_broken_links():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "test")
        
        wiki_dir = hub_path / "topics" / "test" / "wiki"
        # Create a file with a broken link
        (wiki_dir / "page1.md").write_text("Link to [[MissingPage]]")
        
        report = run_lint(hub_path, "test")
        
        assert len(report["broken_links"]) == 1
        assert report["broken_links"][0]["source"] == "page1.md"
        assert report["broken_links"][0]["target"] == "MissingPage"

def test_lint_detects_orphans():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "test")
        
        wiki_dir = hub_path / "topics" / "test" / "wiki"
        # page1 links to page2
        (wiki_dir / "page1.md").write_text("Link to [[page2]]")
        (wiki_dir / "page2.md").write_text("I am linked")
        # page3 is an orphan
        (wiki_dir / "page3.md").write_text("I am alone")
        
        report = run_lint(hub_path, "test")
        
        # page3 should be an orphan
        orphan_ids = [o["id"] for o in report["orphans"]]
        assert "page3.md" in orphan_ids
        # page1 is also technically an orphan if nothing links to it
        assert "page1.md" in orphan_ids
        assert "page2.md" not in orphan_ids

def test_lint_passes_on_clean_hub():
    with tempfile.TemporaryDirectory() as tmpdir:
        hub_path = Path(tmpdir)
        init_topic(hub_path, "test")
        
        wiki_dir = hub_path / "topics" / "test" / "wiki"
        (wiki_dir / "A.md").write_text("[[B]]")
        (wiki_dir / "B.md").write_text("[[A]]")
        
        report = run_lint(hub_path, "test")
        assert len(report["broken_links"]) == 0
        assert len(report["orphans"]) == 0
