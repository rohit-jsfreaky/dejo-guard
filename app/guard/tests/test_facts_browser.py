"""The page-facts reader on real HTML, in a real (headless) browser: facts JS → class. Words never decide.

Skipped when no Chromium is installed (`playwright install chromium`). CI installs it.
"""

from __future__ import annotations

import pytest

from dejo_guard.classes import classify
from dejo_guard.facts import ELEMENT_FACTS_JS, from_element
from dejo_guard.guard import Guard

sync_api = pytest.importorskip("playwright.sync_api")
SITE = "https://shop.test"
PAGE = SITE + "/checkout"

CHECKOUT = """<form method="post" action="/api/orders">
  <label>{name_label}<input name="name" autocomplete="name"></label>
  <label>{card_label}<input name="cardnumber" autocomplete="cc-number"></label>
  <button type="submit" id="go">{button}</button>
</form>"""


@pytest.fixture(scope="module")
def page():
    with sync_api.sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as problem:  # noqa: BLE001
            pytest.skip(f"no Chromium: {problem}")
        ctx = browser.new_context()
        pg = ctx.new_page()
        pg.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body="<html><body></body></html>"))
        pg.goto(PAGE)
        yield pg
        browser.close()


def cls_of(page, html: str, selector: str, action: str = "click") -> str:
    page.set_content(html)
    raw = page.locator(selector).first.evaluate(ELEMENT_FACTS_JS)
    facts = from_element(action, raw, page_url=PAGE)
    facts.page_has_payment = Guard.page_has_payment(page)
    return classify(facts, {"shop.test"}).cls


@pytest.mark.parametrize(("button", "name_label", "card_label"), [
    ("Place order", "Name", "Card number"),
    ("Continue", "Name", "Card number"),
    ("ऑर्डर करें", "नाम", "कार्ड नंबर"),
    ("Next page →", "", ""),
])
def test_submit_of_a_card_form_is_submit_payment_whatever_it_says(page, button, name_label, card_label):
    html = CHECKOUT.format(button=button, name_label=name_label, card_label=card_label)
    assert cls_of(page, html, "#go") == "submit_payment"


def test_span_inside_the_pay_button_is_still_the_pay_button(page):
    html = CHECKOUT.format(button="<span id='inner'>Continue</span>", name_label="", card_label="")
    assert cls_of(page, html, "#inner") == "submit_payment"


def test_card_field_is_type_payment(page):
    html = CHECKOUT.format(button="Pay", name_label="", card_label="")
    assert cls_of(page, html, "input[name=cardnumber]", "fill") == "type_payment"


def test_name_field_on_checkout_is_plain_text(page):
    html = CHECKOUT.format(button="Pay", name_label="", card_label="")
    assert cls_of(page, html, "input[name=name]", "fill") == "type_text"


def test_password_box_is_type_secret(page):
    html = "<form method='post'><input type='password' name='pw' autocomplete='current-password'></form>"
    assert cls_of(page, html, "input[name=pw]", "fill") == "type_secret"


def test_post_form_without_cards_is_submit_form(page):
    html = "<form method='post' action='/subscribe'><input name='email'><button>Sign up</button></form>"
    assert cls_of(page, html, "button") == "submit_form"


def test_get_search_form_is_navigation(page):
    html = "<form method='get' action='/search'><input name='q' type='search'><button>Search</button></form>"
    assert cls_of(page, html, "button") == "navigate"


def test_link_on_the_same_site_is_navigate(page):
    assert cls_of(page, f"<a href='{SITE}/books/2'>Next page</a>", "a") == "navigate"


def test_link_to_another_site_is_new_domain(page):
    assert cls_of(page, "<a href='https://elsewhere.example/pay'>Next page</a>", "a") == "new_domain"


def test_plain_js_button_is_interact(page):
    assert cls_of(page, "<button type='button' onclick='1'>Add to cart</button>", "button") == "interact"


def test_card_box_inside_a_sandboxed_frame_is_type_payment(page):
    frame_doc = "<input name='cardnumber' autocomplete='cc-number'>"
    page.set_content(f"<iframe title='Card' sandbox='allow-scripts' srcdoc=\"{frame_doc}\"></iframe>")
    target = page.frame_locator("iframe[title=Card]").locator("input")
    raw = target.evaluate(ELEMENT_FACTS_JS)
    facts = from_element("fill", raw, page_url=PAGE)
    facts.page_has_payment = Guard.page_has_payment(page)
    assert raw["in_frame"] and raw["cross_origin_frame"]
    assert classify(facts, {"shop.test"}).cls == "type_payment"
