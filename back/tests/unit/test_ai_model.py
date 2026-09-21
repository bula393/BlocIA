import pytest

from app.domain.user.ai_model import AIModel


def test_model_belongs_to_provider():
    AIModel("model", "openai", "Model").validate()
    with pytest.raises(ValueError):
        AIModel("model", "", "Model").validate()
