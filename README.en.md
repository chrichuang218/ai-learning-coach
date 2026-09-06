# AI Learning Coach

**Learn TypeScript and Agent development through real source code, with a coach that remembers where you got stuck.**

[简体中文](README.md) · [First session](examples/first-session/README.md) · [Installation](docs/install.md)

Built first for developers who already know Java or another backend language. The coach reads your project and learning history, chooses one useful action, helps you predict and debug behavior, and records what you actually demonstrated.

It distinguishes running a supplied test from independently designing one. On your next visit, it checks the current source and resumes from your evidence and unresolved boundary.

## Install

```bash
codex plugin marketplace add chrichuang218/ai-learning-coach
codex plugin add ai-learning-coach@ai-learning-coach
```

Start a new Codex session, then say: “Use learning-coach to help me learn TypeScript through a real Agent project. I already know Java. Coach me in English.” The default language is Chinese; an explicit language request can override it.

For the local MCP prototype, install Python 3.10+ and `mcp==1.27.0`. Plain Markdown coaching remains usable through file tools. See [installation boundaries](docs/install.md).

## Try one real problem

The [cache-invalidation first session](examples/first-session/README.md) pins a public mini-claude commit and one deterministic test. Predict what a second discovery call returns after adding a file, run the real code, explain the difference, and keep one next checkpoint. Budget about 15 minutes for learning, plus initial setup.

The source test needs no provider API key; using the coach itself still needs a suitable account. Windows / Node 24 installation and Green → mutation Red → restored Green have been [verified](docs/validation/first-session.md). This is engineering verification, not a claim of measured learner outcomes.

## A portable learning record

Learning Lab is your optional Markdown workspace, not another service. Mission, evidence, assistance level, boundaries and a next action remain local. [Read-only tools](docs/learning-lab.md) can check drift, produce a progress page, and export a selected result for manual review and sharing.

Two skills are included: learning-coach for daily learning, focus-coach for competing goals and strategic choices. Broader domains remain supported by the coaching method; the most developed examples currently concern source-code learning.

[Report your first experience](https://github.com/chrichuang218/ai-learning-coach/issues/new?template=first_experience.yml) · [Contribute](CONTRIBUTING.md) · [MIT](LICENSE)
