from pathlib import Path


OPENAPI_USER_MODULE = Path(__file__).with_name("openapi-user-module.yaml")


def user_module_openapi_contract() -> str:
    return OPENAPI_USER_MODULE.read_text(encoding="utf-8")
