from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class DatabaseSettings:
    url: str = "postgresql://blocia:blocia@localhost:5432/blocia"


@contextmanager
def transaction():
    yield
