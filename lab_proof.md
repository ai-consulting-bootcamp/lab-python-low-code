# Lab Proof: Meal Planner Refactoring

## Scope and workflow

I followed Path 2 using the instructor-provided Meal Planner starter notebook. The generic product-generator examples were adapted to meal-plan requests and validation.

The workflow is:

**Request → normalization → API invocation → JSON parsing → Pydantic validation → output**

The refactored implementation is in [meal_planner_refactored.ipynb](meal_planner_refactored.ipynb). The original is preserved in [meal_planner_starter.ipynb](meal_planner_starter.ipynb).

Configuration is loaded from environment variables. [.env.example](.env.example) documents the credential variable names without secret values.

## Successful final live run

The final run used the refactored generation flow and a real API request. Its input, validated output, and timestamped execution trace are saved separately from the original baseline.

- [Input payload](evidence/refactored_input.json)
- [Execution trace](evidence/execution_trace.txt)
- [Validated output record](evidence/refactored_output.json)
- [Successful execution screenshot](evidence/02_refactored_success.png)

The corresponding notebook cell is identified by:

`# Final live run: input, execution trace, and matching output.`

The trace records a run identifier, the configured model, generation status, schema-validation status, and output destination. The output passed the schema checks for recipe count, ingredient count, and unique themes.

## Input-to-output mapping

The request fields `dietary_preference`, `theme_requests`, and `additional_preferences` are normalized and passed to the generation chain. The model response is parsed as JSON and validated against `MealPlan`.

The validated output contains `dietary_preference`, `recipes`, and `shopping_list`. Formatting functions prepare the plan for display and email.

The email callback receives the displayed plan through Gradio session state rather than generating another plan.

## Baseline and comparison

The original successful baseline is preserved in:

- [Baseline input](evidence/baseline_input.json)
- [Baseline output](evidence/baseline_output.json)
- [Baseline screenshot](evidence/01_baseline_success.png)

The [refactoring checklist](docs/refactoring_checklist.md) records the original problems, implemented changes, and verification plans.

The final workflow preserves the meal-plan output contract while separating responsibilities, improving error messages, and preventing email-triggered regeneration. Since model generation is nondeterministic, baseline and final dishes are not expected to match word for word.

## Error-handling evidence

Saved test outputs in the refactored notebook demonstrate:

- Missing API-key configuration.
- Simulated authentication, rate-limit, timeout, connection, and server errors.
- Malformed response JSON and invalid meal-plan data.
- Missing input files, malformed JSON files, and invalid request data.
- Missing email configuration and simulated SMTP failures.
- Offline Generate-to-Email forwarding without another generation call.

File-based tests use:

- [Valid requests](tests/fixtures/test_cases.json)
- [Malformed JSON](tests/fixtures/malformed.json)
- [Invalid requests](tests/fixtures/invalid_requests.json)

`tests/fixtures/missing_test_cases.json` is intentionally absent. Tests verify that its absence produces a helpful error identifying the file path.

The notebook tests exercise the actual loading, parsing, validation, and callback paths. API and SMTP failure tests use mocks; they do not demonstrate real service failures or actual email delivery.

## Operational risk and limitations

The first failure I would monitor in daily operation is unsuccessful API generation or an invalid response. Generation returns a structured failure, and the UI clears the plan state when a new generation starts so that a failed attempt does not leave an old plan available for email.

The final successful generation was live. Email delivery was tested with mocked SMTP, and browser-session isolation and concurrent interactions were not demonstrated. Schema validation checks structure and selected rules; it does not independently prove dietary suitability or shopping-list accuracy.

## Reflection

See [lab_summary.md](lab_summary.md) for the short learning summary.
