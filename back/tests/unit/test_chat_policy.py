from ml.train import extract_examples


def test_training_input_rejects_conflicting_labels():
    import pytest
    text = "¿Qué hago? | personal_decision\nQue hago | no_personal"
    with pytest.raises(ValueError, match="Contradictory"):
        extract_examples(text, ["personal_decision", "no_personal", "personal_informativa"])
