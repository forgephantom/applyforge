---
name: "jd-resume-review-loop"
description: "Tailor the base resume to a job description through a fast-apply review loop (computed ATS score via ats_score.py gates every build: overall 10/10 required, Skills + Experience presence machine-measured; early exit at 90%+ top-10 keyword coverage; otherwise six reviewers in parallel plus company lens and a final interview vote; volume mode uses a lighter 4-reviewer parallel pass), then render the final one-page PDF/DOCX. Use for EVERY job-application resume build, no exceptions."
---

# JD Resume Review Loop

## Purpose

Produce a JD-matched, one-page tailored resume from the base resume through a structured review loop, then render and file it per the job-sprint conventions. No tailored resume ships without this loop.

INTERVIEW-CONVERSION STANDARD (user-set 2026-10-03, binding for EVERY resume): every resume is built to maximum strength for one goal — getting interviews. The skill-experience coverage map and the company-lens review run on every build, no exceptions, no shortcuts. The bar is unanimous "interview" votes and 10/10 scores, not mere completion.

FAST APPLY (v2.8.3, binding): speed over sequential reviews. After Draft 1, the six independent reviewers (A–F) run IN PARALLEL, never one after another. EARLY EXIT: a Draft 1 covering 90%+ of the JD's top-10 keywords with no red flags skips the remaining review rounds and ships. VOLUME MODE (behind the hourly or daily target): a lighter 4-reviewer parallel pass (ATS, hiring manager, peer, AI-voice) + at most 1 rewrite round; ship if the average score is >= 8.5 with no hard fails. A hard fail is any red flag, banned word, AI phrasing, invented fact, duty-only bullet, or failed layout MATCH. Fast apply trades review rounds for speed — never for invented facts, AI voice, or a skipped layout check.

