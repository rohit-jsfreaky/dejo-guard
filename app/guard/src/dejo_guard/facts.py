"""Page facts: what the DOM says an element IS, read from the live page.

Only structure is read here — tags, types, autocomplete tokens, form method and action,
link targets, which frame the element lives in. The words on a button are collected too,
but only so a human can see them in an approval. They never reach the class table.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlparse

# Runs inside the element's own frame. Returns plain JSON.
#
# `closest(...)` matters: an agent often points at the <span> inside a <button> or the <img>
# inside an <a>. What the click DOES is decided by the control around it.
ELEMENT_FACTS_JS = r"""
(el) => {
  const ctl = el.closest('button, input, select, textarea, a[href], [role="button"], [role="link"], [contenteditable="true"]') || el;
  const tag = ctl.tagName.toLowerCase();
  const type = (ctl.getAttribute('type') || '').toLowerCase();
  const ac = (ctl.getAttribute('autocomplete') || '').toLowerCase();
  const form = ctl.form || ctl.closest('form');
  const anchor = ctl.closest('a[href]');
  const payName = /(^|[^a-z])(card.?num|cc.?num|cardnumber|cvc|cvv|csc|card.?exp|cc.?exp)/i;
  const isPayField = (n) => {
    const a = (n.getAttribute('autocomplete') || '').toLowerCase();
    return /(^|\s)cc-/.test(a) || payName.test(n.getAttribute('name') || '') || payName.test(n.id || '');
  };
  const isSecretField = (n) => {
    const t = (n.getAttribute('type') || '').toLowerCase();
    const a = (n.getAttribute('autocomplete') || '').toLowerCase();
    return t === 'password' || /(current-password|new-password|one-time-code)/.test(a);
  };
  const fields = form ? Array.from(form.elements) : [];
  let isSubmit = false;
  if (form) {
    if (tag === 'button') isSubmit = (type === '' || type === 'submit');
    if (tag === 'input') isSubmit = (type === 'submit' || type === 'image');
  }
  let frameTop = true, crossOriginFrame = false;
  try { frameTop = window.top === window; } catch (e) { frameTop = false; }
  if (!frameTop) {
    const anc = location.ancestorOrigins;
    const topOrigin = anc && anc.length ? anc[anc.length - 1] : null;
    crossOriginFrame = topOrigin !== null && topOrigin !== location.origin;
  }
  const words = (ctl.innerText || ctl.value || ctl.getAttribute('aria-label') || ctl.getAttribute('placeholder') || ctl.getAttribute('name') || '').trim();
  return {
    tag, type, role: (ctl.getAttribute('role') || '').toLowerCase(), autocomplete: ac,
    field_name: ctl.getAttribute('name') || '',
    is_payment_field: (tag === 'input' || tag === 'select') && isPayField(ctl),
    is_secret_field: tag === 'input' && isSecretField(ctl),
    is_text_field: tag === 'textarea' || ctl.isContentEditable || (tag === 'input' && !['submit','button','image','checkbox','radio','file','hidden','reset'].includes(type)),
    is_file_input: tag === 'input' && type === 'file',
    href: anchor ? anchor.href : null,
    link_download: anchor ? anchor.hasAttribute('download') : false,
    is_submit: isSubmit,
    in_form: !!form,
    form_method: form ? (form.getAttribute('method') || 'get').toLowerCase() : null,
    form_action: form ? (form.action || location.href) : null,
    form_has_payment: fields.some(isPayField),
    form_has_secret: fields.some(isSecretField),
    frame_url: location.href,
    in_frame: !frameTop,
    cross_origin_frame: crossOriginFrame,
    words: words.slice(0, 80),
  };
}
"""

# Runs once per frame: does this frame hold card fields?
FRAME_PAYMENT_JS = r"""
() => {
  const payName = /(^|[^a-z])(card.?num|cc.?num|cardnumber|cvc|cvv|csc|card.?exp|cc.?exp)/i;
  return Array.from(document.querySelectorAll('input, select')).some((n) => {
    const a = (n.getAttribute('autocomplete') || '').toLowerCase();
    return /(^|\s)cc-/.test(a) || payName.test(n.getAttribute('name') || '') || payName.test(n.id || '');
  });
}
"""


@dataclass
class PageFacts:
    """Everything the class table is allowed to look at, for one action."""

    action: str
    page_url: str = ""
    target_url: str | None = None  # where a goto / new_tab / link goes
    tag: str = ""
    type: str = ""
    role: str = ""
    autocomplete: str = ""
    field_name: str = ""
    is_payment_field: bool = False
    is_secret_field: bool = False
    is_text_field: bool = False
    is_file_input: bool = False
    href: str | None = None
    link_download: bool = False
    is_submit: bool = False
    in_form: bool = False
    form_method: str | None = None
    form_action: str | None = None
    form_has_payment: bool = False
    form_has_secret: bool = False
    frame_url: str = ""
    in_frame: bool = False
    cross_origin_frame: bool = False
    page_has_payment: bool = False  # card fields anywhere on the page, frames included
    key: str | None = None  # for `press`
    words: str = ""  # shown to the human only
    unreadable: bool = False  # the element could not be read — the table says `unknown`
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v not in (None, "", False, {})}


def from_element(action: str, raw: dict[str, Any] | None, *, page_url: str) -> PageFacts:
    if not raw:
        return PageFacts(action=action, page_url=page_url, unreadable=True)
    known = {k: raw[k] for k in PageFacts.__dataclass_fields__ if k in raw}
    return PageFacts(action=action, page_url=page_url, **known)


# Suffixes where the registrable domain is three labels, not two. Small on purpose: this
# decides "same site or not", and a miss only means a held navigation, never an allowed one.
_TWO_PART_SUFFIXES = {
    "co.in", "co.uk", "org.uk", "ac.uk", "com.au", "net.au", "co.jp", "co.nz", "com.br",
    "com.sg", "co.za", "net.in", "org.in", "gov.in", "ac.in", "edu.in", "firm.in",
    "vercel.app", "github.io", "netlify.app", "pages.dev", "web.app", "herokuapp.com",
}


def site_of(url: str | None) -> str:
    """The registrable domain of a URL ("www.amazon.in" → "amazon.in"). Localhost keeps its port."""
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"//{url}")
    host = (parsed.hostname or "").lower()
    if host in ("localhost", "127.0.0.1") or host.replace(".", "").isdigit():
        return parsed.netloc.lower()
    labels = host.split(".")
    if len(labels) >= 3 and ".".join(labels[-2:]) in _TWO_PART_SUFFIXES:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])
