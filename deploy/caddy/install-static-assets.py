#!/usr/bin/env python3
"""Validate an immutable asset release; --apply installs it and reloads Caddy."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--config", default="/etc/caddy/Caddyfile")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    manifest = json.loads((repo / "deploy/static-assets.json").read_text())
    assets = repo / "assets/ankia"
    destination = Path("/var/www/ankia-assets")
    for name, expected in manifest["files"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Invalid manifest path")
        if hashlib.sha256((assets / path).read_bytes()).hexdigest() != expected:
            raise ValueError("Source checksum mismatch: " + name)
        target = destination / path
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError("Refusing to replace immutable asset: " + name)

    config = Path(args.config)
    original = config.read_bytes()
    text = original.decode()
    site = "www.tsaitang.com {\n"
    rewrite = "not path /share*"
    if text.count(site) != 1 or text.count(rewrite) != 1:
        raise ValueError("Unexpected site/rewrite configuration")
    marker = "    # BEGIN Ankia immutable static assets\n"
    if marker in text:
        raise ValueError("Static route already exists; review before updating")
    snippet = Path(__file__).with_name("static-assets.caddy").read_text()
    block = marker + "".join("    " + line + "\n" for line in snippet.splitlines())
    block += "    # END Ankia immutable static assets\n"
    text = text.replace(site, site + block, 1)
    text = text.replace(rewrite, rewrite + " /assets/ankia/*", 1)
    fd, name = tempfile.mkstemp(prefix=".ankia-static-", dir=config.parent)
    candidate = Path(name)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(text)
        subprocess.run(["caddy", "validate", "--config", str(candidate),
                        "--adapter", "caddyfile"], check=True)
        if not args.apply:
            print("Assets and Caddy candidate validated; live configuration unchanged")
            return
        if config.read_bytes() != original:
            raise ValueError("Caddyfile changed during validation")
        destination.mkdir(parents=True, exist_ok=True)
        os.chmod(destination, 0o755)
        for name in manifest["files"]:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            os.chmod(target.parent, 0o755)
            shutil.copyfile(assets / name, target)
            os.chmod(target, 0o644)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup = config.with_name(config.name + ".bak-ankia-static-" + stamp)
        if backup.exists():
            raise ValueError("Backup already exists")
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
        print("Static assets installed; backup:", backup)
    finally:
        candidate.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