COMPUTED ATS SCORE (v2.10.0, binding): coverage is MEASURED, never judged. Every build runs `python3 ats_score.py --jd JD.md --pdf <resume>.pdf --skills top10.json --out ats_score.json` from the repo root, and the score JSON goes in the packet folder. No reviewer writes a "match %" from judgment: Review A reads the computed score. The gate is overall 10/10 — a build below 10/10 does not submit until every missing skill is either added with a truthful Experience anchor or recorded as a named honest gap in `APPLICATION_FORM.md` (a skill with no honest anchor stays off the resume; the gap record is what unblocks submission, not a reviewer's call). Experience below 9/10 prints a warning: Skills-only keywords pass an ATS parser but fail human credibility review, so every Skills-only skill is listed explicitly in the packet.

## Inputs

1. Base resume (content authority): `~/workspace/resume-tailor/baseline/build_resume.js`. Every run starts from the BASE, never from a previous tailored version. If unclear which file is the base, ask.
2. Target JD (text, file, or link). No JD given: ask for it. Never guess.

## Binding user overrides (these win over the generic rules below)

- Output filenames are ALWAYS exactly `Your_Name_Resume.pdf` / `.docx`. Never put role or company in the filename.
- Files live in `~/workspace/job_resumes/<Company>/<YYYY-MM-DD>_<Role-Slug>/` as PDF + DOCX + `JD.md` + `APPLICATION_FORM.md`, mirrored under Drive `job_resumes/`. Per-role build scripts live in `~/workspace/resume-tailor/jobs/<slug>/`.
- The final resume MUST be one page and pass the layout MATCH check (`compare_layout.py` vs the baseline). Pipeline notes: `~/TOOLS.md` ("Resume pipeline" section).
- Additions: the user attests real experience across JD-relevant fields even when unlisted on the base resume. JD-requested skills/tools MAY be added, attributed to the employer where gained (e.g. a monitoring tool to the employer where the candidate ran on-call). NEVER invent: employers, job titles, dates, metrics/percentages, years of experience, salary, credentials, legal/work-auth facts. No `[X%]` placeholders in the final file: strip any metric that is not verified. Honest omissions (no attested experience) are left out and named, never faked.
- SKILL-EXPERIENCE MATCH (hard, user-set 2026-09-30): every skill or tool in the Skills section must trace to real experience — anchored by at least one Experience bullet, or explicitly user-attested with the employer where it was gained. No aspirational, JD-only, or course-only skills. Review A must flag any skill lacking an experience anchor; either anchor it with a bullet or delete it. The Skills section and the Experience section must tell the same story.
- SKILL-EXPERIENCE COVERAGE MAP (hard, user-set 2026-10-03; machine-enforced v2.10.0): for each of the JD's top 10 skills, build a map row — skill → in Skills section? → in Experience? → at which employer(s)? Every top-10 skill must appear in BOTH the Skills section and at least one Experience bullet when truthfully supportable. This rule is enforced by `ats_score.py`, not by reviewer judgment: the script measures Skills-section presence and Experience-bullet presence per skill from the extracted PDF text, and the score JSON in the packet is the record. A key skill must be evidenced at every employer where they actually used it, and the map must name which employer anchors each skill. Anchor only to real experience — never invent usage at an employer where they didn't use it. A skill with no honest anchor stays off the resume and is named as a gap in the review summary, never faked in.
- SINGLE TITLE PER EMPLOYER (hard, user-set 2026-09-30): every Professional Experience entry shows ONE role title only — the title actually held at that employer. Never show dual titles, stacked titles, or "X / Y" variants on any entry. (This is the user's directed presentation of their own roles; list it under "Confirm before applying".)
- REWRITE LATITUDE (user-granted 2026-09-30, refined 2026-09-30): the Skills section may be freely rewritten per JD (reorder, rename categories, swap in JD keywords) within the skill-experience match rule. The Summary is always rewritten per JD at the same quality bar: first line states years + lane identity + strongest attested scale/outcome. Experience bullets are strong as written: tailoring may lightly reframe them for the JD (keyword alignment, reordering, leading with the most relevant), but must NEVER weaken their substance — no hollowing out, no dropping core claims (quantified outcomes such as incident reduction, utilization gains, MTTR improvements, hours saved, where present). Strengthen around them, not instead of them. The truth boundary still holds (no invented employers, titles, dates, metrics, tools, or years).
- BULLET FORMULA (user-set 2026-10-03, binding — supersedes the 2026-10-01 XYZ rule): every Experience bullet follows [Action Verb] + [What You Did] + [Quantified Result]. At least 70% of bullets must carry an honest metric (%, hours, counts, scale). Never invent a number to satisfy this: use attested metrics, or honest scope counts derived from items already listed in the bullet (e.g., "5 observability platforms" for five named tools, "4 teams" for four named teams). Bullets with no attested number stay clean and unquantified — a forced fake metric fails Review E. Canonical wording: ~/workspace/resume-tailor/preview_bullets_v2/build_bullets_v2.js.
- TOP-10 JD SKILLS (user-set 2026-10-03, binding): for every build, extract the JD's top 10 skills/keywords first, scan the resume against each one, and rewrite until 100% of the top 10 appear in context (Skills section plus at least one Experience bullet each, using the JD's exact wording). The scan is `ats_score.py` against a `top10.json` skills file kept in the packet — run the scan-check-rewrite cycle multiple times, one pass is never enough.
- MISSING SKILLS (user-set 2026-10-03): a top-10 JD skill missing from the resume gets added when the user attests the experience or it anchors to an existing bullet, attributed to the employer where gained. Every such addition goes in the "Confirm before applying" list.
- ROLE MATCH (user-set 2026-10-03): the resume headline title mirrors the JD's role name 100% (existing title rule). Employer job titles in the Experience section are NEVER changed — they are the titles actually held. Background checks verify titles; the truth boundary holds.
- ITERATE UNTIL PASS (user-set 2026-10-03, binding): run the ATS-scanner, recruiter, and hiring-manager analyses in rounds. Anything any of the three flags as missed sends the draft back for a targeted rewrite, then re-scan. Repeat until all three pass or 5 full rounds are done. If gaps remain after round 5, ship the best version and show the user exactly what still misses and which reviewer flagged it. FAST APPLY (v2.8.3): in volume mode, at most 1 rewrite round total — ship if the average is >= 8.5 with no hard fails.
- Writing style: plain and smart. No AI buzzwords, no em dashes, no semicolons, no smart quotes. Banned words: leverage, utilize, spearheaded, orchestrated, delve, robust, seamless, cutting-edge, innovative, dynamic, holistic, synergy, foster, pivotal, streamline, empower, passionate, results-driven, detail-oriented, proven track record, responsible for, adept at, well-versed. Prefer plain verbs: built, ran, fixed, cut, moved, wrote, led, set up, migrated, owned. Commas and short sentences. Vary bullet openers; no more than two bullets starting with the same verb.
- Every addition not in the base resume goes in a "Confirm before applying" list shown to the user.
- Match target: 100% of the JD's must-have skills/responsibilities and 90%+ of nice-to-haves, in context (Skills section plus at least one Experience bullet per must-have), using the JD's exact wording. Score every review against a written checklist.

## Workflow

### Step 1: Read the JD (no comparison yet)
Do not compare or score the base resume against the JD. Just read and note privately: must-have skills, nice-to-haves, exact keywords and phrasing, seniority level, top 3 responsibilities. Comparison starts after Draft 1 exists.

### Step 2: Draft 1 (tailor)
Editable: the resume title (headline under the name), Summary, Skills, Experience. TITLE RULE (lane-specific descriptor, strengthened 2026-09-30; supersedes the single-descriptor rule of 2026-09-28): the title line is "<JD role>  •  <lane descriptor>" — the JD's role name followed by the descriptor for the role's lane, two spaces around the bullet. Pick the descriptor by lane:
- SRE: Production Reliability & Scale
- Capacity (engineer/planner/manager/analyst): Cloud Efficiency, Capacity & FinOps
- Production Engineering: Production Engineering & Reliability
- Infrastructure Engineering: Infrastructure, Automation & Scale
- Reliability Engineering: Reliability Engineering & Operations
- Performance Engineering: Performance Engineering at Scale
Example: "Senior Site Reliability Engineer  •  Production Reliability & Scale". If a posting's title is vague or unusable, fall back to "Software Engineer  •  <lane descriptor>". Never use the Capacity/FinOps descriptor on a non-capacity lane: a FinOps-flavored subtitle on an SRE resume mispositions the candidate. Target lanes come from the user's `config.yaml` (`target_lanes` in `config.example.yaml`); the descriptors above cover the common infrastructure lanes — for a lane not listed, write a descriptor in the same "<discipline> & <scope>" shape.
SUMMARY RULE: the first line must state years of experience, the lane identity, and the single strongest attested scale or outcome fact for that lane. No generic openers.

### Step 3: Early-exit check (v2.8.3)
Before any review runs, run the computed score on Draft 1: `python3 ats_score.py --jd JD.md --pdf <draft>.pdf --skills top10.json`. Does it already cover 90%+ of the JD's top-10 keywords (in context — Skills section plus at least one Experience bullet each), with no red flags (no banned words, no AI phrasing, no timeline/title/level issues, no duty-only bullets)? If yes, skip to Step 9 (Deliver). Never review for the sake of reviewing. The early exit skips review rounds only — the submission gate (overall 10/10, or every missing skill recorded as a named honest gap) still applies before anything ships.

### Step 4: Parallel reviews A–F (standard mode)
Reviews A–F run IN PARALLEL on Draft 1 — never one after another. Each reviewer scores out of 10 and lists exactly what to fix.

#### Review A (ATS recruiter)
Run on Draft 1, never on the base resume. Read the computed score from `ats_score.py` — do NOT write a judged "match %": the script's overall / Skills / Experience numbers are the coverage verdict. Output briefly: keyword match (must-haves matched vs missing, one by one, from the score JSON); what's correct; what's wrong (weak verbs, vague bullets, buried skills, keyword stuffing, parsing risks); the computed score (overall x/10, Skills x/10, Experience x/10); score out of 10.

ATS TEXT SIMULATION (hard, added 2026-10-03; computed by `ats_score.py` since v2.10.0): the script runs the final PDF through a plain-text extractor (pdftotext) and reads it the way the ATS does — no layout, no fonts, just text. Every top-10 keyword must appear in the extracted text; section headers must appear in order (Summary, Skills, Experience, Education); no garbled characters, merged words, or lost lines. A keyword missing from the raw text is a fail even if it renders fine visually.

ACRONYM RULE (added 2026-10-03): expand acronyms on first use so full-phrase matchers hit — write "service level indicators/objectives (SLIs/SLOs)" and "identity and access management (IAM)" on first use. Universally understood eng abbreviations (CI/CD, HPA/VPA, SAR/PerfMon) may stay abbreviated. EXCEPTION (user-set 2026-10-03): role names are NEVER abbreviated — always "Site Reliability Engineer", never "SRE"; always "Senior", never "Sr". This applies to the headline, summary, skills, and bullets.

#### Review B (hiring manager / director)
Output briefly: credibility (ownership and scope vs mere duties); impact (scale, cost, time, reliability visible?); fit and gaps (would I interview? what worries me?); summary check (who this person is and why they fit, in the first 3 lines); score out of 10.
IMPACT GATE (hard, 2026-09-30): every Experience bullet must carry ownership, scale, or a measurable outcome. A bullet that only lists duties ("responsible for X", "worked on Y") fails Review B regardless of keyword coverage, and the draft goes back for another pass. Acceptable scale/outcome carriers: systems or fleet size, request or data volume, users affected, hours or dollars saved, reliability deltas, deployment frequency, incident counts. Use only attested facts; never invent a number to satisfy this gate. If no attested number exists for a bullet, carry ownership or scope instead ("owned on-call for X", "led migration of Y").

#### Review C (staff / peer engineer — technical depth)
Output briefly: technical credibility (would the tooling and scale claims survive a technical screen?); depth vs breadth (reads like someone who operated these systems, or just listed them?); terminology accuracy (any misused terms a peer would catch?); buzzword check (any claim an engineer would read as fluff?); score out of 10.

#### Review D (executive skim — the 6-second test)
Output briefly: top-third test (title + summary + first two bullets — do I know who this person is and why they are strong within 6 seconds?); seniority signal (reads at the JD's level, not above or below?); one-line pitch (how I would pitch this candidate to the hiring manager in one sentence); score out of 10.

#### Review E (HR red-flag screen)
Output briefly: timeline check (gaps, overlaps, short stints — anything needing an explanation?); title-scope consistency (do the titles match what the bullets claim?); level fit (overqualified or underqualified signals for this JD?); verification risk (any claim that invites an uncomfortable background-check question?); verdict: pass or flag with the specific concern.

#### Review F (AI-voice / buzzword detector — added 2026-09-30)
One job: make sure no machine wrote this resume. Output briefly:
- Banned-word scan: check every word against the banned list in this skill; list each hit with its line and a plain replacement.
- AI-phrasing scan: em dashes, semicolons, smart quotes; "not only X but also Y"; triple parallelisms ("built, scaled, and optimized"); "furthermore / moreover / additionally"; "in today's fast-paced"; uniform bullet rhythm (every bullet the same length and structure); vague intensifiers ("very", "extremely", "highly", "significantly" without a number); hedged claims ("helped with", "assisted in", "involved in").
- Voice check: does it read like a human engineer wrote it? Flag any sentence that reads machine-generated, and rewrite it plain.
- Verdict: pass or fail with the specific flags; score out of 10. Any AI-sounding phrase, em dash, triple parallelism, or hedged fluff FAILS the application — the flagged lines must be rewritten in plain human writing before the resume ships or the form submits, no exceptions.

### Step 5: Draft 2 (one rewrite round)
Fix every issue from Reviews A–F. Same editable sections only.

### Step 6: Review G (company lens — what the company sees, added 2026-10-03)
Read the revised draft exactly as the hiring company sees it, not as the applicant's advocate. Output briefly:
- 10-second verdict: what the company concludes about fit, in one line.
- Requirement traceability: for each of the JD's top requirements, quote the exact resume line that proves it. Any requirement with no proving line is a gap — name it plainly.
- Interview triggers: the 2-3 lines most likely to make the company request an interview, and why.
- Company-side risks: anything that would make them pass — thin evidence on a must-have, title or scope mismatch, unexplained short stint, location or seniority doubts.
- Score out of 10. Anything below 10 sends the draft back for a targeted rewrite of the flagged lines.

10/10 BAR (hard, user-set 2026-09-30, rounds raised to 5 on 2026-10-03): the target is 10/10 from every reviewer. Any score below 10 triggers a targeted revision pass addressing that reviewer's notes, followed by a re-score of the affected review. Maximum 5 full rounds total. If any score is still below 10 after round 5, ship the best version and show the user the remaining gap and which reviewer withheld the 10.

### Step 7: Interview vote (final gate — added 2026-09-30)
All seven reviewers vote "interview" or "no interview", each with a one-line reason. ALL SEVEN must vote interview for the resume to ship. Any "no" triggers one targeted revision pass addressing that reviewer's objection, followed by a re-vote. If the vote still fails after 5 full rounds, ship the best version and show the user the dissenting reviewer's reason in the review summary.

### Step 8: Volume mode (behind the hourly or daily target — v2.8.3)
When the hour or day is behind target, use the lighter path instead of Steps 4–7: a 4-reviewer parallel pass (ATS, hiring manager, peer, AI-voice) + at most 1 rewrite round. Ship if the average score is >= 8.5 with no hard fails (any red flag, banned word, AI phrasing, invented fact, duty-only bullet, or failed layout MATCH). The company-lens review and interview vote still run. Volume mode trades rounds for speed — never for invented facts, AI voice, or a skipped layout check.

### Step 9: Deliver
1. Show the user a short review summary: all seven scores before and after, the interview vote, the computed ATS score (overall / Skills / Experience from `ats_score.py`), the Skills-only skills list, top 3 changes, and the "Confirm before applying" list.
2. Show the final resume.
3. Render the final one-page PDF/DOCX through the `~/workspace/resume-tailor/` pipeline, verify layout MATCH, place in the role folder, mirror to Drive. Save ONLY the final version. The packet folder must contain `ats_score.json` (the computed score) and `top10.json` (the JD top-10 skills list, with aliases), and `APPLICATION_FORM.md` must record the computed score plus the Skills-only skills list — a packet with no recorded score is incomplete.

## Self-check before saving
- Only the title, Summary, Skills, Experience differ from the base resume.
- No changed employers or dates; one title per employer; no invented numbers.
- Every addition listed under "Confirm before applying".
- 100% of must-haves appear in context, not as a keyword dump.
- `ats_score.py` ran on the final PDF and the gate passed (overall 10/10, or every missing skill recorded as a named honest gap); `ats_score.json` and `top10.json` are in the packet folder, and the Skills-only skills are listed in `APPLICATION_FORM.md`.
- Reads human: no banned words, no em dashes, no semicolons.
- Strong, varied verb openers; length at or under the base; one page; MATCH verified.
- All seven reviewers voted "interview". Any score below 10 or any dissent is shown to the user with the reason.
- Fast-apply path applied correctly: early exit only at 90%+ top-10 coverage with no red flags; volume mode only at average >= 8.5 with no hard fails and at most 1 rewrite round.
