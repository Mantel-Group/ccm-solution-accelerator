import tomllib
from functools import lru_cache
from pathlib import Path

import streamlit as st

_CONFIG_PATH = Path(__file__).parent / "colours.toml"


@lru_cache(maxsize=1)
def _load_config() -> dict:
    with open(_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def get_rag_colours() -> dict[str, str]:
    config = _load_config()
    try:
        is_dark = st.context.theme.type == "dark"
    except AttributeError:
        is_dark = False
    return config["dark" if is_dark else "light"]
