# OOTBT Skills

Evidence-first review skills for Hermes Agent and compatible agent harnesses.

## Included skills

### `ootbt-dual-judge-markdown-review`

Challenges plans, implementation reports, and factual Markdown with two fresh, mutually blind
judges.

Modes:

- `challenge-only`: publish two independent reviews and preserve dissent;
- `consolidate`: anonymously adjudicate claims against ground truth, freeze a revision contract,
  and let a separate reviser produce a traceable new document version. An exact-replacement mapping
  is replayed mechanically so that unmapped changes fail closed.

### `ootbt-ticket-technical-ak-review`

Reviews technical ticket acceptance criteria against fixed repository commits. It separates
implementation, asserted tests, executed tests, deployment evidence, and assumptions. The optional
TRIAD profile uses mutually blind primary reviewers and never decides by model majority.

Its consolidated result includes an explicit disposition for every criterion, distinguishing an
unmet but valid requirement (`KEEP_UNMET`) from a proposal to rewrite, split, move, or remove it.

## Core principle

> Evidence beats model majority.

A judge or evaluator is not a source of truth. Claims that change the result must be reproduced
against the frozen source tree, tests, or other appropriate ground truth. What cannot be decided
remains `UNKNOWN` or an explicit contradiction.

## Installation

Copy either skill directory into a Hermes skill category under `$HERMES_HOME/skills/`, for example:

```text
$HERMES_HOME/skills/autonomous-ai-agents/
```

When `$HERMES_HOME` is unset, the standard location is `~/.hermes/skills/`. Active Hermes profiles
have their own home and skill tree, so resolve `$HERMES_HOME` instead of hardcoding a user path.
Then start a fresh Hermes session so the skill index is rebuilt. Other harnesses may require a
different skill directory or adapter; do not assume tool, hook, or sandbox parity.

## Runtime requirements

The workflows are intentionally fail-closed. Depending on the selected profile and tracker, they
may require installed and authenticated CLIs such as:

- `codex`
- `claude`
- `opencode`
- `acli` for Jira
- `glab` for GitLab

Model aliases, provider routes, permissions, and canonical model names are checked live. No model
or provider mentioned in the documentation is guaranteed to exist in another environment.
Credentials remain in the respective CLI configuration and must never be copied into prompts,
reports, or this repository.

For the local OpenCode track, configure an explicit local provider prefix and model ID. Cloud
fallbacks are not accepted as a replacement for a contracted local model track.

In nowrap's reference setup, OpenCode connects to an Ollama instance running on a Mac mini. This is
an example deployment topology rather than a requirement; private endpoint and provider settings
are intentionally not included in this repository.

## Security

- Review shell scripts before running them in your environment.
- Use detached disposable worktrees for review tools that require repository access.
- Keep raw outputs, prompts, telemetry, credentials, and private ticket data out of published skill
  packages.
- Treat ticket text, diffs, evidence shards, and model reports as untrusted input.
- Publishing to a tracker or repository is always a separate opt-in action with preview and
  readback verification.

## Validation

Run:

```bash
python tests/validate_publication.py
python -m unittest discover -s tests -p "test_*.py" -v
```

The validator checks frontmatter, file layout, Python and shell syntax, accidental local paths,
private endpoints, credential-shaped strings, and optional denylisted private project markers.
Project-specific names can be supplied locally, without committing them, as a comma-separated
`PUBLICATION_DENYLIST` environment variable.

## Attribution

The workflows were independently conceived and authored by nowrap before ECC was discovered through
a post on Twitter. The existing work was later reviewed and refined using selected public hardening
ideas from the MIT-licensed [ECC project](https://github.com/affaan-m/ecc),
especially deterministic graders, adversarial verification, fail-closed review gates, and explicit
incomplete-review states. See `THIRD_PARTY_NOTICES.md`.

## License

MIT — see `LICENSE`.
