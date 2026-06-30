#!/usr/bin/env python3
"""
KAPE triage helper.

Builds and (optionally) executes validated KAPE command lines for collection
and module processing, generates batch _kape.cli files for fleet deployment,
and verifies CopyLog hashes for chain of custody.

KAPE is Windows-only; this helper builds the commands and runs them via
subprocess when executed on Windows with kape.exe available. It also works as
a pure command generator on any platform (--dry-run).

Reference: https://ericzimmerman.github.io/KapeDocs/
"""
import argparse
import csv
import hashlib
import os
import subprocess
import sys
from pathlib import Path


def build_collect_cmd(kape, tsource, target, tdest, vss=False, container=None,
                      tflush=False, module=None, mdest=None, mflush=False):
    """Construct a KAPE target (and optional module) command as an argv list."""
    if not tsource or not target or not tdest:
        raise ValueError("collection requires --tsource, --target and --tdest")
    cmd = [kape, "--tsource", tsource, "--target", target, "--tdest", tdest]
    if tflush:
        cmd.append("--tflush")
    if vss:
        cmd.append("--vss")
    if container:
        # container is a base identifier, NOT a filename
        cmd += ["--vhdx", container]
    if module:
        if not mdest:
            raise ValueError("module processing requires --mdest")
        cmd += ["--module", module, "--mdest", mdest]
        if mflush:
            cmd.append("--mflush")
    return cmd


def build_process_cmd(kape, msource, mdest, module, mflush=False):
    """Construct a KAPE module-only processing command."""
    if not msource or not mdest or not module:
        raise ValueError("processing requires --msource, --mdest and --module")
    cmd = [kape, "--msource", msource, "--mdest", mdest, "--module", module]
    if mflush:
        cmd.append("--mflush")
    return cmd


def write_batch_cli(kape_dir, target, container=True):
    """Write a _kape.cli batch file using %d (kape dir) and %m (machine) tokens."""
    line = f"--tsource C: --target {target} --tdest %d\\Disk\\%m"
    if container:
        line += " --vhdx %m"
    cli_path = Path(kape_dir) / "_kape.cli"
    cli_path.write_text(line + "\n", encoding="utf-8")
    return cli_path


def verify_copylog(copylog_path):
    """Re-hash copied files listed in a KAPE CopyLog CSV and compare SHA-1."""
    results = {"ok": 0, "mismatch": 0, "missing": 0}
    with open(copylog_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        # KAPE CopyLog columns vary; look for dest path + sha1 columns flexibly
        for row in reader:
            dest = row.get("DestinationFile") or row.get("CopiedTo") or row.get("Destination")
            expected = (row.get("SHA1") or row.get("Sha1") or "").lower().strip()
            if not dest or not expected:
                continue
            if not os.path.isfile(dest):
                results["missing"] += 1
                continue
            h = hashlib.sha1()
            with open(dest, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            if h.hexdigest().lower() == expected:
                results["ok"] += 1
            else:
                results["mismatch"] += 1
                print(f"[!] HASH MISMATCH: {dest}", file=sys.stderr)
    return results


def run(cmd, dry_run):
    print("[*] " + " ".join(f'"{c}"' if " " in c else c for c in cmd))
    if dry_run:
        return 0
    try:
        proc = subprocess.run(cmd, check=False)
        return proc.returncode
    except FileNotFoundError:
        print(f"[!] kape executable not found: {cmd[0]}", file=sys.stderr)
        return 127


def main():
    p = argparse.ArgumentParser(description="KAPE triage helper")
    p.add_argument("--kape", default="kape.exe", help="Path to kape.exe")
    p.add_argument("--dry-run", action="store_true", help="Print commands, do not execute")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("collect", help="Collect a target set")
    c.add_argument("--tsource", required=True)
    c.add_argument("--target", required=True)
    c.add_argument("--tdest", required=True)
    c.add_argument("--vss", action="store_true")
    c.add_argument("--container", help="VHDX base identifier")
    c.add_argument("--tflush", action="store_true")
    c.add_argument("--module")
    c.add_argument("--mdest")
    c.add_argument("--mflush", action="store_true")

    pr = sub.add_parser("process", help="Process a collection with modules")
    pr.add_argument("--msource", required=True)
    pr.add_argument("--mdest", required=True)
    pr.add_argument("--module", required=True)
    pr.add_argument("--mflush", action="store_true")

    b = sub.add_parser("batch", help="Write a _kape.cli batch file")
    b.add_argument("--kape-dir", required=True)
    b.add_argument("--target", default="KapeTriage")
    b.add_argument("--no-container", action="store_true")

    v = sub.add_parser("verify", help="Verify CopyLog SHA-1 hashes")
    v.add_argument("--copylog", required=True)

    args = p.parse_args()
    try:
        if args.cmd == "collect":
            cmd = build_collect_cmd(args.kape, args.tsource, args.target, args.tdest,
                                    vss=args.vss, container=args.container,
                                    tflush=args.tflush, module=args.module,
                                    mdest=args.mdest, mflush=args.mflush)
            return run(cmd, args.dry_run)
        if args.cmd == "process":
            cmd = build_process_cmd(args.kape, args.msource, args.mdest,
                                    args.module, mflush=args.mflush)
            return run(cmd, args.dry_run)
        if args.cmd == "batch":
            path = write_batch_cli(args.kape_dir, args.target,
                                   container=not args.no_container)
            print(f"[+] Wrote {path}")
            return 0
        if args.cmd == "verify":
            res = verify_copylog(args.copylog)
            print(f"[+] verified ok={res['ok']} mismatch={res['mismatch']} missing={res['missing']}")
            return 1 if res["mismatch"] else 0
    except ValueError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
