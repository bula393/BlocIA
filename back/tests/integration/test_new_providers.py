from app.domain.user.ai_provider import AIProvider
from app.infrastructure.database import Database
from app.infrastructure.user.sqlite_repositories import ProviderRepository


def test_existing_database_adds_groq_and_openrouter_without_overwriting_provider(tmp_path):
    path = tmp_path / "old.sqlite3"
    database = Database(path)
    providers = ProviderRepository(database)
    providers.save(AIProvider("openai", "OpenAI personalizado"))
    database.execute("DELETE FROM providers WHERE provider_id IN ('groq', 'openrouter')")

    reopened = Database(path)
    providers = ProviderRepository(reopened)

    assert providers.get("openai").name == "OpenAI personalizado"
    assert providers.get("groq").name == "Groq"
    assert providers.get("openrouter").name == "OpenRouter"
    assert reopened.health()["ok"]
