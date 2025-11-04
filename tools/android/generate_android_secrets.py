#!/usr/bin/env python3
"""Interactive helper to prepare Kodi Android signing secrets.

This script uses an Android release keystore located next to the current
working directory (``android-release.keystore``). If that keystore does not
exist, it will be generated automatically via ``keytool`` using the
credentials you enter.

The script then writes four files that can be copied directly into GitHub
repository secrets:

  * KODI_ANDROID_KEYSTORE_BASE64.txt
  * KODI_ANDROID_STORE_PASSWORD.txt
  * KODI_ANDROID_KEY_ALIAS.txt
  * KODI_ANDROID_KEY_PASSWORD.txt

Each file contains the exact value that should be used when creating the
matching GitHub secret.

The script also generates a combined github_secrets.env file with KEY=VALUE
pairs for convenience.
"""

from __future__ import annotations

import base64
import getpass
from pathlib import Path
import shutil
import subprocess
import sys


def ensure_keytool_available() -> None:
    if shutil.which("keytool") is None:
        print("Error: 'keytool' not found on PATH. Please install a JDK and retry.")
        raise SystemExit(1)


def generate_keystore(keystore_path: Path, store_password: str, key_alias: str, key_password: str) -> None:
    ensure_keytool_available()
    keystore_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "keytool",
        "-genkeypair",
        "-v",
        "-keystore",
        str(keystore_path),
        "-storepass",
        store_password,
        "-alias",
        key_alias,
        "-keypass",
        key_password,
        "-keyalg",
        "RSA",
        "-keysize",
        "2048",
        "-validity",
        "10000",
        "-dname",
        "CN=Kodi,O=Kodi,C=US",
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        print("Failed to generate keystore via keytool. Output:\n")
        sys.stdout.write(exc.stderr.decode("utf-8", errors="ignore"))
        raise SystemExit(exc.returncode)


def prompt_secret(prompt: str, allow_empty: bool = False) -> str:
    """Prompt for a secret value, hiding the input."""
    while True:
        value = getpass.getpass(prompt).strip()
        if value or allow_empty:
            return value
        print("Input cannot be empty. Please try again.\n")


def prompt_alias(prompt: str) -> str:
    while True:
        alias = input(prompt).strip()
        if alias:
            return alias
        print("Alias cannot be empty. Please try again.\n")


def choose_output_directory(default: Path) -> Path:
    print(f"\nWhere should the secret files be written?\n"
          f"Press Enter to use the default: {default}")
    raw = input("Output directory [/default/path]: ").strip()
    if not raw:
        directory = default
    else:
        directory = Path(raw).expanduser().resolve()

    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_secret(directory: Path, name: str, value: str) -> None:
    target = directory / f"{name}.txt"
    target.write_text(value, encoding="utf-8")
    try:
        rel_path = target.relative_to(Path.cwd())
    except ValueError:
        rel_path = target
    print(f"  - Wrote {rel_path}")


def write_env_file(directory: Path, secrets: dict[str, str]) -> None:
    target = directory / "github_secrets.env"
    with target.open("w", encoding="utf-8") as handle:
        for key, value in secrets.items():
            handle.write(f"{key}={value}\n")
    try:
        rel_path = target.relative_to(Path.cwd())
    except ValueError:
        rel_path = target
    print(f"  - Wrote {rel_path}")


def main() -> int:
    print("Kodi Android signing secret generator\n" + "=" * 38)

    keystore_path = Path.cwd() / "android-release.keystore"
    print(f"Using keystore: {keystore_path}")

    store_password = prompt_secret("Enter the keystore password (will be created if missing): ")
    key_alias = prompt_alias("Enter the key alias: ")
    key_password = prompt_secret("Enter the key password: ")

    if not keystore_path.exists():
        print("\nKeystore not found. Generating a new one with keytool...\n")
        generate_keystore(keystore_path, store_password, key_alias, key_password)
    else:
        print("\nFound existing keystore. It will be re-used.\n")

    default_output = Path.cwd() / "android-secrets"
    output_dir = choose_output_directory(default_output)

    keystore_bytes = keystore_path.read_bytes()
    keystore_base64 = base64.b64encode(keystore_bytes).decode("ascii")

    secrets = {
        "KODI_ANDROID_KEYSTORE_BASE64": keystore_base64,
        "KODI_ANDROID_STORE_PASSWORD": store_password,
        "KODI_ANDROID_KEY_ALIAS": key_alias,
        "KODI_ANDROID_KEY_PASSWORD": key_password,
    }

    print("\nWriting secret files:")
    for key, value in secrets.items():
        write_secret(output_dir, key, value)

    write_env_file(output_dir, secrets)

    print("\nDone! Copy the values into GitHub as repository secrets with the same names.")
    print(f"All data saved under: {output_dir}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nAborted by user.")
        raise SystemExit(1)
