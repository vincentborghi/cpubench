# Example:
#   uv run scripts/verify_data.py --verbose
#   uv run scripts/verify_data.py --debug

import argparse
import json
import re
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Verify cpubench dataset integrity and syntax.",
        epilog="Examples:\n  uv run scripts/verify_data.py --verbose\n  uv run scripts/verify_data.py --debug\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--verbose", action="store_true", help="Print detailed validation logs")
    parser.add_argument("--debug", action="store_true", help="Enable debug diagnostics")
    return parser.parse_args()


def verify_html(verbose: bool, debug: bool):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    if verbose or debug:
        print("[INFO] index.html loaded successfully, size:", len(content))

    # 1. Check cpuData extraction
    match = re.search(r"const cpuData = \[(.*?)\];", content, re.DOTALL)
    if not match:
        print("[ERROR] cpuData array not found in index.html", file=sys.stderr)
        sys.exit(1)

    raw_items = match.group(1).strip()
    # Find all CPU names
    cpu_names = re.findall(r'name:\s*"([^"]+)"', raw_items)
    if verbose or debug:
        print(f"[INFO] Found {len(cpu_names)} CPUs in dataset.")

    # Check for Snapdragon
    snapdragon_found = any("Snapdragon" in n for n in cpu_names)
    if snapdragon_found:
        print("[PASS] Snapdragon CPU found in dataset.")
    else:
        print("[FAIL] Snapdragon CPU NOT found in dataset!", file=sys.stderr)
        sys.exit(1)

    # 2. Check PassMark sorting
    passmarks = [int(p) for p in re.findall(r"passmark:\s*(\d+)", raw_items)]
    is_sorted = all(passmarks[i] <= passmarks[i + 1] for i in range(len(passmarks) - 1))
    if is_sorted:
        print(f"[PASS] cpuData is correctly sorted by PassMark ({len(passmarks)} entries).")
    else:
        print("[FAIL] cpuData is NOT properly sorted by PassMark!", file=sys.stderr)
        sys.exit(1)

    # 3. Check for ARM filter button
    if 'id="btnSelArm"' in content:
        print("[PASS] btnSelArm element found in HTML.")
    else:
        print("[FAIL] btnSelArm not found in HTML!", file=sys.stderr)
        sys.exit(1)

    # 4. Check for bestMatch bug fix
    if "setCompareCpu(bestMatch.name)" in content and "const bestMatch =" not in content:
        print("[FAIL] bestMatch reference without declaration found!", file=sys.stderr)
        sys.exit(1)
    else:
        print("[PASS] bestMatch reference is properly declared.")

    print("\n[ALL CHECKS PASSED] Dataset and controls are consistent.")


def main():
    args = parse_arguments()
    if args.debug:
        print("[DEBUG] Running validation in debug mode.")
    verify_html(verbose=args.verbose, debug=args.debug)


if __name__ == "__main__":
    main()
