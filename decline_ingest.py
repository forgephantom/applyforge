#!/usr/bin/env python3
"""Decline ingestion: write Gmail decline emails back into the tracker and
the rejection cool-down list, in the same step.

The 2026-11-19 ATS/decline review found the feedback loop broken: the
cool-down file was missing at least 21 companies' declines that exist in
Gmail, and 50 of 56 known declines still showed Status "Submitted" in the
tracker. Without this step, every decline-rate number the pipeline reports
is wrong, and the pipeline cannot learn from declines (e.g. which companies
silently filter on sponsorship).

Workflow (see DECLINE_INGESTION.md for the full procedure):
    1. Triage Gmail for decline emails since the last run.
    2. Build a declines JSON file (one object per decline event).
    3. Run this script. It matches each decline to a tracker row by
       company + role, sets Status to Rejected, and appends the
       cool-down row — both writes in the same step, or neither
       (dry-run first, then a real run).

Usage:
    python3 decline_ingest.py --declines declines.json \
        --tracker applications-tracker.xlsx \
        --cooldown rejection_cooldown.md [--dry-run]

Declines JSON format (a list of objects):
    [
      {
        "company": "Acme Corp",
        "role": "Senior Site Reliability Engineer",
        "declined_date": "2026-11-18",
        "applied_date": "2026-11-16",
        "req_id": "GH 8259621",
        "source": "Gmail 1a1efeca21d16d69",
        "reason": "other candidates"
      }
    ]
Only company, role, and declined_date are required. applied_date, req_id,
source, and reason are recorded in the cool-down row when present.

Matching: company and role are normalized (lowercase, punctuation and extra
whitespace stripped) before comparison. If several tracker rows match, the
req_id breaks the tie when given; otherwise the most recent Date Applied
wins. A decline with no matching tracker row is reported as UNMATCHED and
still gets a cool-down row — the decline is real even if the application
came from another bot — but no tracker row is ever invented.

Cool-down: 90 days from the decline date, per the standing rule. A decline
already present in the cool-down file (same company + role + date) is not
appended twice, and a tracker row already marked Rejected is left alone.

Requires: openpyxl (pip install openpyxl). The tracker is edited in place;
keep a backup (the Drive copy) before the first real run.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta

COOLDOWN_DAYS = 90


def normalize(text):
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(value):
    """Parse a YYYY-MM-DD date (or a datetime) into a date object."""
    if value is None:
        return None
    if hasattr(value, "date"):
        return value.date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def cooldown_until(declined):
    return declined + timedelta(days=COOLDOWN_DAYS)


def cooldown_row_text(decline, declined):
    parts = [decline["role"]]
    if decline.get("req_id"):
        parts.append(f"({decline['req_id']}")
        if decline.get("applied_date"):
            parts[-1] += f", submitted {decline['applied_date']}"
        parts[-1] += ")"
    elif decline.get("applied_date"):
        parts.append(f"(submitted {decline['applied_date']})")
    detail = " ".join(parts)
    if decline.get("reason"):
        detail += f". Stated reason: {decline['reason']}"
    if decline.get("source"):
        detail += f" (source: {decline['source']})"
    detail += f". Cool-down until {cooldown_until(declined).isoformat()} " \
              f"({COOLDOWN_DAYS} days)."
    return f"| {decline['company']} | {declined.isoformat()} | {detail} |"


def load_tracker(path):
    try:
        import openpyxl
    except ImportError:
        print("ERROR: openpyxl is required (pip install openpyxl).",
              file=sys.stderr)
        sys.exit(2)
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows())
    header = [str(c.value).strip() if c.value is not None else ""
              for c in rows[0]]
    col = {name.lower(): i for i, name in enumerate(header)}
    for needed in ("company", "role", "status", "date applied"):
        if needed not in col:
            print(f"ERROR: tracker is missing the '{needed}' column.",
                  file=sys.stderr)
            sys.exit(2)
    return wb, ws, rows, col


def find_tracker_row(rows, col, decline):
    """Best matching tracker row (1-based Excel row number) or None."""
    target_company = normalize(decline["company"])
    target_role = normalize(decline["role"])
    candidates = []
    for excel_row, row in enumerate(rows[1:], start=2):
        company = normalize(row[col["company"]].value)
        role = normalize(row[col["role"]].value)
        if company == target_company and role == target_role:
            candidates.append(excel_row)
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Tie-break 1: req_id, when the decline carries one.
    if decline.get("req_id") and "req id" in col:
        want = normalize(decline["req_id"])
        for r in candidates:
            if normalize(rows[r - 1][col["req id"]].value) == want:
                return r
    # Tie-break 2: most recent Date Applied.
    dated = []
    for r in candidates:
        d = parse_date(rows[r - 1][col["date applied"]].value)
        dated.append((d or datetime.min.date(), r))
    dated.sort(reverse=True)
    return dated[0][1]


def cooldown_has(cooldown_text, decline, declined):
    """True if the cool-down file already holds this decline."""
    for line in cooldown_text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if (normalize(cells[0]) == normalize(decline["company"])
                and cells[1] == declined.isoformat()
                and normalize(decline["role"]) in normalize(cells[2])):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Ingest decline emails into the tracker + cool-down list.")
    parser.add_argument("--declines", required=True,
                        help="JSON file with decline events")
    parser.add_argument("--tracker", required=True,
                        help="applications-tracker.xlsx path")
    parser.add_argument("--cooldown", required=True,
                        help="rejection_cooldown.md path")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print planned actions; write nothing")
    args = parser.parse_args()

    with open(args.declines, encoding="utf-8") as f:
        declines = json.load(f)
    if not isinstance(declines, list):
        print("ERROR: declines file must be a JSON list.", file=sys.stderr)
        sys.exit(2)

    wb, ws, rows, col = load_tracker(args.tracker)
    with open(args.cooldown, encoding="utf-8") as f:
        cooldown_text = f.read()

    actions, unmatched, skipped = [], [], []
    new_cooldown_rows = []
    for decline in declines:
        for field in ("company", "role", "declined_date"):
            if not decline.get(field):
                print(f"ERROR: decline event missing '{field}': {decline}",
                      file=sys.stderr)
                sys.exit(2)
        declined = parse_date(decline["declined_date"])
        if declined is None:
            print(f"ERROR: bad declined_date: {decline}", file=sys.stderr)
            sys.exit(2)

        excel_row = find_tracker_row(rows, col, decline)
        if excel_row is None:
            unmatched.append(decline)
        else:
            status_cell = ws.cell(row=excel_row, column=col["status"] + 1)
            if str(status_cell.value).strip().lower() == "rejected":
                skipped.append((decline, "tracker already Rejected"))
            else:
                actions.append((excel_row, decline))
                if not args.dry_run:
                    status_cell.value = "Rejected"

        if cooldown_has(cooldown_text, decline, declined):
            skipped.append((decline, "cool-down row already present"))
        else:
            row_text = cooldown_row_text(decline, declined)
            new_cooldown_rows.append(row_text)
            actions.append(("cooldown", decline))

    if new_cooldown_rows and not args.dry_run:
        with open(args.cooldown, "a", encoding="utf-8") as f:
            if cooldown_text and not cooldown_text.endswith("\n"):
                f.write("\n")
            for row_text in new_cooldown_rows:
                f.write(row_text + "\n")
    if actions and not args.dry_run:
        wb.save(args.tracker)

    # Report.
    mode = "DRY RUN — nothing written" if args.dry_run else "WRITTEN"
    print(f"Decline ingestion ({mode}): {len(declines)} event(s)")
    n_tracker = sum(1 for a in actions if a[0] != "cooldown")
    print(f"  Tracker rows set to Rejected: {n_tracker}")
    print(f"  Cool-down rows appended: {len(new_cooldown_rows)}")
    for target, decline in actions:
        where = f"tracker row {target}" if target != "cooldown" else "cool-down"
        print(f"    {where}: {decline['company']} — {decline['role']} "
              f"(declined {decline['declined_date']})")
    for decline, why in skipped:
        print(f"  SKIPPED ({why}): {decline['company']} — {decline['role']}")
    for decline in unmatched:
        print(f"  UNMATCHED (no tracker row; cool-down row still added): "
              f"{decline['company']} — {decline['role']}")
    if unmatched:
        print("  NOTE: unmatched declines mean the application was filed by "
              "another bot or predates the tracker. Investigate before "
              "re-applying to that company + role.")


if __name__ == "__main__":
    main()
