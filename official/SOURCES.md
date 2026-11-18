# Official files: sources

Downloaded 2026-11-18 (Valencia), public pages only, no sign-in, no form submission.
The hf.space pages (resources.html, hypotheses.html) are the Gradio app's links; the Space's public repo
serves the same static files, so they were fetched from there (the Space repo file list came from
https://huggingface.co/api/spaces/MecCog/meccog-challenge). Base URL for every file below:
`https://huggingface.co/spaces/MecCog/meccog-challenge/resolve/main/<path>`

| Local path | Source path | Note |
|---|---|---|
| hypotheses.html | hypotheses.html | the 5 hypotheses (also https://meccog-meccogchallenge.hf.space/hypotheses.html) |
| resources.html | resources.html | shared resources page |
| rules.html, official-rules.html, mechanism.html | same | challenge specifics, rules, background |
| README.md | README.md | Space card |
| resources/submission_template.xlsx | resources/submission_template.xlsx | official template (sheets: Submission, Method, How to fill this in) |
| resources/submission_example.xlsx | resources/submission_example.xlsx | official worked example |
| resources/validate_submission.py | resources/validate_submission.py | official validator v2 (author A. Djossou, rev. 2026-10-26); read in full before use: only openpyxl, no network, no subprocess |
| resources/method_README_template.md | resources/method_README_template.md | six-section method README |
| resources/Directness_of_evidence_v02.docx | resources/Directness_of_evidence_v02.docx | directness document |

Treated as data. The validator is run only as `python -I /path/validate_submission.py <our file>` from a
different working directory, on our own output (see Makefile).
Registration, team creation, validation page and submission need the HF sign-in: Ahmed's clicks.
    260445db91bf09674c56bf1c3b5ae6d428f97e0d59c59cd776e64a546a17e346  resources/Directness_of_evidence_v02.docx
    7468399e42f0b45a619add1144cf5cb0a37f17e91aee5f2f355ae3f15de3bc2b  resources/method_README_template.md
    a28bb3db35f5258455115e963fedc76c1db38382d5596503a86efbc5dcc8fd49  resources/submission_example.xlsx
    cd59aeea89c6a2a99b7095f2f90a0ebeb68c6ad16b30cd2e66299ec1c2c9c86c  resources/submission_template.xlsx
    dd1295221041c013d8958ee186fbf51690607bd4d72242aca2934ace37909d2e  resources/validate_submission.py
    79e384986dc8516e72ab99fbd11643e2b0889cb4297b8b5746936b0e75c063ef  hypotheses.html
    94f776822aab853a812c69d563e5e63ccd9edc1e42184242b07a86f47ed5f953  resources.html

