from functools import lru_cache
from pathlib import Path
import re
from typing import Literal

from pydantic import BaseModel, Field, model_validator
import yaml

ROOT = Path(__file__).resolve().parents[3]
Label = Literal["no_personal", "personal_informativa", "personal_decision"]


class ClassifierSettings(BaseModel):
    embedding_model: str
    embedding_prefix_query: str
    labels: list[Label]
    primary_grouping: dict[Label, str]
    confidence_threshold: float = Field(ge=0, le=1)
    review_threshold: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def thresholds(self):
        if self.review_threshold >= self.confidence_threshold:
            raise ValueError("review_threshold must be lower than confidence_threshold")
        if set(self.labels) != {"no_personal", "personal_informativa", "personal_decision"}:
            raise ValueError("All three classifier labels are required")
        return self


class ChatSettings(BaseModel):
    max_input_characters: int = Field(ge=10, le=12000)
    cpu_threads: int = Field(ge=1, le=16)
    sensitive_patterns: list[str]

    @model_validator(mode="after")
    def patterns(self):
        for pattern in self.sensitive_patterns:
            re.compile(pattern)
        return self


@lru_cache(maxsize=8)
def _load(classifier_mtime, chat_mtime):
    return (
        ClassifierSettings.model_validate(yaml.safe_load((ROOT / "config/classifier.yaml").read_text(encoding="utf-8"))),
        ChatSettings.model_validate(yaml.safe_load((ROOT / "config/chat.yaml").read_text(encoding="utf-8"))),
    )


def settings():
    return _load((ROOT / "config/classifier.yaml").stat().st_mtime_ns, (ROOT / "config/chat.yaml").stat().st_mtime_ns)
