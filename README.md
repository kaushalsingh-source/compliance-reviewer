# compliance-reviewer-mcp

A small local MCP (Model Context Protocol) server that serves POP's fintech
compliance reference material — the same three regulatory documents used by
Kaushal's `compliance-guardrail-reviewer` Claude Code skill:

- **RBI (Digital Lending) Directions, 2025**
- **RBI co-branded card Directions, 2025** (Commercial Banks – Credit Cards
  and Debit Cards: Issuance and Conduct)
- **DPDP Act, 2023** (Digital Personal Data Protection Act)

## Why this exists

The `compliance-guardrail-reviewer` skill lives at
`~/.claude/skills/compliance-guardrail-reviewer/` and only works inside
Kaushal's own Claude Code setup. This repo copies the same three reference
files into `references/` and serves them over MCP, so **anyone** — Kaushal,
a colleague, or a future teammate — can point their own Claude Code at this
one server and get identical grounding. When a regulation gets amended,
update the markdown here once; everyone who's connected picks it up on
their next tool call. No more copy-drift across personal skill folders.

This server only serves reference text and does simple keyword search over
it — it does not itself judge compliance. (The judgment logic — "never
output a verdict, always say confirm with legal" — lives in the skill
prompt / your own Claude instructions, not in this server.)

## What it exposes

**Tools** (the reliable option — every MCP client supports tool calls):

| Tool | Purpose |
|---|---|
| `list_compliance_topics()` | Lists the 3 reference docs: topic key, filename, one-line description, aliases. |
| `get_compliance_reference(topic: str)` | Returns the full text of one doc. Accepts the canonical key (`digital_lending`, `cobranding`, `dpdp`) or common aliases (`lending`, `cards`, `privacy`, etc). |
| `search_compliance_reference(keyword: str, context_lines: int = 4)` | Searches all three docs for a keyword and returns each match with surrounding context (not just a bare line). |

**Resources** (exposed in addition, for clients that surface MCP resources):

- `compliance://digital-lending`
- `compliance://cobranding`
- `compliance://dpdp`

If your Claude Code client doesn't show resources in its UI, use the tools
above instead — that's why both exist.

## File layout

```
compliance-reviewer-mcp/
├── server.py            # the MCP server (FastMCP, stdio transport)
├── test_client.py        # standalone test client — exercises every tool/resource
├── requirements.txt       # mcp<2,>=1.30.0 (pinned to the FastMCP-style v1.x API)
├── references/
│   ├── rbi-digital-lending-directions-2025.md
│   ├── rbi-cobranding-card-directions-2025.md
│   └── dpdp-act-2023.md
├── .gitignore
└── README.md
```

## Requirements

- **Python 3.10+** (the official `mcp` SDK requires it). Check with
  `python3 --version`.
  - If your only `python3` is older than 3.10 (common on stock macOS,
    which ships 3.9), grab a self-contained build instead of touching your
    system Python — no admin/root needed:
    ```bash
    curl -sL -o /tmp/cpython.tar.gz \
      "https://github.com/astral-sh/python-build-standalone/releases/download/20260901/cpython-3.12.14+20260901-aarch64-apple-darwin-install_only.tar.gz"
    # (use aarch64 for Apple Silicon Macs, x86_64_v2 for Intel Macs)
    mkdir -p ~/.local/share && tar -xzf /tmp/cpython.tar.gz -C ~/.local/share \
      && mv ~/.local/share/python ~/.local/share/python-3.12-standalone
    ```
    Then use `~/.local/share/python-3.12-standalone/bin/python3` in place of
    `python3` in the steps below.

## Running it locally

```bash
cd compliance-reviewer-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run the server directly (it just waits on stdin/stdout for an MCP client —
# this is expected, it's not meant to print anything on its own)
python server.py
```

To actually see it do something without wiring up a client, run the
included test script instead (see "Testing" below).

## Testing

This repo includes `test_client.py`, which spawns `server.py` as a real MCP
stdio subprocess (exactly how Claude Code would), lists tools/resources,
and calls each tool once:

```bash
source .venv/bin/activate
python test_client.py
```

Expect it to print the 3 tools, the 3 resources, sample output from each
tool call (including an alias lookup and a deliberate bad-topic call to
confirm graceful error handling), and finish with `ALL CHECKS PASSED`.

## Adding this to Claude Code

Both Kaushal and a colleague do this **on their own machine**, against
**their own local clone** of this repo. There's no hosting/deployment here —
it's a local stdio MCP server, same as running any other CLI tool.

### Step 1 — get the repo and set it up

```bash
git clone <this-repo-url-or-copy-the-folder> ~/compliance-reviewer-mcp
cd ~/compliance-reviewer-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python test_client.py   # confirm it works before wiring it into Claude Code
```

### Step 2 — register it with Claude Code

**Option A: `claude mcp add` (recommended, one-time, user-wide)**

Run this from inside the `compliance-reviewer-mcp` directory so the
`$PWD`-based paths resolve to your own clone:

```bash
claude mcp add compliance-reviewer -s user -- \
  "$PWD/.venv/bin/python" "$PWD/server.py"
```

- `-s user` registers it globally for you across every Claude Code project
  (not just whatever directory you happen to be in) — appropriate here
  since compliance review isn't tied to one codebase.
- The `--` separates `claude mcp add`'s own flags from the actual command
  to run.
- Verify it registered: `claude mcp list` (should show `compliance-reviewer`
  pointing at your venv's python and `server.py`).
- Remove it later with: `claude mcp remove compliance-reviewer`.

**Option B: manual `.mcp.json` (project-scoped, shareable in a repo)**

If you'd rather check this into a project's `.mcp.json` so it's scoped to
that project and versioned alongside it, add:

```json
{
  "mcpServers": {
    "compliance-reviewer": {
      "command": "/absolute/path/to/compliance-reviewer-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/compliance-reviewer-mcp/server.py"]
    }
  }
}
```

Replace both absolute paths with wherever you actually cloned this repo —
`.mcp.json` does not expand `~` or `$HOME` reliably, so use the literal
absolute path (find it with `pwd` from inside the repo).

### Step 3 — use it

In a Claude Code session, ask something like "what does the DPDP Act say
about children's data" or "check this spec against the co-branded card
directions" — Claude will call `search_compliance_reference` /
`get_compliance_reference` as needed. You can also sanity-check the
connection directly with `/mcp` inside Claude Code, which lists connected
servers and their tools.

## Keeping the reference material current

Edit the three files under `references/`, commit, and `git push` (or hand
the updated folder to whoever needs it). There is no separate build step —
the server reads the files fresh on every tool call, so an update is live
the moment the file changes and the server is running (or on next server
start, if you restart Claude Code's connection to it).
