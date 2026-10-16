# Dejo limitations found while building Dejo Guard (to improve in Dejo later)

1. **Fixed browser size.** `dejo/browser.py` hard-codes `VIEWPORT = {"width": 1280, "height": 800}` and offers no
   setting to change it. In a headed window narrower than 1280 CSS px (e.g. half of a 1080p screen at 125% scaling)
   the page is cut off on the right instead of re-flowing. Found 17 Oct 2026 while recording the demo video.
   Fix in Dejo: a `DEJO_VIEWPORT=WIDTHxHEIGHT` setting (or `no_viewport` so the page follows the window).
   Dejo Guard works around it with `DEJO_GUARD_VIEWPORT` (sets Dejo's constant before the browser starts).
2. **No way to size or place the headed window.** The window opens wherever Chrome puts it; the demo had to move
   it with Win32 calls. Fix: `DEJO_WINDOW=x,y,w,h` passed as Chrome's `--window-position/--window-size`.
3. **Chrome shows "unsupported command-line flag: --no-sandbox"** in every headed window (Dejo launches with it).
   It looks broken on camera. Fix: drop `--no-sandbox` on Windows/macOS where it is not needed. (Playwright adds it
   unless the launch passes `chromium_sandbox=True`; Chrome then also warns about Dejo's
   `--disable-blink-features` flag unless `--test-type` is set.) Dejo Guard does both in headed mode (`server.py`).
