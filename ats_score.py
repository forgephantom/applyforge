#!/usr/bin/env python3
"""Computed ATS score for a tailored resume against a JD's top-10 skills.

This replaces reviewer-judged "match %" with a measured number. The 2026-11-19
ATS/decline review found the pipeline could not prove its own coverage claims:
no computed score existed anywhere, and the loop's "match %" was a number a
reviewing agent wrote. This script is the measurement.

Usage:
    python3 ats_score.py --jd JD.md --pdf Resume.pdf --skills top10.json [--out ats_score.json]

Inputs:
    --jd      Job description text or Markdown. Used for a sanity check that
              each listed skill actually appears in the JD.
    --pdf     Built one-page resume PDF. Text is extracted with `pdftotext`
              (poppler-utils), the same plain-text view an ATS parser sees.
    --skills  JSON file: the JD's top-10 skills, in the JD's exact wording.
              A list of strings, or objects with aliases:
                  ["Capacity planning", {"name": "BigQuery / SQL",
                   "aliases": ["BigQuery", "SQL"]}]
              An object may also carry "omission_reason" to exclude the
              skill from scoring (see Gate, below):
                  {"name": "OpenCode AI",
                   "omission_reason": "Employer-internal tool; no honest
                    experience available"}
              The skills file is the human-readable override list for the
              packet: the agent extracts the top 10 from the JD first, then
              this script verifies presence. Keep the file in the packet.
    --out     Optional path to write the score JSON (required by the review
              loop: the JSON goes in the packet folder as ats_score.json).

What it computes (three numbers, all x/10):
    overall     skill appears anywhere in the extracted resume text
    skills      skill appears in the Skills section
    experience  skill appears in an Experience bullet (in context)

Matching: case-insensitive exact-phrase match with word boundaries, an
optional plural "s" on the final word, and hyphen-insensitive matching
(pdftotext drops the hyphen on wrapped words, e.g. "singlecommand").
Aliases and the SYNONYMS map below count as the skill.

Gate (see skills/jd-resume-review-loop/SKILL.md):
    exit 0  overall AND Experience are 10/10 on every scored skill — the
            submission gate passes. Work history must match skills at
            100%, not just the Skills list.
    exit 1  overall or Experience is below 10/10 on the scored skills —
            the gate FAILS. First rewrite bullets to surface real
            experience the candidate has; never fabricate a skill into
            a bullet.
    Honest omissions: a top-10 skill with genuinely no honest Experience
    evidence may be excluded from scoring, but ONLY with a documented
    reason, as a top10.json entry carrying "omission_reason" (see above).
    Omitted skills are excluded from both denominators and listed with
    their reasons in the score JSON; they must also be recorded in the
    packet's APPLICATION_FORM.md. Omitted skills are never silent, and
    an omission without a non-empty reason is an error (exit 2).
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date

# Stem/synonym map: canonical term -> equivalent terms that count as a match.
# Both directions apply: matching "Kubernetes" also tries "K8s" and vice versa.
# Keep this list short and unambiguous; anything debatable belongs in the
# per-packet skills file as an explicit alias, not here.
SYNONYMS = {
    "kubernetes": ["k8s"],
    "k8s": ["kubernetes"],
    "amazon web services": ["aws"],
    "aws": ["amazon web services"],
    "google cloud platform": ["gcp"],
    "gcp": ["google cloud platform"],
    "microsoft azure": ["azure"],
    "azure": ["microsoft azure"],
    "continuous integration": ["ci"],
    "continuous delivery": ["cd"],
    "ci/cd": ["ci cd", "continuous integration", "continuous delivery"],
    "service level indicators": ["slis"],
    "service level objectives": ["slos"],
    "identity and access management": ["iam"],
    "iam": ["identity and access management"],
    "site reliability engineer": ["sre"],
    "sre": ["site reliability engineer"],
    "machine learning": ["ml"],
    "ml": ["machine learning"],
    "artificial intelligence": ["ai"],
    "ai": ["artificial intelligence"],
    "sql": ["structured query language"],
    "terraform": ["iac"],
    "infrastructure as code": ["iac"],
    "on-call": ["oncall", "on call"],
    "oncall": ["on-call", "on call"],
    "root cause analysis": ["rca"],
    "rca": ["root cause analysis"],
    "disaster recovery": ["dr"],
    "high availability": ["ha"],
}

# Section headers, in the order they appear on the one-page resume.
# Each entry: (canonical name, header variants as they appear in pdftotext).
SECTIONS = [
    ("summary", ["SUMMARY"]),
    ("skills", ["TECHNICAL SKILLS", "SKILLS"]),
    ("experience", ["PROFESSIONAL EXPERIENCE", "EXPERIENCE", "WORK EXPERIENCE"]),
    ("education", ["CERTIFICATIONS & EDUCATION", "EDUCATION", "CERTIFICATIONS"]),
]


def normalize(text):
    """Lowercase, collapse whitespace, normalize punctuation for matching."""
    text = text.lower()
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def phrase_pattern(phrase):
    """Regex for a phrase: word boundaries, flexible whitespace, optional
    plural 's' on the final word, hyphens matched as hyphen-or-space."""
    words = normalize(phrase).split(" ")
    parts = []
    for i, w in enumerate(words):
        w = re.escape(w)
        # A hyphen inside a word matches a hyphen or a space ("on-call" ==
        # "on call"); a trailing hyphen artifact is handled by the
        # de-hyphenated text variant in match_in().
        w = w.replace(r"\-", r"[-\s]")
        if i == len(words) - 1 and not w.endswith("s"):
            w += "s?"
        parts.append(w)
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b")


def match_in(phrase, text, text_no_hyphen):
    """True if phrase matches text, in either hyphen form."""
    pat = phrase_pattern(phrase)
    if pat.search(text):
        return True
    # pdftotext drops the hyphen on line-wrapped words ("single-command"
    # becomes "singlecommand"); retry against hyphen-stripped text with the
    # hyphen also stripped from the phrase.
    pat2 = phrase_pattern(phrase.replace("-", ""))
    return bool(pat2.search(text_no_hyphen))


def expand_terms(skill):
    """All matchable terms for a skill: name + aliases + synonyms."""
    if isinstance(skill, str):
        name, aliases = skill, []
    else:
        name, aliases = skill["name"], skill.get("aliases", [])
    terms = [name] + list(aliases)
    for term in list(terms):
        terms += SYNONYMS.get(normalize(term), [])
    # Deduplicate, preserving order.
    seen, out = set(), []
    for t in terms:
        if normalize(t) not in seen:
            seen.add(normalize(t))
            out.append(t)
    return name, out


def extract_pdf_text(pdf_path):
    try:
        proc = subprocess.run(
            ["pdftotext", pdf_path, "-"],
            capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError:
        print("ERROR: pdftotext not found (install poppler-utils).", file=sys.stderr)
        sys.exit(2)
    if proc.returncode != 0:
        print(f"ERROR: pdftotext failed on {pdf_path}: {proc.stderr.strip()}",
              file=sys.stderr)
        sys.exit(2)
    return proc.stdout


def split_sections(text):
    """Split extracted resume text into sections by header line.

    Returns a dict of canonical section name -> section text. Raises
    ValueError if the Skills or Experience header cannot be found, since
    the section scores are meaningless without them.
    """
    lines = text.splitlines()
    found = []  # (line index, canonical name)
    for i, line in enumerate(lines):
        stripped = line.strip()
        for name, variants in SECTIONS:
            if stripped.upper() in variants:
                found.append((i, name))
                break
    found.sort()
    sections = {}
    for j, (line_idx, name) in enumerate(found):
        end = found[j + 1][0] if j + 1 < len(found) else len(lines)
        sections[name] = "\n".join(lines[line_idx + 1:end])
    missing = [n for n in ("skills", "experience") if n not in sections]
    if missing:
        raise ValueError(
            "Could not find section header(s) in PDF text: "
            + ", ".join(missing)
            + ". Expected headers like TECHNICAL SKILLS and "
            "PROFESSIONAL EXPERIENCE."
        )
    return sections


def score(jd_text, resume_text, sections, skills):
    jd_norm = normalize(jd_text)
    jd_no_hyphen = jd_norm.replace("-", "")
    full_norm = normalize(resume_text)
    full_no_hyphen = full_norm.replace("-", "")
    skills_norm = normalize(sections["skills"])
    skills_no_hyphen = skills_norm.replace("-", "")
    exp_norm = normalize(sections["experience"])
    exp_no_hyphen = exp_norm.replace("-", "")

    per_skill = []
    for skill in skills:
        name, terms = expand_terms(skill)
        matched_term = None
        in_overall = in_skills = in_exp = False
        for term in terms:
            if match_in(term, full_norm, full_no_hyphen):
                in_overall = True
                matched_term = matched_term or term
            if match_in(term, skills_norm, skills_no_hyphen):
                in_skills = True
                matched_term = matched_term or term
            if match_in(term, exp_norm, exp_no_hyphen):
                in_exp = True
                matched_term = matched_term or term
        in_jd = any(match_in(t, jd_norm, jd_no_hyphen) for t in terms)
        per_skill.append({
            "skill": name,
            "matched_term": matched_term,
            "in_jd": in_jd,
            "overall": in_overall,
            "skills_section": in_skills,
            "experience": in_exp,
            "skills_only": in_skills and not in_exp,
        })
    return per_skill


def main():
    parser = argparse.ArgumentParser(
        description="Computed ATS score: JD top-10 skills vs resume PDF.")
    parser.add_argument("--jd", required=True, help="Job description file (text/Markdown)")
    parser.add_argument("--pdf", required=True, help="Built resume PDF")
    parser.add_argument("--skills", required=True,
                        help="JSON file with the JD top-10 skills list")
    parser.add_argument("--out", help="Write score JSON to this path")
    args = parser.parse_args()

    with open(args.jd, encoding="utf-8") as f:
        jd_text = f.read()
    with open(args.skills, encoding="utf-8") as f:
        skills = json.load(f)
    if not isinstance(skills, list) or not skills:
        print("ERROR: skills file must be a non-empty JSON list.", file=sys.stderr)
        sys.exit(2)
    if len(skills) != 10:
        print(f"WARNING: skills list has {len(skills)} entries, expected 10 "
              "(the JD top 10). Scoring against the list as given.",
              file=sys.stderr)

    # Split out honest omissions: excluded from scoring, never silent.
    scored, omissions = [], []
    for entry in skills:
        if isinstance(entry, dict) and "omission_reason" in entry:
            name = entry.get("name")
            reason = entry.get("omission_reason")
            if not name:
                print("ERROR: an omitted skill has no \"name\".",
                      file=sys.stderr)
                sys.exit(2)
            if not isinstance(reason, str) or not reason.strip():
                print(f"ERROR: omitted skill {name!r} has an "
                      "omission_reason that is missing or empty. An "
                      "omission needs a documented reason.",
                      file=sys.stderr)
                sys.exit(2)
            omissions.append({"skill": name,
                              "omission_reason": reason.strip()})
        else:
            scored.append(entry)
    if not scored:
        print("ERROR: every listed skill is omitted; nothing left to score.",
              file=sys.stderr)
        sys.exit(2)

    resume_text = extract_pdf_text(args.pdf)
    try:
        sections = split_sections(resume_text)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    per_skill = score(jd_text, resume_text, sections, scored)
    total = len(per_skill)
    n_overall = sum(1 for s in per_skill if s["overall"])
    n_skills = sum(1 for s in per_skill if s["skills_section"])
    n_exp = sum(1 for s in per_skill if s["experience"])
    missing = [s["skill"] for s in per_skill if not s["overall"]]
    skills_only = [s["skill"] for s in per_skill if s["skills_only"]]
    not_in_jd = [s["skill"] for s in per_skill if not s["in_jd"]]

    result = {
        "jd": args.jd,
        "pdf": args.pdf,
        "date": date.today().isoformat(),
        "total_skills": len(skills),
        "scored_skills": total,
        "omissions": omissions,
        "overall": {"matched": n_overall, "total": total},
        "skills_section": {"matched": n_skills, "total": total},
        "experience": {"matched": n_exp, "total": total},
        "missing_overall": missing,
        "skills_only": skills_only,
        "not_in_jd": not_in_jd,
        "per_skill": per_skill,
    }
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    # Human-readable report.
    print(f"ATS score: {args.pdf} vs {args.jd}")
    print(f"  Overall (anywhere in resume): {n_overall}/{total}")
    print(f"  Skills section:               {n_skills}/{total}")
    print(f"  Experience bullets:           {n_exp}/{total}")
    for s in per_skill:
        mark = lambda b: "Y" if b else "-"
        print(f"    [{mark(s['overall'])}{mark(s['skills_section'])}"
              f"{mark(s['experience'])}] {s['skill']}"
              + (f"  (matched: {s['matched_term']})"
                 if s["matched_term"] and s["matched_term"] != s["skill"] else ""))
    print("  (columns: Overall / Skills / Experience)")
    if omissions:
        for o in omissions:
            print(f"  OMITTED (documented, excluded from scoring): "
                  f"{o['skill']} — {o['omission_reason']}")
    if missing:
        print(f"  MISSING overall: {', '.join(missing)}")
    if skills_only:
        print(f"  SKILLS-ONLY (no Experience evidence): {', '.join(skills_only)}")
    if not_in_jd:
        print(f"  WARNING: listed skill(s) not found in the JD text: "
              f"{', '.join(not_in_jd)}")
    if n_overall < total or n_exp < total:
        failed = []
        if n_overall < total:
            failed.append(f"overall {n_overall}/{total}")
        if n_exp < total:
            failed.append(f"Experience {n_exp}/{total}")
        print(f"  GATE FAILED: {' and '.join(failed)} < {total}/{total}. "
              "First rewrite bullets to surface real experience; a skill "
              "with genuinely no honest Experience evidence is recorded "
              "as an honest omission with a reason — never fabricated "
              "into a bullet.")
        sys.exit(1)
    omitted_note = (f" ({len(omissions)} documented omission(s))"
                    if omissions else "")
    print(f"  GATE PASSED: overall and Experience {total}/{total} on all "
          f"scored skills{omitted_note}.")
    sys.exit(0)


if __name__ == "__main__":
    main()
