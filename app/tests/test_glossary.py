from lib.glossary import term_help


def test_term_help_contains_description_and_encoded_google_search():
    help_text = term_help("ゴールデンクロス")

    assert "短期移動平均線" in help_text
    assert "https://www.google.com/search?q=" in help_text
    assert "Googleで詳しく調べる" in help_text


def test_unknown_term_has_no_help():
    assert term_help("未登録の用語") is None
