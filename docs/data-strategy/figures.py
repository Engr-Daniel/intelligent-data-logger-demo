"""Figures for the Intelligent Data Logger data strategy, built with blueprint-visualise.

The brand-locked figure library is part of the Petgrave.io(TM) Blueprint skills and
is not copied into this repository. Point BLUEPRINT_VISUALS at its scripts folder:

    BLUEPRINT_VISUALS=/path/to/petgrave-data-strategy/skills/blueprint-visualise/scripts \
        python docs/data-strategy/figures.py

Writes editions/petgrave-idl/figures/*.png and editions/system-owner/figures/*.png.
Every number comes from evidence-register.md; synthetic results are labelled as such.
"""
import os
import sys

sys.path.insert(0, os.environ.get("BLUEPRINT_VISUALS", ""))
import blueprint_visuals as bv  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
IDL = os.path.join(HERE, "editions/petgrave-idl/figures")
OWN = os.path.join(HERE, "editions/system-owner/figures")
os.makedirs(IDL, exist_ok=True)
os.makedirs(OWN, exist_ok=True)


def bars(rows, path, unit, note, focus=0, height=None):
    """Aligned horizontal bars, direct-labelled, brand monochrome. rows: [(label, value, value_text)]."""
    h = height or 0.5 + 0.42 * len(rows)
    fig = plt.figure(figsize=(bv.W, h), dpi=bv.DPI)
    ax = fig.add_axes([0.36, 0.22 if note else 0.08, 0.5, 0.74 if note else 0.88])
    vmax = max(v for _, v, _ in rows)
    for i, (label, v, txt) in enumerate(rows):
        y = len(rows) - 1 - i
        solid = i == focus
        ax.barh(y, v, height=0.56, color=bv.NAVY if solid else bv.ASH, edgecolor=bv.NAVY if solid else bv.ASH)
        ax.text(v + vmax * 0.02, y, txt, va="center", ha="left", fontsize=8,
                color=bv.INK if solid else bv.GREY, weight="bold" if solid else "normal")
        ax.text(-vmax * 0.03, y, label, va="center", ha="right", fontsize=8,
                color=bv.INK if solid else bv.GREY, weight="bold" if solid else "normal")
    ax.set_xlim(0, vmax * 1.25)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.axis("off")
    if note:
        fig.text(0.02, 0.05, note, fontsize=7, color=bv.GREY, ha="left", va="bottom", wrap=True)
    fig.savefig(path, dpi=bv.DPI, facecolor="white")
    plt.close(fig)


# ---------------- Petgrave.io IDL edition ----------------
# The core evidence: history across components matters (C04; n = 240 identifiable cases per condition).
bars([
    ("Full history + all components", 97.1, "97.1%  (233 of 240)"),
    ("Full history + inverter only", 53.8, "53.8%"),
    ("Last 24 h + all components", 40.0, "40.0%"),
    ("Last 24 h + inverter only", 20.0, "20.0%"),
], os.path.join(IDL, "access.png"), "%",
    note="Correct diagnoses on identifiable clean cases, same diagnostic policy. Synthetic: 24 installations, 240 cases per condition.")

# Where the flow from a real installation to a checked answer breaks (Stage 4, provisional).
bv.strength_strip([
    ("Capture", "dashed", "No real route yet; most systems have no monitoring"),
    ("Store", "solid", "Versioned schema and store"),
    ("Prepare", "ash", "Validation works; no real inverter mapped"),
    ("Analyse", "solid", "Deterministic tools; ROI assumes grid only"),
    ("Visualise", "ash", "Receipts work; strict replies 0 of 24"),
    ("Act", "dashed", "No route from an answer to an action"),
    ("Learn", "dashed", "Nobody records what the installer found"),
], os.path.join(IDL, "lifecycle.png"))

# Maturity on real-data operation (Stage 3).
bv.maturity_matrix([
    ("People & Culture", 2, 3),
    ("Processes", 1, 2),
    ("Technology", 2, 3),
    ("Governance", 2, 3),
    ("Strategy & Impact", 1, 2),
], os.path.join(IDL, "maturity.png"), constraint="Processes")

