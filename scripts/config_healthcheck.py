#!/usr/bin/env python3
"""Simple diagnostic helper for verifying bot configuration.

Run this script after exporting your environment variables (or by pointing it
at an ``.env`` file with ``KEY=VALUE`` lines) to confirm the core configuration
values can be loaded.  The helper re-imports ``info`` just like the bot would
and prints a short report so you can double check channel IDs, booleans and
other derived values.  Optionally it can trigger the unit test suite to ensure
the configuration helpers behave as expected.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path
from typing import Dict

REQUIRED_ENV_VARS = ("API_ID", "API_HASH", "BOT_TOKEN")


def parse_env_file(path: Path) -> Dict[str, str]:
    """Parse a very small ``KEY=VALUE`` style ``.env`` file.

    ``dotenv`` is not part of the runtime dependencies, so we provide a tiny
    parser that understands the subset of syntax used by the project.  Lines
    starting with ``#`` are ignored.  Values wrapped in single or double quotes
    have the surrounding quotes stripped.
    """

    env: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                print(
                    f"Skipping line {line_number} in {path}: does not look like KEY=VALUE",
                    file=sys.stderr,
                )
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            env[key] = value
    return env


def ensure_environment(env_path: Path | None) -> None:
    """Load environment variables and report missing required keys."""

    if env_path:
        env_values = parse_env_file(env_path)
        os.environ.update(env_values)

    missing = [key for key in REQUIRED_ENV_VARS if not os.environ.get(key)]
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(
            "The following required environment variables are missing: "
            f"{missing_list}.\n"
            "Export them in your shell or supply an .env file via --env-file."
        )


def load_info_module():
    """Import ``info`` and surface helpful errors if it fails."""

    try:
        return importlib.import_module("info")
    except KeyError as exc:
        raise SystemExit(
            "Importing info.py failed because an expected environment variable is "
            f"missing: {exc!s}.\nEnsure you have provided every required value."
        ) from exc
    except Exception as exc:  # pragma: no cover - diagnostic output only
        raise SystemExit(
            "Importing info.py failed with an unexpected error:\n"
            f"{exc}\n"
            "Double check your environment configuration and try again."
        ) from exc


def render_bool(value: bool) -> str:
    return "ON" if value else "OFF"


def print_report(info_module) -> None:
    """Emit a human readable summary of the derived configuration."""

    print("Configuration summary\n======================")
    print(f"API_ID            : {info_module.API_ID}")
    print(f"Cache time (secs) : {info_module.CACHE_TIME}")
    print(f"Admins            : {info_module.ADMINS or 'None'}")
    print(f"Channels          : {info_module.CHANNELS or 'None'}")
    print(f"Auth channel      : {info_module.AUTH_CHANNEL or 'None'}")
    print(f"Redirect behaviour: {info_module.redirected_env(info_module.REDIRECT_TO)}")
    print(f"Caption filtering : {render_bool(info_module.USE_CAPTION_FILTER)}")
    print(f"Single button UI  : {render_bool(info_module.SINGLE_BUTTON)}")
    print(f"Spell check reply : {render_bool(info_module.SPELL_CHECK_REPLY)}")
    print(f"Protect content   : {render_bool(info_module.PROTECT_CONTENT)}")

    if info_module.CUSTOM_FILE_CAPTION:
        preview = info_module.CUSTOM_FILE_CAPTION.replace("\n", "\\n")
        if len(preview) > 80:
            preview = preview[:77] + "..."
        print(f"Custom caption    : {preview}")
    else:
        print("Custom caption    : (not set)")


def run_tests() -> bool:
    """Execute the unittest suite and return ``True`` when successful."""

    from unittest import TextTestRunner, TestLoader

    loader = TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    result = TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that the bot configuration can be loaded and optionally run "
            "the unit tests for extra confidence."
        )
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to a .env file containing KEY=VALUE pairs to load before testing.",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run the project\'s unittest suite after loading the configuration.",
    )
    args = parser.parse_args(argv)

    ensure_environment(args.env_file)
    info_module = load_info_module()
    print_report(info_module)

    if args.run_tests:
        print("\nRunning unit tests...\n")
        if not run_tests():
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
