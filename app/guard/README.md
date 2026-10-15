# dejo-guard

**Your browser agent clicks; ArmorIQ decides what the click means.**

Dejo Guard is [Dejo](https://pypi.org/project/dejo-mcp/)'s MCP server (a real browser with a memory, for Claude Code,
Codex, Cursor and any MCP agent) with [ArmorIQ](https://armoriq.ai) in front of every page action. Before each click,
keystroke or replayed step it reads what the action *is* from the page — a link, a form submit, a card field, a
password box, another site — and sends that as a named step to ArmorIQ, whose policy allows it, blocks it, or holds it
until you approve. Writes a page sends on its own are paused until ArmorIQ decides them too.

```bash
pip install dejo-guard
playwright install chromium
armoriq login
dejo-guard init
claude mcp add dejo-guard -- dejo-guard
```

Commands: `dejo-guard` (MCP server, stdio) · `init` · `policy` (print the ArmorIQ policy) · `plan "<task>"` ·
`feed` · `share` (a live web page of your decisions) · `eval` · `serve --http PORT`.

Docs, the attack lab and the live feed: https://dejo-guard.vercel.app · Source: https://github.com/rohit-jsfreaky/dejo-guard

Built for ArmorIQ Flow State (Oct 2026). Dejo (MIT) predates it and is used as a library; everything in this
package is new. MIT licensed.
