#!/usr/bin/env python3
"""Validate first; use --apply to back up, install and reload the cache rule."""
import argparse
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def candidate_config(original, snippet):
    marker = "    # BEGIN Ankia public asset cache\n"
    end_marker = "    # END Ankia public asset cache\n"
    site = "www.tsaitang.com {\n"
    if original.count(site) != 1:
        raise ValueError("Expected exactly one www.tsaitang.com site block")
    block = marker + "".join("    " + line + "\n" for line in snippet.splitlines()) + end_marker
    if marker in original or end_marker in original:
        raise ValueError("Cache block already exists; inspect it before updating")
    return original.replace(site, site + block, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="/etc/caddy/Caddyfile")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = Path(args.config)
    snippet = Path(__file__).with_name("theme-assets.caddy").read_text()
    original = config.read_bytes()
    updated = candidate_config(original.decode(), snippet)
    fd, name = tempfile.mkstemp(prefix=".ankia-cache-", dir=config.parent)
    candidate = Path(name)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(updated)
        subprocess.run(["caddy", "validate", "--config", str(candidate),
                        "--adapter", "caddyfile"], check=True)
        if not args.apply:
            print("Validated candidate; live configuration unchanged")
            return
        if config.read_bytes() != original:
            raise RuntimeError("Caddyfile changed during validation; refusing to overwrite")
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = config.with_name(config.name + ".bak-ankia-cache-" + stamp)
        if backup.exists():
            raise RuntimeError("Backup path already exists")
        shutil.copy2(config, backup)
        stat = config.stat()
        os.chmod(candidate, stat.st_mode & 0o777)
        os.chown(candidate, stat.st_uid, stat.st_gid)
        os.replace(candidate, config)
        try:
            subprocess.run(["systemctl", "reload", "caddy"], check=True)
        except BaseException:
            shutil.copy2(backup, config)
            subprocess.run(["systemctl", "reload", "caddy"], check=True)
            raise
        print("Applied cache rule; backup:", backup)
    finally:
        candidate.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
