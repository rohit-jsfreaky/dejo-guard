# Demo folder for recording Dejo Guard

Open Claude Code here. It has one MCP server: dejo-guard (Dejo's browser with ArmorIQ in front of every action).
Use the browser only through dejo-guard tools. Call guard_task first for every new task, in the user's own words.
If a reply says HELD, tell the user what is waiting and wait for them to approve it in ArmorIQ, then call guard_wait.
If a reply says BLOCKED, stop and explain. Never try another way round.
