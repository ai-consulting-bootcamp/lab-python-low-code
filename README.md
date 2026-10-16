# From hacky script to "we could ship this"

**Track:** Module 2 — Python low-code · **When:** Week 3, Day 1 · **Status:** Required

This repository contains everything you need for this lab.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.

## Run the listing generator

Install dependencies with `pip install -r requirements.txt` and set `OPENAI_API_KEY`
in your environment or a local `.env` file. Keep that file out of version control.

```powershell
# Validate all input products without API calls
python product_generator.py --validate-only

# Generate one listing (uses the API)
python product_generator.py products.json --limit 1

# Generate listings using the configured batch size (default: 5)
python product_generator.py
```

`product_generator.py` coordinates the workflow. `listing_generator/files.py` loads
and validates JSON and saves results; `generator.py` calls the API and processes
batches. These use the shared `config.py`, `models.py`, `prompts.py`, `images.py`
and `errors.py` modules. The default input is `products.json`; images are optional
for the internal Product model, so the sample JSON uses text-only generation.
Outputs are `output/listings.json`, `output/listings.csv`, and `output/errors.csv`.
Each run replaces these files. `LISTING_NUM_PRODUCTS`, `LISTING_MODEL` and
`LISTING_OUTPUT_DIR` can override the defaults through environment variables.
The original script is preserved in `legacy/product_generator_before.py`.
