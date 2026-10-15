# hackathon.md — rules and submission checklist (ArmorIQ Flow State)

Sources: armoriq.ai/hackathons/flow-state · luma.com/tttqkw24 · hackbriven.com/event/flow-state · Discord kickoff text
pasted by Rohit 10 Oct (copied in `hackathon_ideas/contexts/armoriq-flow-state.md`). Re-checked 15 Oct night. If this file
and the live pages disagree, the live pages win.

## Clock (IST)
| | |
|---|---|
| Build week | Oct 10, 10:00 AM → **Sat Oct 17, 11:30 PM IST** (Luma; HackBriven shows 11:59 PM) |
| **Submit by** | **Sat Oct 17, 6:00 PM IST** (prepare the submission page by 4 PM) |
| Results | Oct 21 8 PM (HackBriven) / Oct 22 (armoriq.ai) |

## Rules (verbatim essentials, Discord kickoff)
1. "All projects must integrate ArmorIQ. Projects without functional ArmorIQ integration are not eligible."
2. "Projects using ElevenLabs must also integrate ArmorIQ." (We don't use ElevenLabs; no public ElevenLabs prize found.)
3. Any model, framework, language or service.
4. **"Every project must use at least one MCP server."**
5. "Core development must take place during the official hackathon window. Existing libraries, frameworks, and starter
   templates are allowed."
6. "AI coding assistants and open-source dependencies are allowed. **Significant pre-existing code must be disclosed.**"
   → Dejo is disclosed as a dependency.
7. "Sensitive operations must use sandbox or test environments. **No real customer data or production payment systems.**"
8. "Security demos must use **actual ArmorIQ enforcement**, not simulated or hardcoded results."
9. Don't attack ArmorIQ infrastructure, other participants or third-party systems.
10. Misrepresenting integrations = DQ.
- "All projects must demonstrate intent and policy enforcement through platform.armoriq.ai. API keys must be generated
  through the platform, and **all agents and MCPs must be onboarded to the ArmorIQ platform**."
- Must have: an AI agent · at least one MCP server · ArmorIQ showing **one action allowed and one blocked**, real, "not a
  fake or hardcoded demo".

## What to submit
- **GitHub repo** with code, README and setup instructions
- **Demo video, max 90 seconds**
- **Short description:** what you built, how the agent works, how ArmorIQ is used, other tools used
- **Proof of ArmorIQ:** screenshot, dashboard trace, or live demo showing it blocking an action
- HackBriven extra (judging FAQ, exact): "There will be no live presentation or pitching round… Your final submission must
  include: - PPT / project deck - Demo video - GitHub repository URL - **Live project URL**. Make sure your submission clearly
  demonstrates what you built, how it works, how MCP is being used, and how ArmorIQ is integrated."

## Prizes and judges
$1,000 cash grand prize (ArmorIQ); "Partner awards are announced as partners confirm"; winner may be interviewed for the
Developer Products team. Judges: ArmorIQ team (Fuzail Kazi, Isha Parekh, Aniket Vishwakarma, Amit Dubey; organisers on
HackBriven: Fuzail, Isha, Ash). Criteria not published.

## Ship checklist
- [ ] Repo public, README in kit order, Dejo disclosed + AI disclosure on the first screen
- [ ] Agent `dejo-guard-agent` + MCP `sandbox-shop` (public HTTPS) onboarded on platform.armoriq.ai; policy active
- [ ] Live URL: landing + /judges + live decision feed + sandbox shop
- [ ] One real ALLOW, one real BLOCK, one real HOLD → approval, with ArmorIQ trace ids + dashboard screenshots in `evidence/`
- [ ] Video ≤ 90 s (YouTube, public)
- [ ] Deck (PPT/PDF) for HackBriven
- [ ] Submitted on HackBriven (and Luma/Discord if asked) by 6 PM IST
