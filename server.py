"""
compliance-reviewer-mcp
========================

MCP server that serves POP's fintech compliance reference material —
RBI Digital Lending Directions 2025, RBI co-branded card Directions 2025,
and the DPDP Act 2023 — as a shared, single-source-of-truth grounding set.

This exists so the reference text lives in ONE place (this repo's
references/ folder) instead of drifting across copies of a personal
Claude Code skill folder. Anyone who runs this server locally (via stdio)
gets the exact same grounding material Kaushal's compliance-guardrail-reviewer
skill uses.

Run directly:
    python server.py

See README.md for how to register this with Claude Code (`claude mcp add`).
"""

from __future__ import annotations

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Reference catalogue
# ---------------------------------------------------------------------------

REFERENCES_DIR = Path(__file__).parent / "references"

# topic key -> (filename, one-line description, list of accepted aliases)
TOPICS: dict[str, dict] = {
    "digital_lending": {
        "filename": "rbi-digital-lending-directions-2025.md",
        "description": (
            "RBI (Digital Lending) Directions, 2025 — LSP due diligence, KFS, "
            "disbursement/repayment flow-of-funds, cooling-off, data minimization "
            "for lending/BRE/onboarding-to-a-loan flows."
        ),
        "aliases": ["lending", "digital lending", "rbi lending", "dl", "loans", "loan"],
    },
    "cobranding": {
        "filename": "rbi-cobranding-card-directions-2025.md",
        "description": (
            "RBI (Commercial Banks – Credit Cards and Debit Cards: Issuance and "
            "Conduct) Directions, 2025 — co-branded card partner data access, "
            "KFS/MITC disclosure, unsolicited issuance, revenue-share, closure mechanics."
        ),
        "aliases": ["cobrand", "co-brand", "co-branding", "cards", "card", "credit card", "rbi cards"],
    },
    "dpdp": {
        "filename": "dpdp-act-2023.md",
        "description": (
            "Digital Personal Data Protection Act, 2023 — consent design, notice, "
            "retention/purge, breach notification, children's data, Data Fiduciary obligations."
        ),
        "aliases": ["dpdp act", "data protection", "privacy", "personal data"],
    },
}


def _resolve_topic(topic: str) -> str | None:
    """Resolve a free-form topic string to a canonical topic key, or None."""
    if not topic:
        return None
    normalized = topic.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in TOPICS:
        return normalized
    for key, meta in TOPICS.items():
        alias_norm = [a.lower().replace("-", "_").replace(" ", "_") for a in meta["aliases"]]
        if normalized in alias_norm:
            return key
    # loose substring match as a last resort
    for key, meta in TOPICS.items():
        haystack = [key] + meta["aliases"]
        for candidate in haystack:
            candidate_norm = candidate.lower().replace("-", "_").replace(" ", "_")
            if normalized in candidate_norm or candidate_norm in normalized:
                return key
    return None


def _read_reference(key: str) -> str:
    path = REFERENCES_DIR / TOPICS[key]["filename"]
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "compliance-reviewer",
    instructions=(
        "Serves the reference material behind POP's compliance-guardrail-reviewer "
        "skill: RBI Digital Lending Directions 2025, RBI co-branded card Directions "
        "2025, and the DPDP Act 2023. Use list_compliance_topics to see what's "
        "available, get_compliance_reference to pull a full reference document, "
        "and search_compliance_reference to find specific clauses by keyword. "
        "This tool only surfaces regulatory text for grounding — it never issues "
        "a compliance verdict."
    ),
)


# --- Tools -------------------------------------------------------------------


@mcp.tool()
def list_compliance_topics() -> list[dict]:
    """List the available compliance reference documents.

    Returns each document's topic key (use this with get_compliance_reference),
    its source filename, and a one-line description of what it covers.
    """
    return [
        {
            "topic": key,
            "filename": meta["filename"],
            "description": meta["description"],
            "aliases": meta["aliases"],
        }
        for key, meta in TOPICS.items()
    ]


@mcp.tool()
def get_compliance_reference(topic: str) -> str:
    """Return the full text of one compliance reference document.

    Args:
        topic: A reasonable name for the document, e.g. "digital_lending",
            "cobranding", "dpdp", or aliases like "lending", "cards", "privacy".
            Use list_compliance_topics to see all valid topics and aliases.

    Returns:
        The full markdown text of the matched reference document, or an
        error message listing valid topics if no match was found.
    """
    key = _resolve_topic(topic)
    if key is None:
        valid = ", ".join(TOPICS.keys())
        return (
            f"No reference document matches topic '{topic}'. "
            f"Valid topics are: {valid}. Call list_compliance_topics() for aliases."
        )
    return _read_reference(key)


@mcp.tool()
def search_compliance_reference(keyword: str, context_lines: int = 4) -> list[dict]:
    """Search all three compliance reference documents for a keyword.

    Args:
        keyword: Term or phrase to search for (case-insensitive). Matches
            against section headings and body text.
        context_lines: How many lines of surrounding context to include
            above and below each match (default 4), since a bare matching
            line is rarely enough to judge relevance.

    Returns:
        A list of matches, each with the source topic/filename, the
        matching line, and a context snippet. Empty list if nothing matched.
    """
    if not keyword or not keyword.strip():
        return []

    pattern = re.compile(re.escape(keyword.strip()), re.IGNORECASE)
    results: list[dict] = []

    for key, meta in TOPICS.items():
        text = _read_reference(key)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if pattern.search(line):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                snippet = "\n".join(lines[start:end])
                results.append(
                    {
                        "topic": key,
                        "filename": meta["filename"],
                        "matched_line": line.strip(),
                        "line_number": i + 1,
                        "context": snippet,
                    }
                )

    return results


# --- Resources ---------------------------------------------------------------
# Exposed in addition to the tools above, since not every MCP client
# surfaces resources the same way — tools are the reliable fallback.


@mcp.resource("compliance://digital-lending")
def digital_lending_resource() -> str:
    """RBI (Digital Lending) Directions, 2025 — full text."""
    return _read_reference("digital_lending")


@mcp.resource("compliance://cobranding")
def cobranding_resource() -> str:
    """RBI co-branded card (Credit/Debit Card Issuance and Conduct) Directions, 2025 — full text."""
    return _read_reference("cobranding")


@mcp.resource("compliance://dpdp")
def dpdp_resource() -> str:
    """Digital Personal Data Protection Act, 2023 — full text."""
    return _read_reference("dpdp")


if __name__ == "__main__":
    mcp.run()
