# Candidate Objects

This folder contains a short list of objects flagged as "interesting" for follow-up.
The source is a coordinate table you assembled from your exploration.

Files:
- `table_of_coordinates.pdf` original table as a PDF
- `interesting_objects.csv` best-effort extracted table for search and filtering
- `SUMMARY.md` auto-generated quick summary and flags

## What can be said from this list

Each row includes at least:
- `object_id` internal identifier
- `ra_deg`, `dec_deg` sky position
- `neowise_class` a coarse class label (for example `ClassII`, `FS`, `Linear`)
- `raw_text` the full block from the PDF (kept so no context is lost)

The PDF also includes context such as:
- a SIMBAD match and separation in arcseconds
- a SIMBAD object type label
- a short ZTF behavior label (for example periodic on long timescales, transient brightening, irregular variability)

Because the PDF wraps columns across lines, `interesting_objects.csv` is intentionally conservative and does not attempt to perfectly parse every field. The raw text is included so you can interpret each entry.

## Why these are worth looking at

This list is useful because it focuses attention on a small number of targets that appear unusual in at least one of:
- morphology versus amplitude behavior
- long-timescale periodicity candidates
- transient-like events (sudden brightening)
- objects with ambiguous or surprising SIMBAD types relative to YSO expectations

Follow-up value:
- verifies whether the variability is astrophysical versus an artifact
- identifies misclassifications (for example LPVs or PNe contaminating a YSO list)
- highlights high-value targets for deeper time-domain or spectroscopic follow-up

## Recommended next steps

1. Crossmatch and sanity checks
- confirm SIMBAD match separation is small for the preferred counterpart
- crossmatch with Gaia DR3 for parallax and proper motion consistency with star-forming regions

2. Light curve inspection
- pull NEOWISE W1 and W2 light curves for each target
- pull ZTF light curves and check that the label matches the data

3. Prioritize follow-up targets
- transient-like behavior and high-amplitude irregulars first
- objects with suspicious SIMBAD types (for example PN) for contamination analysis

## How to regenerate the CSV

Run:
- `python3 tools/extract_coordinates_pdf.py`

To regenerate the summary:
- `python3 tools/summarize_candidates.py`
