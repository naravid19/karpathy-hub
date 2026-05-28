# 🧠 Karpathy Hub

Karpathy Hub is a highly efficient, scalable framework for building personal knowledge bases maintained by AI agents. Inspired by **Andrej Karpathy's LLM Wiki Pattern**, it enables humans and AI to co-author a structured library of knowledge without suffering from context window overflow.

The system enforces a strict isolation between topics, allowing an agent to operate within a specific domain with surgical precision while maintaining a global knowledge graph.

---

## 📋 Table of Contents
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Quickstart (AI Extensions)](#-quickstart-ai-extensions)
- [Getting Started (Developer Setup)](#-getting-started-developer-setup)
- [Architecture](#-architecture)
- [Agent Protocol](#-agent-protocol)
- [CLI Reference](#-cli-reference)
- [Testing](#-testing)
- [Philosophy](#-philosophy)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Key Features

- **Topic-Isolated Hub**: Prevents context drift by scoping agent interactions to specific topics.
- **Source-to-Wiki Pipeline**: Immutable `raw` source storage with agent-synthesized `wiki` pages.
- **Knowledge Graph (JSON)**: Programmatic mapping of entities and relationships for advanced querying.
- **Quality Gates**: Built-in linting for broken wikilinks and orphan detection.
- **Agent-First Design**: Optimized for Gemini, Claude, and other interactive CLI agents.

## 🛠️ Tech Stack

- **Language**: Python 3.13+
- **CLI Engine**: Argparse-based automation
- **Data Format**: Markdown (Obsidian-compatible `[[wikilinks]]`)
- **Metadata**: JSON Knowledge Graph & Registry
- **Testing**: Pytest

---

## 🚀 Quickstart (AI Extensions)

If you are using an AI agent (Gemini CLI, Claude Code), you can install Karpathy Hub as an extension to automatically load the **Agent Protocol** and supporting tools.

### Gemini CLI
```bash
gemini extensions install https://github.com/user/karpathy-hub
```

### Claude Code
```bash
/plugin install https://github.com/user/karpathy-hub
```

---

## 🛠️ Getting Started (Developer Setup)

### 1. Prerequisites
- **Python 3.13+** installed.
- **pip** for package management.

### 2. Installation
Clone the repository and install the `khub` CLI in editable mode:

```bash
git clone https://github.com/user/karpathy-hub.git
cd karpathy-hub
pip install -e ./cli
```

### 3. Initialize Your First Topic
Create a new knowledge domain within the hub:

```bash
khub init my-topic --hub ./wiki_hub
```
This command:
1. Creates `wiki_hub/topics/my-topic/`.
2. Scaffolds `raw/` and `wiki/` subdirectories.
3. Initializes `_index.md` and `log.md`.
4. Updates the global `wikis.json` registry.

---

## 🏗️ Architecture

### Directory Structure
```text
karpathy-hub/
├── cli/                # Python Package
│   ├── khub/           # Core library logic
│   │   ├── core.py     # Topic initialization & Registry
│   │   ├── graph.py    # JSON Graph generator
│   │   ├── lint.py     # Link & Orphan validator
│   │   └── main.py     # CLI Entry point
│   └── tests/          # Pytest suite
├── wiki_hub/           # The Knowledge Base
│   ├── wikis.json      # Global registry of all topics
│   └── topics/         # Topic containers
│       └── <topic>/
│           ├── _index.md   # Human-readable entry point
│           ├── graph.json  # Machine-readable relationship map
│           ├── log.md      # Activity audit trail
│           ├── raw/        # Immutable source materials
│           └── wiki/       # Synthesized agent notes
└── AGENTS.md           # The "Constitution" for AI contributors
```

### The Ingestion Pipeline
1. **Source Capture**: A raw document (article, chat log, transcript) is saved to `raw/`.
2. **Extraction**: The Agent reads the source and identifies key entities/concepts.
3. **Synthesis**: The Agent creates or updates files in `wiki/` using `[[wikilinks]]`.
4. **Compilation**: `khub graph` is run to rebuild the `graph.json` from the new markdown links.
5. **Verification**: `khub lint` ensures no links were broken during synthesis.

---

## 🤖 Agent Protocol

This framework is designed for a **Human-in-the-loop, AI-driven** workflow. The `AGENTS.md` file in the root directory acts as the system prompt for any agent participating in the hub.

### Core Workflow for Agents
1. **Context Discovery**: Read `wiki_hub/topics/<topic>/_index.md` and `graph.json`.
2. **Knowledge Ingestion**: 
    - Save raw data to `raw/YYYY-MM-DD-slug.md`.
    - Extract entities and create/edit `wiki/*.md` pages.
3. **Graph Sync**: Run `khub graph <topic>` after every edit.
4. **Validation**: Run `khub lint <topic>` to catch broken links early.

### Handling Context Overflow
When a topic grows too large for an agent's context window, the agent should:
- Review the `graph.json` to identify the most relevant nodes.
- Only load files related to the specific query or task.
- Propose "Topic Splitting" if the domain has become too broad.

---

## 🛠️ CLI Reference

The `khub` tool is your primary interface for maintaining hub integrity.

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `khub init` | `<name> --hub <path>` | Scaffolds a new topic and updates the registry. |
| `khub graph` | `<name> --hub <path>` | Parses wikilinks in `wiki/` and generates `graph.json`. |
| `khub lint` | `<name> --hub <path>` | Checks for broken `[[links]]` and orphan (unlinked) pages. |

### Example Usage

**Rebuild a graph for the "ai-safety" topic:**
```bash
khub graph ai-safety --hub ./wiki_hub
```

**Check for broken links in the "quantum" topic:**
```bash
khub lint quantum --hub ./wiki_hub
```

---

## 🧪 Testing

The CLI engine is backed by a suite of tests to ensure graph generation and linting remain robust.

### Running Tests
Ensure you are in the `cli/` directory:

```bash
cd cli
pytest
```

### Test Coverage
- **`test_core.py`**: Topic initialization and registry updates.
- **`test_graph.py`**: Wikilink parsing and JSON graph consistency.
- **`test_lint.py`**: Validation logic for broken links and orphans.
- **`test_workflow.py`**: End-to-end ingestion and maintenance flows.

---

## 📜 Philosophy

Karpathy Hub follows the **LLM Wiki Pattern** outlined by Andrej Karpathy. The core tenet is that knowledge should be stored in a way that is **machine-readable (Graph/JSON)** but **human-editable (Markdown)**.

By isolating topics, we provide the LLM with a "bounded context," which drastically improves reasoning quality and reduces hallucinations.

- **Reference**: [Andrej Karpathy's LLM Wiki Post](docs/Karpathy-Philosophy.md)
- **Design Decisions**: See `docs/specs/` for detailed architectural ADRs.

---

## ❓ Troubleshooting

### CLI Command Not Found
**Issue**: `bash: khub: command not found`
**Solution**: Ensure you installed the CLI with `pip install -e ./cli` and that your local bin path is in your `$PATH`.

### Broken Links After Moving Files
**Issue**: `khub lint` reports broken links after renaming a wiki page.
**Solution**: The link target must match the filename (stem) exactly. Update all `[[old-name]]` references to `[[new-name]]` and re-run `khub graph`.

### Corrupted `wikis.json`
**Issue**: Registry file is unreadable.
**Solution**: The CLI handles `JSONDecodeError` by starting fresh, but you can manually fix it or delete it and re-run `khub init` for your existing topics to re-register them.