# Verdicts (Stage 5 screen).
bv.verdict_lanes([
    ("Proceed", "solid", [
        "Record what installers find on call-backs",
        "Measure what solar replaced: grid or generator",
        "Structured replies and a citation check",
        "A 3-site pilot on data that already exists",
    ]),
    ("Reshape", "ash", [
        "Read Suny's meter readings: ask Fitzroy; consent first",
    ]),
    ("Not now", "dashed", [
        "Our own edge hardware",
        "A validation paper (needs 30+ checked diagnoses)",
        "Mini-grids, wind, buildings",
        "AI forecasting · carbon credits",
    ]),
    ("Stop", "dashed", [
        "The AI taking actions by itself",
    ]),
], os.path.join(IDL, "verdicts.png"))

# The next 90 days.
bv.swimlane(
    ["Daniel", "Fitzroy", "Installers"],
    ["This week", "November", "December", "January"],
    [
        ("Daniel", "This week", "Present at NASEF, 21 Oct", "solid"),
        ("Daniel", "November", "Fix ROI/carbon counterfactual; structured replies", "outline"),
        ("Daniel", "December", "Pilot month 1: weekly readings, statements", "outline"),
        ("Daniel", "January", "First field check: M01 counts", "dashed"),
        ("Fitzroy", "November", "Agree M01; consent terms; Suny data?", "outline"),
        ("Fitzroy", "January", "Teach the Blueprint with this case", "dashed"),
        ("Installers", "November", "Answer the question pack", "outline"),
        ("Installers", "December", "Log findings on each visit", "outline"),
    ],
    os.path.join(IDL, "plan.png"))

# ---------------- System-owner edition ----------------
# The monthly report, as it was done by hand (Stage 4; one reported case).
bv.strength_strip([
    ("Capture", "dashed", "Read by hand, when someone remembers"),
    ("Store", "ash", "Notebook, then a spreadsheet"),
    ("Prepare", "dashed", "Re-typing and fixing missing days"),
    ("Analyse", "ash", "ROI and solar share worked out by hand"),
    ("Visualise", "ash", "A monthly report, at best"),
    ("Act", "dashed", "After the failure, not before"),
    ("Learn", "dashed", "Rarely"),
], os.path.join(OWN, "logbook.png"))

# What the system is worth depends on what it replaced (C09; synthetic 120 days, same 1,851 kWh).
bars([
    ("If solar replaced a petrol generator", 0.9, "0.9 years (upper bound)"),
    ("If solar replaced the grid", 5.1, "5.1 years (today's model)"),
], os.path.join(OWN, "payback.png"), "years", focus=0,
    note="Simple payback on a ₦6.5m system from 120 synthetic days. Petrol: 0.8 L/kWh at ₦1,596.25/L. Grid: ₦225/kWh (demo value). The truth lies between.")

bars([
    ("If solar replaced a petrol generator", 3481, "3,481 kg CO₂"),
    ("If solar replaced the grid", 883, "883 kg CO₂"),
], os.path.join(OWN, "carbon.png"), "kg", focus=0,
    note="CO₂ avoided in the same 120 synthetic days. Petrol 2.35 kg/L (US EPA); Nigerian grid 0.477 kg/kWh (IFI harmonised factor).")

# The questions an owner can ask, grouped by the decision they serve (Stage 2).
bv.card_groups([
    ("Is it working?", [
        ("Made vs. what the sun allowed", "Call the installer, or wait"),
        ("Is the battery getting weaker?", "Replace it before it fails"),
        ("How long can we run tonight?", "Shed load or start the generator"),
    ]),
    ("What is it worth?", [
        ("Money saved, split by grid and generator", "Budget; whether to expand"),
        ("Fuel we did not buy", "Fuel purchasing"),
    ]),
    ("What did it avoid?", [
        ("How much power came from solar", "Shift loads to midday"),
        ("CO₂ avoided, with its assumptions", "The sustainability report"),
    ]),
], os.path.join(OWN, "questions.png"), focus=(1, 0))

bv.maturity_matrix([
    ("People & Culture", 2, 3),
    ("Processes", 1, 2),
    ("Technology", 1, 2),
    ("Governance", 1, 2),
    ("Strategy & Impact", 1, 2),
], os.path.join(OWN, "maturity.png"), constraint="Processes")

print("figures written to", IDL, "and", OWN)
