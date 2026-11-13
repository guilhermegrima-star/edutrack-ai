from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_protects_streamlit_secret_files():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".streamlit/.env" in gitignore
    assert ".streamlit/secrets.toml" in gitignore


def test_get_setting_prefers_streamlit_secrets():
    sys.path.insert(0, str(ROOT))
    import utils.config as config

    fake_streamlit = types.SimpleNamespace(
        secrets={
            "XANO_AUTH_BASE_URL": "https://secrets.example/api:auth",
            "EDUTRACK_BASE_URL": "https://secrets.example/api:main",
            "EDUTRACK_TASKS_PATH": "task",
        }
    )
    old_env_file = config._get_from_env_file
    old_environ = config.os.environ.copy()
    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "streamlit":
            return fake_streamlit
        return original_import(name, *args, **kwargs)

    try:
        config._get_from_env_file = lambda _key: "env-fallback"
        config.os.environ = {"XANO_AUTH_BASE_URL": "https://env.example/api:auth"}
        import builtins
        builtins.__import__ = fake_import

        assert config.get_setting("XANO_AUTH_BASE_URL") == "https://secrets.example/api:auth"
        assert config.get_setting("EDUTRACK_TASKS_PATH") == "task"
    finally:
        config._get_from_env_file = old_env_file
        config.os.environ = old_environ
        import builtins
        builtins.__import__ = original_import


if __name__ == "__main__":
    test_gitignore_protects_streamlit_secret_files()
    test_get_setting_prefers_streamlit_secrets()
    print("verified: streamlit secret priority and gitignore protection")
