from langchain_intro.graph import lowercase_node, uppercase_node


def test_uppercase_preserves_spaces_punctuation_and_accents() -> None:
    state = {"output": "Olá, mundo!  café"}

    result = uppercase_node(state)

    assert result["output"] == "OLÁ, MUNDO!  CAFÉ"


def test_lowercase_preserves_spaces_punctuation_and_accents() -> None:
    state = {"output": "OLÁ, MUNDO!  CAFÉ"}

    result = lowercase_node(state)

    assert result["output"] == "olá, mundo!  café"

