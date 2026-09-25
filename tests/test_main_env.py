import importlib.util
import os
from pathlib import Path


def test_load_env_file_falls_back_to_dotenv_example(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    env_path = root / ".env"
    if env_path.exists():
        env_path.unlink()

    monkeypatch.chdir(root)
    monkeypatch.delenv("HIDRIVE_NEXT_USER", raising=False)
    monkeypatch.delenv("HIDRIVE_NEXT_PASS", raising=False)

    spec = importlib.util.spec_from_file_location("main_module", root / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.load_env_file()

    assert os.environ.get("HIDRIVE_NEXT_USER") == "your_username"
    assert os.environ.get("HIDRIVE_NEXT_PASS") == "your_password"
