import os
from pathlib import Path
from unittest.mock import patch

from app.config import load_env_file


def test_env_file_loads_values_without_overriding_existing_environment(monkeypatch):
    env_file = Path("virtual.env")
    monkeypatch.setenv("EXISTING", "shell-value")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with patch.object(Path, "is_file", return_value=True), patch.object(
        Path,
        "read_text",
        return_value="# comment\nOPENAI_API_KEY=test-key\nEXISTING=file-value\n",
    ):
        load_env_file(env_file)

    assert os.environ["OPENAI_API_KEY"] == "test-key"
    assert os.environ["EXISTING"] == "shell-value"
