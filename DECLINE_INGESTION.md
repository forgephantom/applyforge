# Decline Ingestion

Declines only help the pipeline if they are written back. The 2026-11-19
ATS/decline review found the feedback loop broken: the cool-down file was
missing at least 21 companies' declines that exist in Gmail, and 50 of 56
known declines still showed Status "Submitted" in the tracker. Until
declines are ingested, every decline-rate number the pipeline reports is
wrong, and the pipeline cannot detect patterns (for example, which
companies silently filter on sponsorship).

This document is the procedure. `decline_ingest.py` is the tool.

## The step

Run on a schedule (daily, with the afternoon edition), and always as one
step: triage Gmail, then update the tracker AND the cool-down file
together. Never update one without the other.

1. **Triage Gmail.** Search the applications mailbox for decline mail
   since the last ingestion run. Decline senders are usually
   no-reply addresses from the ATS (Greenhouse, Ashby, Lever, Workday)
   or the company's recruiting team. Read each candidate email's full
   body: a decline says the company will not move forward with the
   application. Do not count interview invitations, assessments, or
   "still under consideration" mail as declines.
2. **Build the declines JSON.** One object per decline event, with the
   fields below. `company`, `role`, and `declined_date` are required;
   the rest are recorded in the cool-down row when present.

   ```json
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
   ```

   - `declined_date` is the date the decline email arrived (the cool-down
     clock starts there), in `YYYY-MM-DD`.
   - `reason` records ONLY what the email actually states. Most declines
     state no reason (84.7% in the Nov 19 review) — leave the field out
     rather than inventing one. Never guess a reason from the role or
     the company.
   - One event per company + role + decline date. A second decline email
     for the same role is a duplicate, not a new event.
3. **Dry-run first.** `python3 decline_ingest.py --declines declines.json
   --tracker applications-tracker.xlsx --cooldown rejection_cooldown.md
   --dry-run`. Check the planned actions: every decline should match a
   tracker row, and no cool-down row should duplicate an existing one.
4. **Run it.** Same command without `--dry-run`. The script sets each
   matched tracker row's Status to Rejected and appends the cool-down
   row in the same step.
5. **Verify.** Re-read the tracker rows and the tail of the cool-down
   file. Report the count ingested.

## Matching and edge cases

- Matching is by normalized company + role; req ID breaks ties, then the
  most recent Date Applied. If the script reports UNMATCHED, the
  application was filed by another bot or predates the tracker: the
  cool-down row is still added (the decline is real), but no tracker row
  is ever invented. Investigate the unmatched decline before re-applying
  to that company + role.
- A decline for a role the pipeline never applied to (for example, a
  stale application from before the sprint) still gets a cool-down row:
  the company has rejected the candidate, and the cool-down applies
  company-wide.
- Cool-down is 90 days from the decline date. A decline already in the
  cool-down file is not appended twice.
- Role-level vs company-level: the cool-down file records the declined
  role, but the cool-down applies company-wide (do not apply to other
  roles at that company until it expires), with the two standing
  exceptions in the cool-down file's header (a referral, or a materially
  better-fitting role at a company with a strong H-1B gate).

## What this does not do

- It does not decide WHY a decline happened. Employers almost never say.
  The ingestion step records the fact and the stated reason, if any.
  Pattern analysis (decline rate by platform, by company size, by
  sponsorship signal) is a separate analysis over the ingested records,
  and it needs the tracker columns added in v2.10.0 (Required Years,
  Coding Share, Sponsorship Signal) to be answerable.
- It does not close interview loops. A decline after an interview also
  closes the tracked interview goal — that is a separate bookkeeping
  step for the agent, not this script.
