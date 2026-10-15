"""guard.yaml widens a task's plan (never the decision), and ignores what it doesn't understand."""

from dejo_guard import userplan


def test_sites_and_words_add_known_classes(tmp_path):
    f = tmp_path / "guard.yaml"
    f.write_text("sites:\n  github.com: [submit_form, nonsense]\nwords:\n  '" + r"\bstar\b" + "': [state_change]\n",
                 encoding="utf-8")
    user = userplan.load(f)
    assert user["sites"] == {"github.com": ["submit_form"]}
    assert userplan.extra_classes("star this repo", {"github.com"}, user) == ("submit_form", "state_change")
    assert userplan.extra_classes("read the readme", {"wikipedia.org"}, user) == ()


def test_missing_or_broken_file_adds_nothing(tmp_path):
    assert userplan.load(tmp_path / "none.yaml") == {"sites": {}, "words": {}}
    bad = tmp_path / "bad.yaml"
    bad.write_text("sites: [unclosed", encoding="utf-8")
    assert userplan.load(bad) == {"sites": {}, "words": {}}


def test_default_file_is_valid_and_empty(tmp_path):
    f = tmp_path / "guard.yaml"
    assert userplan.write_default(f)
    assert userplan.load(f) == {"sites": {}, "words": {}}
    assert not userplan.write_default(f)  # never overwrites the user's file
