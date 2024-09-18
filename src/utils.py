"""Utility functions."""

import os
import pathlib

import tomli
from pydantic_settings import BaseSettings


def get_app_version() -> str:
    """Gets the current version specified in the pyproject.toml file."""
    current_dir = pathlib.Path(__file__).resolve().parent
    while current_dir != pathlib.Path("/"):
        toml_file_path = current_dir / "pyproject.toml"
        if toml_file_path.exists():
            with open(toml_file_path, mode="rb") as config:
                toml_file = tomli.load(config)
                version = toml_file["tool"]["poetry"]["version"]
            return version
        current_dir = current_dir.parent

    raise FileNotFoundError(
        "pyproject.toml file not found in any parent directory."
    )


class DBSettings(BaseSettings):
    """
    Application constant settings for the microservice.
    """

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USERNAME", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "bridgeai")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/{POSTGRES_DB}"
    )


settings = DBSettings()
