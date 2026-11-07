# ApplyForge

![zero prompt](https://img.shields.io/badge/run-zero%20prompt-blue)
![auto-apply](https://img.shields.io/badge/auto--apply-50--70%2Fday-green)
![runs 24 hours](https://img.shields.io/badge/runs-24%20hours-blue)
![runs on any agent](https://img.shields.io/badge/runs%20on-any%20agent-purple)
![no installs](https://img.shields.io/badge/installs-none-orange)

**AI job-application autopilot.** Upload your base resume once — Muse
extracts your roles, finds matching jobs, and for every job runs your
resume through a **seven-reviewer quality loop** (ATS recruiter, hiring
manager, peer engineer, executive skim, HR red-flag screen, AI-voice
detector, company lens) plus a final **interview vote** — then applies. **50–70
applications per day**, running 24 hours, on autopilot from the 3rd application. Your files
live in **Google Drive**, never on local disk, and this repo never holds
your personal data.

> **No prompt runs everything.** Load this repo into Muse (it reads every
> file, beginning to end) and it starts on its own — onboarding, role
> extraction, job matching, tailored resumes, applications — with no setup
> and nothing to paste. See §1.

> **Privacy by design:** this repo ships a blank template only. Your name,
> contact, employers, and metrics live in env vars and your Google Drive —
> never in this repository. Never list tools, metrics, dates, titles, or
> employers you cannot defend in an interview.

---

## 1. The pipeline (what happens)

```
You clone the repo into Muse
  -> Muse auto-syncs to the latest release first — always, with no manual
     update step, ever
  -> Muse asks you to upload your base resume (first run only)
  -> Muse asks your location and relocation: current city/state, willing
     to relocate, preferred locations if any
  -> Muse asks the candidate details companies mainly ask on their forms
     (see First-run onboarding) — asked once, remembered, never stored in
     this repo
  -> Muse extracts every role from it: titles, employers, dates, skills
  -> Muse searches jobs matching those roles: posted 60 min – 1 month ago,
     strictly USA-wide and never narrowed to a single state — all 50 states
     (remote, hybrid, or onsite anywhere in the USA);
     LinkedIn first (main priority), then company career portals,
     then other job sites
  -> Auto-search runs every 60 minutes and applying starts on its own
  -> Sponsorship check per company (strict): USCIS H-1B Employer Data Hub
     record for the last 5 years through the current year (plus
     site:h1bdata.info); apply ONLY to proven sponsors — everyone else
     is skipped, no exceptions
  -> Existing-employer check: skip any company that already appears as an
     employer in your uploaded base resume (current or past) — never apply
     to a current or former employer, no exceptions
  -> Duplicate check across bots (strict): before any resume is built,
     check the shared Drive job_resumes record — if a packet for this
     company + role already exists (from ANY bot, on ANY platform), skip.
     Never apply twice to the same company + role, no exceptions
  -> For each job: 50–70 applications per day, running 24 hours:
       read JD -> Draft 1 (keep EVERY section from the uploaded base resume:
       Projects, Publications, Awards, whatever the candidate included — never
       drop a section; order sections by experience: under 3 yrs =
       Summary, Education, Projects, Skills, Experience; 3+ yrs =
       Summary, Experience, Skills, Projects, Education)
       -> Review A (ATS recruiter) -> Draft 2
       -> Review B (hiring manager) -> Draft 3
       -> Review C (peer engineer) -> Review D (executive 6-second skim)
       -> Review E (HR red-flag screen) -> Review F (AI-voice detector)
       -> unanimous interview vote (all seven reviewers)
       -> build DOCX -> PDF -> layout MATCH check (exactly 1 page)
       -> fill application (upload the PDF resume ONLY on every portal —
          never the DOCX) -> smart form questions answered only from
          verified facts, in plain human writing — no AI bluff words
          (see §3, Smart form questions) -> submit
       -> resume, JD, and filled form are each written to Google Drive
          instantly, the moment they exist — never batched, never held
          until submission; filed pieces stay even if the application
          is later parked
```

### Starting (no prompt needed)

Loading the repo is the entire setup. Muse reads every file, beginning to
end, then starts onboarding automatically — no prompt to paste:

1. Muse asks you to **upload your base resume** (first run only).
2. Muse asks your **location and relocation**: current city/state, willing
   to relocate, preferred locations if any.
3. Muse asks the **candidate details companies mainly ask** on their forms
   (full list in First-run onboarding below). Asked once, remembered.
4. Muse asks you to **connect Google Drive**: Muse app → Settings →
   Connectors → Google Drive → Connect. (See `CONNECTORS.md`.)
5. Muse asks **where your Drive `job_resumes` folder is** — remembered as
   `OUT_BASE`; every application packet is filed under it.
6. Muse recommends connecting **Gmail** the same way, so it can verify
   application confirmations.
7. Muse checks your resume's **section coverage** for your experience band
   and tells you what's missing so you can reupload before the first build.

Then it extracts every role from your resume and starts the apply loop. If
Muse doesn't start on its own, just say **"start"** — that's the only
trigger phrase, and the only thing you ever type to begin.

### Sponsorship check (before every application)

Apply ONLY to companies that sponsor visas — strictly. **Before** any
resume is built:

1. Pull the company's H-1B record from the USCIS H-1B Employer Data Hub
   (supplemented by `site:h1bdata.info <Company>`), covering the last 5
   years through the current year: filings, approvals, and any explicit
   sponsorship statement in the posting.
2. **Apply only if** the company shows H-1B activity in that 5-year window
   or the posting explicitly offers sponsorship. Any company without it is
   skipped — no exceptions.
3. Log the signal per application: proven sponsor (years active) / no
   qualifying history — skipped.

Your work-authorization answers stay exactly as they are — the check changes
*which companies* get applications, never what you claim. Nothing is
misrepresented to pass it.

### Existing-employer check (before every application)

Never apply to a company you already work for or have worked for. **Before**
any resume is built:

1. Take the employer list from the Experience section of your uploaded base
   resume — every current and past employer.
2. **Skip any job whose company matches one of those employers** — no
   exceptions, even if the role, location, or team is different. A new role
   at a former employer is still a former employer.
3. Log the skip per application: existing employer — skipped.

### Duplicate check across bots (strict)

Different bots running this repo must never apply to the same job twice.
**Before** any resume is built:

1. **One shared record.** Every bot — Muse, Grok bot, Dots, Claude Duet,
   or any other — must point at the SAME Drive `job_resumes` folder (same
   `OUT_BASE`). That folder is the single record of what has been applied
   to. A bot with its own separate folder cannot see other bots'
   applications and will duplicate them.
2. **Check before building.** For every job, search the shared folder for
   an existing packet for that company + role
   (`job_resumes/<Company>/<YYYY-MM-DD>_<Role-Slug>/`). If a packet
   exists — from any bot, on any platform, on any day — **skip the job.
   No exceptions.**
3. **One application per company + role, ever.** Never re-apply to the
   same company + role, even if the earlier application came from another
   bot, another platform, or another day. Only the user can explicitly
   order a re-application, and then it is a new decision, not an automatic
   one.
4. **File before moving on.** Every submitted application is filed in the
   shared folder immediately after submitting, so the next bot — or the
   next run — sees it. Never submit without filing.

### Agent-agnostic rules

The rules in this repo live in the repo itself, not in any one app — any AI
agent that loads the repo end to end (Muse, Grok bot, Dots, Claude Duet, or
others) runs the same pipeline and the same checks.

### First-run onboarding

On the first run, Muse walks you through six steps — nothing to paste,
just answer:

1. **Upload your base resume.** From it, Muse extracts every role (title,
   employer, start/end dates), skills and tools per role, education,
   certifications, and contact details.
2. **Location and relocation.** Current city and state, whether you are
   willing to relocate, and preferred locations if any. This is asked
   first, before any job search, because it filters every role.
3. **Candidate details companies mainly ask.** The fields that show up on
   almost every company application form, so the pipeline can fill any
   form without inventing anything:
   - Full name, email, phone
   - Location: city, state, country (from step 2)
   - LinkedIn profile URL, GitHub profile URL, portfolio or website URL
     (if you have them)
   - Work authorization: legally authorized to work in the US, and whether
     you need sponsorship now or in the future
   - Country of citizenship
   - Have you worked for this company before
   - Do you know / are you related to / were you referred by anyone at
     this company
   - How did you hear about us
   - Earliest start date (how soon you can start)
   - Salary expectations (a number, a range, or your rule for answering
     when a range is posted)
   - Willing to relocate, preferred locations (from step 2)
   - Education: highest degree, school, graduation year
   - Years of relevant experience
   Asked once and remembered. Nothing personal is written to this repo or
   to local disk.
4. **Connect Google Drive.** Muse app → Settings → Connectors → Google
   Drive → Connect. Full steps in `CONNECTORS.md`.
5. **Point at your Drive folder** (e.g. your Drive's `job_resumes` folder).
   That path becomes `OUT_BASE` — every application from then on is filed
   there.
6. **Connect Gmail** (recommended): Muse app → Settings → Connectors →
   Gmail → Connect, so Muse can verify application confirmations.
7. **Section-coverage check.** Muse compares your resume against the
   sections expected for your experience band (under 3 yrs: Summary,
   Education, Projects, Skills, Experience; 3+ yrs: Summary, Experience,
   Skills, Projects, Education) and tells you what's missing so you can
   reupload a complete resume before the first build.

Nothing personal is written to local disk or to this repo.

### Approval gates (first 2 only)

For your **first 2 applications**, Muse stops and asks for approval twice:

1. **Resume approval** — Muse shows the tailored resume; you approve or ask
   for changes.
2. **Submission approval** — Muse shows the filled application (every field);
   you approve before it submits.

From the **3rd application onward, no approvals** — Muse tailors, verifies,
and submits on its own. (Muse still never invents employers, titles, dates,
metrics, tools, salary, or work-authorization facts, and still strips any
number it cannot verify.)

### Daily volume: 50–70 applications, 24 hours

The pipeline runs around the clock: job search re-runs every 60 minutes,
24 hours a day, and applying starts on its own. Each day it submits a
minimum of 50 and a maximum of 70 applications.

Each application is token-expensive: JD reading, multi-draft tailoring, two
review passes, PDF build, layout verification, and form filling. The 50–70
band keeps token usage sustainable while running serious volume, day and
night.

### Google Drive, not local disk

Every piece is written to Drive instantly, the moment it exists — never
batched, never held until submission:

```
<Your Drive>/job_resumes/<Company>/<YYYY-MM-DD>_<Role-Slug>/
  <First>_<Last>_Resume.pdf     (the file actually uploaded)
  <First>_<Last>_Resume.docx    (spare copy — filed in Drive, never uploaded
                               to a portal)
  JD.md                         (the job description as posted)
  APPLICATION_FORM.md           (every question + the submitted answer)
```

**Instant updates.** The JD is written to Drive the moment it is read, the
tailored resume the moment it is built, and the filled form the moment it
is filled — each piece lands in Drive immediately, before submission.
Filed pieces stay even if the application is later parked or skipped; they
are the record of what was prepared. Nothing is deleted to make room.

Control the root with `OUT_BASE` (set during onboarding):

```bash
OUT_BASE="/path/to/your/Google Drive/job_resumes" \
APPLICANT_NAME="Jane Doe" COMPANY=Acme ROLE_SLUG=Backend-Engineer \
node build_resume.js
```

| Env var | Default | Purpose |
|---|---|---|
| `APPLICANT_NAME` | `YOUR FULL NAME` | Identity + filename base (`First_Last_Resume`) |
| `COMPANY` | `ExampleCorp` | Company folder |
| `ROLE_SLUG` | `Example-Role` | Role folder suffix (keep filesystem-safe) |
| `RUN_DATE` | today (`YYYY-MM-DD`) | Date folder prefix |
| `OUT_BASE` | Google Drive `job_resumes` if a Drive mount is found, else `~/Desktop/job_resumes` | Root — set this to your Drive folder during onboarding |

---

## 2. You install nothing

There is nothing to install on your machine — no Node, no Python, no
LibreOffice, no fonts. **Muse runs everything** in its own environment:
dependency setup, resume builds, PDF conversion, and layout verification.

All you do:

1. Get the Muse app at [muse.ai](https://muse.ai) — iPhone (App Store),
   Android (Google Play), the Mac app, or the web app, which works on any OS
   including Windows.
2. Bring this repo into Muse so it can read every file, beginning to end.
   Pick whichever your Muse surface supports:

   **Clone it** (recommended — keeps you on the latest release):
   ```bash
   git clone https://github.com/forgephantom/applyforge.git
   ```
   Then point Muse at the cloned folder (upload it, attach it, or open the
   folder in the desktop app).

   > **Staying updated:** fully automatic — every run starts by syncing
   > your copy to the latest GitHub release before anything else runs. There
   > is no manual update step; you never need to pull, re-download, or
   > paste an update prompt. (ZIP downloads: syncing needs the git
   > history, so prefer the one-time clone above — after that, updates are
   > automatic.)

   **Or download the ZIP:** open
   [github.com/forgephantom/applyforge](https://github.com/forgephantom/applyforge),
   click **Code → Download ZIP**, unzip it, and give the folder to Muse.

   **Or grab a release:** tagged versions with changelogs live under
   [Releases](https://github.com/forgephantom/applyforge/releases) —
   download the source ZIP for the version you want.
3. Done — Muse starts onboarding on its own: resume upload, Drive/Gmail
   connect, `OUT_BASE`. If it doesn't start, just say **"start"**.

### How to use on every platform — Muse, Grok bot, Dots, Claude Duet

ApplyForge is a set of rules in this repo, not a feature of any one app.
Any AI agent that can read these files end to end runs the same pipeline.
The steps are the same on every platform:

1. Give the agent this repo — clone it, upload the folder, or attach the
   files, whichever the platform supports.
2. Ask the agent to read every file, beginning to end.
3. The agent starts onboarding on its own: upload your base resume, connect
   Google Drive, point at your Drive `job_resumes` folder, connect Gmail.
4. If it doesn't start, just say **"start"** — that's the only trigger
   phrase, on every platform.

Platform notes:

- **Muse** — Get the app at [muse.ai](https://muse.ai) — iPhone (App Store),
  Android (Google Play), the Mac app, or the web app. Clone the repo and
  point Muse at the folder. Drive and Gmail connect from Settings →
  Connectors. See `CONNECTORS.md`.
- **Grok bot** — Load the repo files into Grok, ask it to read every file
  beginning to end, then say **"start"**. Connect Drive and Gmail however
  Grok supports them; the pipeline and the rules are unchanged.
- **Dots** — Load the repo files into Dots, ask it to read every file
  beginning to end, then say **"start"**. Same pipeline, same rules.
- **Claude Duet** — Load the repo files into Claude Duet, ask it to read
  every file beginning to end, then say **"start"**. Same pipeline, same
  rules.

Whatever the platform, the agent always syncs to the latest release first,
so every user — new or existing — runs the current rules with no manual
update and no impact on existing packets or approvals.

Muse handles the rest, including installing the pinned dependencies
(`docx@8.5.0`, `pymupdf`, `pypdf`) the first time it builds, and verifying
the sample template renders exactly 1 page before your first real run.

---

## 3. Per-application quality loop (runs automatically)

Every single application goes through this — including the auto-approved ones.
The bar is **10/10 from every reviewer**; any score below 10 sends the draft
back for another pass (max 3 full rounds), and nothing ships until **all seven
reviewers vote "interview"**:

1. **Reads the JD** — must-have skills, nice-to-haves, exact keywords,
   seniority, top responsibilities.
2. **Draft 1** — rewrites the title line (`<JD role> • <lane descriptor>`),
   summary, skills, and bullets against the JD using your real history
   (maximum honest keyword match). The summary's first line states your
   years, lane identity, and strongest attested scale or outcome.
3. **Review A — ATS recruiter.** Scores keyword coverage must-have by
   must-have, scannability, parsing risks. Fixes the gaps.
4. **Review B — hiring manager.** Scores credibility and impact. Hard
   **impact gate**: every bullet must carry ownership, scale, or a
   measurable outcome — duty-only bullets fail, no matter how well they
   match keywords.
5. **Review C — peer engineer.** Would the tooling and scale claims survive
   a technical screen? Catches misused terms and fluff an engineer would
   spot.
6. **Review D — executive skim.** The 6-second test: title + summary + first
   two bullets must say who you are and why you're strong instantly.
7. **Review E — HR red-flag screen.** Timeline gaps, title-scope
   consistency, level fit, verification risk.
8. **Review F — AI-voice detector.** Scans the banned-word list and AI
   phrasings (em dashes, "not only/but also", triple parallelisms,
   "furthermore", uniform bullet rhythm, hedged claims like "helped with")
   and rewrites anything that reads machine-generated.
9. **Interview vote.** All seven reviewers vote "interview" or "no
   interview" with a one-line reason. Any "no" triggers a targeted
   revision and a re-vote. Dissent after 3 rounds is shown to you with the
   reason.
10. **Build + verify** — writes the `.docx`, converts to PDF with
    LibreOffice, runs `compare_layout.py` against your original PDF. If
    section headers shifted or it spilled to 2 pages, Muse trims words and
    rebuilds until **MATCH** (identical spacing, exactly 1 page).
11. **Apply + record** — fills the application from your verified facts,
    submits (after approval for the first 2), and saves the full packet
    (PDF + DOCX + JD + every question/answer) to your Drive folder.
    Resume, JD, and form are each written instantly, the moment they exist
    (see Instant updates); filed pieces stay even if the application is
    later parked.

### Smart form questions — answered correctly, no AI bluff words

Application forms ask open-ended screening questions ("Why this role?",
"Describe a project where you...", "What makes you a good fit?"). These
are answered from the verified fact base only — the uploaded base resume
plus the onboarding answers — and in plain human writing:

1. **Correct first.** Every claim must trace to the resume or the
   onboarding answers: a real employer, a real project, a real number. If
   a question cannot be answered from verified facts, park it (doubt rule)
   — never invent a story, a metric, or a skill to fill the box.
2. **No AI bluff words.** No buzzwords from the ban list
   (`Resume_Section_Spec.md`: leverage, seamless, robust, streamline,
   spearhead, empower, holistic, synergy, utilize, foster, pivotal,
   harness, world-class, best-in-class, state-of-the-art, cutting-edge,
   passionate, results-driven, proven track record, next-gen,
   game-changing, bleeding-edge, "responsible for"), no em dashes, no
   semicolons in body text, no smart quotes, no filler phrases ("in order
   to", "it is worth noting that", "at the end of the day", "the ability
   to"), no hedged filler ("helped with", "was involved in"). Short
   sentences, plain words, straight quotes only when truly needed.
3. **Defensible in an interview.** Write every answer as if the
   interviewer will ask you to prove it on the spot — because they will.
   If you could not defend a sentence in an interview, do not write it.

After a batch, Muse reports: all seven scores before/after, the interview
vote, top 3 changes, JD coverage %, anything omitted, and every claim
you'd need to defend in an interview.

---

## 4. How it works (technical)

```
Base resume (uploaded once, kept private)
  -> extracted profile: roles, employers, dates, skills
  -> job search matched to those roles
  -> per job: JD -> content rewrite (honesty rules, no fabrication)
            -> seven-reviewer loop: ATS -> hiring manager -> peer engineer
               -> executive skim -> HR red flags -> AI-voice detector
               -> company lens
            -> unanimous interview vote (10/10 bar per reviewer)
            -> build_resume.js (docx lib: constants S_NAME..S_SK,
               helpers name/subtitle/contact/section/summary/skill/
               jobline/role/bullet/certline/eduline,
               Letter page, 0.22"/0.6" margins, Carlito, navy 1F3864)
            -> <First>_<Last>_Resume.docx (filed in Google Drive)
            -> LibreOffice (soffice --headless --convert-to pdf)
            -> <First>_<Last>_Resume.pdf (the upload)
            -> compare_layout.py (PyMuPDF: section header Y-positions +
               line counts vs the original; MATCH = identical spacing, 1 page)
            -> application submitted -> packet saved to Drive
```

Why it is built this way:

- **Content and layout are separated.** `Resume_Section_Spec.md` governs
  *what* to write (8 fixed sections, bullet template, ban list: plain hyphens
  only, no em dashes, no buzzwords like leverage/seamless/robust).
  `build_resume.js` governs *how it looks*. Muse edits strings, never
  sizes or spacing.
- **Rewritten text reflows lines**, so a longer bullet pushes every section
  below it down. `compare_layout.py` catches this numerically (header heights
  in points + lines per section) and Muse trims words until MATCH.
- **Pinned toolchain matters:** `docx@8.5.0` (v9 renders spacing differently),
  real Carlito font (substitutes shift line wraps), LibreOffice conversion.
- **Honesty gate:** role titles, employers, dates, metrics, and skills must be
  real and defensible. Anything in the JD without real backing is reported as
  omitted, not added. Disputed numbers are stripped, never shipped.
- **The repo stays data-free:** your resume, tailored outputs, and
  application records live in Google Drive. Cloning this repo gives a new
  user the pipeline, not your data.

---

## 5. Files

| File | What it is |
|---|---|
| `build_resume.js` | Layout engine + sample content. Edit strings only; your real data comes from env vars or your private copy. |
| `skills/jd-resume-review-loop/SKILL.md` | The seven-reviewer quality loop skill: the full review sequence, scoring rules, interview vote, and style bans. Load it into Muse (or any agent) to run the loop. |
| `Resume_Section_Spec.md` | Content rules: sections, bullet template, honesty/ban rules. |
| `compare_layout.py` | Layout verifier: `python3 compare_layout.py ORIG.pdf NEW.pdf`. |
| `HOW_TO_RUN_MUSE.md` | Zero-prompt quick guide: load the repo, Muse starts on its own. No installs. |
| `CONNECTORS.md` | Connecting Google Drive and Gmail from the Muse app (Settings → Connectors), and switching accounts later. |
| `package.json` / `requirements.txt` | Pinned deps. |

## 6. Troubleshooting

Everything below is Muse's job to fix — just describe the symptom in chat.

- **PDF is 2 pages:** tailored text ran long. Ask Muse to shorten
  summary/bullets a few words (keep metrics + tool names) and rebuild. Never
  shrink fonts/margins.
- **Wraps differ from the original:** wrong font or wrong docx version in
  Muse's environment — ask Muse to reinstall the pinned deps (`docx@8.5.0`,
  Carlito) and rebuild.
- **Verification never reaches MATCH:** Muse is editing layout numbers
  instead of trimming words — remind it: content strings only, constants
  untouched.
- **Drive folder not found:** re-run onboarding and give the exact Drive path;
  it becomes `OUT_BASE` for every later run.

## 7. Found an issue?

Open an [issue](https://github.com/forgephantom/applyforge/issues) — reported
problems are triaged and fixed automatically, no waiting on a maintainer.
