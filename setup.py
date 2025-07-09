from setuptools import setup

setup(
    name="notlonely_providers",
    version="0.1",
    packages=["providers"],
    entry_points={
        "notlonely_providers": [
            "openai = providers.openai:OpenAIProvider",
            "ollama = providers.ollama:OllamaProvider",
        ]
    },
) 