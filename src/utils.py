"""Utility functions."""

import pathlib

import tomli


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
