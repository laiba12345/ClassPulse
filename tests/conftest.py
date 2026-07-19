import os

# Tests are offline and deterministic; production defaults to GPT-5.6 when a key exists.
os.environ["CLASSPULSE_LLM_MODE"] = "demo"
