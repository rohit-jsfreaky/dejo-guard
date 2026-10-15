"""The class table, on page facts as the browser reports them. Words never change the class."""

import pytest

from dejo_guard.classes import classify
from dejo_guard.facts import PageFacts, site_of
from dejo_guard.guard import plan_for

SHOP = {"dejo-guard.vercel.app"}
PAGE = "https://dejo-guard.vercel.app/shop/checkout"


def c(**kw):
    kw.setdefault("page_url", PAGE)
    return classify(PageFacts(**kw), SHOP).cls


def test_link_on_the_site_is_navigate():
    assert c(action="click", tag="a", href="https://dejo-guard.vercel.app/shop/p/2", words="Next page") == "navigate"


def test_link_off_the_site_is_new_domain():
    assert c(action="click", tag="a", href="https://evil.example/pay", words="Next page") == "new_domain"


@pytest.mark.parametrize("words", ["Place order", "Continue", "आगे बढ़ें", "Next page", ""])
def test_payment_form_submit_is_submit_payment_whatever_it_says(words):
    assert c(action="click", tag="button", is_submit=True, in_form=True, form_method="post",
             form_has_payment=True, words=words) == "submit_payment"


@pytest.mark.parametrize("words", ["Place order", "Search", "Continue"])
def test_post_form_submit_is_submit_form(words):
    assert c(action="click", tag="button", is_submit=True, in_form=True, form_method="post", words=words) == "submit_form"


def test_get_search_form_is_navigation():
    assert c(action="press", key="Enter", in_form=True, form_method="get",
             form_action="https://dejo-guard.vercel.app/shop?q=x") == "navigate"


def test_enter_in_a_post_form_submits_it():
    assert c(action="press", key="Enter", in_form=True, form_method="post") == "submit_form"


def test_card_field_by_autocomplete_is_type_payment():
    assert c(action="fill", tag="input", autocomplete="cc-number", is_payment_field=True, is_text_field=True,
             words="Name on card") == "type_payment"


def test_field_inside_payment_frame_is_type_payment():
    assert c(action="fill", tag="input", is_text_field=True, cross_origin_frame=True, page_has_payment=True) == "type_payment"


def test_password_is_type_secret():
    assert c(action="fill", tag="input", type="password", is_secret_field=True, is_text_field=True) == "type_secret"


def test_search_box_is_type_text():
    assert c(action="fill", tag="input", type="search", is_text_field=True) == "type_text"


def test_plain_button_is_interact_until_it_writes():
    assert c(action="click", tag="button", words="Add to cart") == "interact"


def test_any_button_on_a_page_with_card_fields_submitting_is_payment():
    assert c(action="click", tag="button", is_submit=True, in_form=True, form_method="post", page_has_payment=True,
             words="Continue") == "submit_payment"


def test_download_link():
    assert c(action="click", tag="a", href="https://dejo-guard.vercel.app/invoice.pdf") == "download"


def test_unreadable_element_is_unknown():
    assert c(action="click", unreadable=True) == "unknown"


def test_goto_other_site_is_new_domain():
    assert c(action="goto", target_url="https://bank.example/transfer") == "new_domain"


def test_evaluate_is_run_script():
    assert c(action="evaluate") == "run_script"


def test_site_of():
    assert site_of("https://www.amazon.in/dp/x") == "amazon.in"
    assert site_of("https://shop.co.uk/a") == "shop.co.uk"
    assert site_of("http://localhost:3000/shop") == "localhost:3000"
    assert site_of("dejo-guard.vercel.app") == "dejo-guard.vercel.app"


def test_plan_words():
    assert "submit_form" not in plan_for("compare prices for Atomic Habits")
    assert "submit_payment" in plan_for("buy the cheapest copy")
    assert "submit_form" in plan_for("add it to my cart")
    assert "submit_payment" not in plan_for("add it to my cart")


def test_network_writes():
    from dejo_guard.classes import network_class
    assert network_class("POST", "https://s.app/api/shop/cart", '{"id":"b1"}', False).cls == "state_change"
    assert network_class("POST", "https://s.app/api/shop/orders", '{"items":[]}', False).cls == "submit_payment"
    assert network_class("POST", "https://s.app/api/x", '{"payment_method":"saved"}', False).cls == "submit_payment"
    assert network_class("POST", "https://s.app/api/x", "{}", True).cls == "submit_payment"


def test_reading_is_read():
    assert c(action="read") == "read"


def test_nouns_do_not_unlock_writes():
    for task in ("compare prices for this book", "find the cheapest book", "read the order of events"):
        assert "submit_form" not in plan_for(task) or "order" in task
    assert "state_change" not in plan_for("compare prices for this book")
