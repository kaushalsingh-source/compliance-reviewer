"""
Tiny standalone test client for server.py.

Spawns server.py as a subprocess over stdio (exactly how a real MCP client
like Claude Code would), lists tools and resources, then calls each of the
three tools once and prints the result. Run with:

    python test_client.py

Exits non-zero if any step fails.
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_PATH = Path(__file__).parent / "server.py"


async def main() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("=" * 70)
            print("TOOLS")
            print("=" * 70)
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"- {t.name}: {t.description.strip().splitlines()[0]}")
            tool_names = {t.name for t in tools.tools}
            expected = {
                "list_compliance_topics",
                "get_compliance_reference",
                "search_compliance_reference",
            }
            assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"

            print()
            print("=" * 70)
            print("RESOURCES")
            print("=" * 70)
            resources = await session.list_resources()
            for r in resources.resources:
                print(f"- {r.uri}  ({r.name})")
            assert len(resources.resources) == 3, f"Expected 3 resources, got {len(resources.resources)}"

            print()
            print("=" * 70)
            print("CALL: list_compliance_topics()")
            print("=" * 70)
            result = await session.call_tool("list_compliance_topics", {})
            for block in result.content:
                print(block.text if hasattr(block, "text") else block)

            print()
            print("=" * 70)
            print("CALL: get_compliance_reference(topic='dpdp')")
            print("=" * 70)
            result = await session.call_tool("get_compliance_reference", {"topic": "dpdp"})
            text = result.content[0].text
            print(text[:400] + f"\n... [truncated, {len(text)} chars total]")
            assert "DPDP" in text or "Data Protection" in text

            print()
            print("=" * 70)
            print("CALL: get_compliance_reference(topic='cobranding') via alias 'cards'")
            print("=" * 70)
            result = await session.call_tool("get_compliance_reference", {"topic": "cards"})
            text = result.content[0].text
            print(text[:400] + f"\n... [truncated, {len(text)} chars total]")
            assert "Credit Card" in text or "Card" in text

            print()
            print("=" * 70)
            print("CALL: search_compliance_reference(keyword='consent')")
            print("=" * 70)
            result = await session.call_tool("search_compliance_reference", {"keyword": "consent"})
            print(result.content[0].text[:1500])

            print()
            print("=" * 70)
            print("CALL: get_compliance_reference(topic='not_a_real_topic')  [expect graceful error]")
            print("=" * 70)
            result = await session.call_tool("get_compliance_reference", {"topic": "not_a_real_topic"})
            print(result.content[0].text)

            print()
            print("=" * 70)
            print("READ RESOURCE: compliance://digital-lending")
            print("=" * 70)
            res_result = await session.read_resource("compliance://digital-lending")
            content = res_result.contents[0]
            res_text = content.text
            print(res_text[:300] + f"\n... [truncated, {len(res_text)} chars total]")

            print()
            print("ALL CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
