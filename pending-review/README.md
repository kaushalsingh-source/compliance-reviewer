# pending-review/

Proposed updates to the compliance reference material, written here by the
`compliance-regulation-watcher` skill. Nothing in this folder has been
applied to `references/` — everything here is a **proposal**, not a fact.

## Why this folder exists

This project was burned once by trusting a single unverified source on
compliance content. The watcher is deliberately built so it can never
silently edit `references/*.md` itself. When it finds something that looks
new or amended, it writes a dated note here instead, and tells Kaushal.
Kaushal reviews the note and either applies the edit himself or asks Claude
to apply it in a later session — at which point it must be applied to
**both** mirrors (this repo's `references/` and
`~/.claude/skills/compliance-guardrail-reviewer/references/`) so they stay
in sync as the authoritative pair.

## File naming

`YYYY-MM-DD-<short-slug>.md`, e.g. `2026-09-22-rbi-cobrand-para23-clarification.md`.

## Note format

Each note should cover:

- **What changed** — the specific provision, in plain language.
- **Source(s)** — the primary/official source checked (rbi.org.in,
  meity.gov.in, egazette, etc.) plus at least one independent corroborating
  source, with URLs. If only one source could be found and it isn't the
  official one, the note must say so explicitly and mark confidence as low
  rather than presenting it as confirmed.
- **Affected reference file(s)** — which of `rbi-digital-lending-directions-2025.md`,
  `rbi-cobranding-card-directions-2025.md`, `dpdp-act-2023.md`, or
  `dpdp-rules-2025.md` this touches.
- **Suggested edit** — the actual text/diff to make it easy for Kaushal (or
  a future Claude session) to apply, if approved.
- **Confidence** — High / Medium / Low, same scale as the guardrail-reviewer
  skill uses for its own flags.

## Once applied

When Kaushal approves a note and it's applied to both `references/`
mirrors, move the note file here into an `applied/` subfolder (create it if
needed) with a one-line addendum noting the date it was applied — don't
delete it, so there's a paper trail of what was proposed vs. what shipped.
