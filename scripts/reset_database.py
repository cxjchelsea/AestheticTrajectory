from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", None}


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_database_url(repo_root: Path, explicit_url: str | None) -> str:
    if explicit_url:
        return explicit_url

    load_env_file(repo_root / ".env")
    load_env_file(repo_root / "backend" / ".env")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set. Add it to backend/.env or pass --database-url.")
    return database_url


def confirm_reset(database_name: str | None, assume_yes: bool) -> None:
    if assume_yes:
        return

    expected = f"RESET {database_name or 'database'}"
    entered = input(f'Type "{expected}" to clear all business data: ').strip()
    if entered != expected:
        raise SystemExit("Reset cancelled.")


def assert_supported_database(database_url: str, allow_remote: bool) -> None:
    url = make_url(database_url)
    if not url.drivername.startswith("postgresql"):
        raise SystemExit(f"Only PostgreSQL URLs are supported, got: {url.drivername}")

    if url.host not in LOCAL_HOSTS and not allow_remote:
        safe_url = url.render_as_string(hide_password=True)
        raise SystemExit(
            "Refusing to reset a non-local database without --allow-remote: "
            f"{safe_url}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clear local/test PostgreSQL business data.")
    parser.add_argument(
        "--database-url",
        help="Override DATABASE_URL from backend/.env.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive RESET <database> confirmation.",
    )
    parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="Allow resetting a database whose host is not localhost/127.0.0.1.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    sql_path = repo_root / "scripts" / "reset_database.sql"

    database_url = load_database_url(repo_root, args.database_url)
    assert_supported_database(database_url, args.allow_remote)

    url = make_url(database_url)
    safe_url = url.render_as_string(hide_password=True)
    print(f"Target database: {safe_url}")
    confirm_reset(url.database, args.yes)

    sql = sql_path.read_text(encoding="utf-8")
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text(sql))

    print("Database business data reset complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Reset cancelled.")
