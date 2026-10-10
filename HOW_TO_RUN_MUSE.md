# How to Run This on Meta Muse

Everything in this repo runs through **Meta Muse** — no installs, no setup
commands, no other runner, and **no prompt to paste**. You bring the repo
into Muse and it starts on its own: resume intake, role extraction, job
matching, tailored resumes, and applications.

## No prompt — it starts itself

1. Get Muse at [muse.ai](https://muse.ai) — iPhone (App Store), Android
   (Google Play), the Mac app, or the web app, which works on any OS
   including Windows.
2. Load this repo into Muse — clone it or upload the folder, whichever your
   Muse surface supports (`git clone
   https://github.com/forgephantom/applyforge.git`). Muse reads every file,
   beginning to end: the pipeline spec, the content rules, the layout
   engine, and this guide.
3. That's it — Muse begins onboarding automatically: base-resume upload,
   Google Drive + Gmail connect (Muse app → Settings → Connectors — see
   `CONNECTORS.md`), and your `OUT_BASE` folder. If it doesn't start on its
   own, just say **"start"**.

Muse handles dependency setup (`docx@8.5.0`, `pymupdf`, `pypdf`), the
pinned toolchain, PDF conversion, and layout verification on its own.

## What the prompt kicks off

- **Onboarding (first run only).** Muse asks for your base resume, extracts
  all roles/skills/employers/dates, and records your Drive folder. Your
  personal data lives in Drive and in the session — never in this repo.
- **Per job.** Muse reads the JD, rewrites title/summary/skills/bullets
  under honesty rules, runs the **seven-reviewer loop** (ATS recruiter,
  hiring manager, peer engineer, executive skim, HR red-flag screen,
  AI-voice detector, company lens — see `skills/jd-resume-review-loop/SKILL.md`),
  requires a **unanimous interview vote** at a **10/10 bar**, builds with
  `node build_resume.js`, converts with
  `soffice --headless --convert-to pdf`, and verifies with
  `python3 compare_layout.py ORIGINAL.pdf <new pdf>` until it prints MATCH —
  trimming words (never layout numbers) if sections run long.
- **Apply + record.** Muse fills the application from your verified facts
  (uploading the PDF resume only — never the DOCX),
  submits (after your approval for the first 2), and files the full packet
  to Drive — only for jobs actually applied to; anything prepared but not
  submitted is removed.
- **Daily report.** Roles submitted, JD coverage %, honestly omitted items,
  and every claim you should be ready to defend in an interview.

## The standing rules Muse follows

- **Job sourcing:** only jobs posted between 60 minutes and 1 month ago,
  strictly USA-wide and never narrowed to a single state — all 50 states;
  every listing must be US-based (remote, hybrid, or onsite anywhere in the
  USA). **Auto-search:** the search runs every 60 minutes and applying
  starts automatically.
  **Sponsorship check before every application (strict):** apply ONLY to
  companies that sponsor visas. Pull the company's H-1B record from the
  USCIS H-1B Employer Data Hub (plus `site:h1bdata.info <Company>`) for the
  last 5 years through the current year; apply only with H-1B activity in
  that window or an explicit sponsorship offer in the posting — everyone
  else is skipped, no exceptions. Work-authorization answers stay exactly
  as they are — nothing gets misrepresented. Search LinkedIn first (main
  priority), then company career portals, then other job sites.
- **First 2 applications:** approval twice each — once for the tailored
  resume, once for the filled application before submit. This is the safety
  default: the user sees exactly what goes out under their name before
  autopilot begins.
- **3rd application onward:** full autopilot, no approvals — including
  standard acknowledgement checkboxes (accuracy, assessment integrity, at-will
  employment, privacy notices, codes of conduct). (Standing auto-approval for
  all job-site actions once trust is established.)
- **Volume:** 50 confirmed applications per day (minimum), running 24 hours —
  the search re-runs every 60 minutes and applying starts on its own. Each
  one is token-heavy: JD reading, multi-draft tailoring, six review passes
  + interview vote, build, verify, form fill.
- **Honesty gate:** role titles, employers, dates, metrics, and skills must
  be real and defensible. Disputed numbers are stripped, never shipped.
- **Screening-answer truth check (hard, 2026-10-09):** when a form asks a
  required "experience with X" question, cross-check the answer against the
  tailored resume's ACTUAL content before answering. If the resume has zero
  mentions of X and the review summary names it as an honest gap, the answer
  is No — never Yes from "general experience." A Yes on a screening question
  is a factual claim about the applicant; it must be defensible in an
  interview. When the truthful answer disqualifies, skip the application and
  log why.
- **Export-control form check (hard, 2026-10-09):** the application FORM's
  questions govern, not the JD text. Always read the form's own fields for
  U.S.-person / export-control / ITAR questions before submitting — a JD
  text-fetch saying "clean" does not override a form-level question. If the
  form requires U.S.-person status the applicant does not hold, skip.
- **Skip fast (user-directed 2026-10-09):** if an application needs input only
  the user can provide — OTP/verification code, sign-in, account creation,
  browser takeover, manual challenge, or an unknown fact — park it within 5
  minutes and move to the next role. Blocked applications never burn run time
  and never reduce the day's count; they are retried once the user supplies
  what is needed.
- **Drive, not local disk:** nothing personal is written to local disk or
  to this repository. Only jobs actually applied to are saved to Drive —
  anything prepared but not submitted is removed.

## How it works (technical)

```
Base resume (uploaded once, kept private)
  -> extracted profile: roles, employers, dates, skills
  -> job search matched to those roles
  -> per job: JD -> content rewrite (honesty rules, no fabrication)
            -> ATS review -> hiring-manager review
            -> build_resume.js (fixed layout: Letter, 0.22"/0.6" margins,
               Carlito, navy 1F3864 — content strings only, never sizes)
            -> <First>_<Last>_Resume.docx (auto-filed in Google Drive)
            -> LibreOffice (soffice --headless --convert-to pdf)
            -> <First>_<Last>_Resume.pdf (the upload)
            -> compare_layout.py vs your original PDF: MATCH = identical
               spacing, exactly 1 page
            -> application submitted -> packet saved to Drive
```

**Content and layout are separated.** `Resume_Section_Spec.md` governs *what*
to write (8 fixed sections, bullet template, ban list: plain hyphens only,
no em dashes, no buzzwords like leverage/seamless/robust).
`build_resume.js` governs *how it looks*. Muse edits strings, never sizes
or spacing.
