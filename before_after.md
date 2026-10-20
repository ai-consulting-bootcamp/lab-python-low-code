# Before and after

Original: `original/meal_planner_starter.ipynb` · Refactored: `meal_planner_refactored.ipynb`

## What changed

| Area | Before (original) | After (refactored) |
|---|---|---|
| Main logic | `MealPlanGenerator.generate()`: 40 lines, 7 jobs | `create_meal_plan()`: 10 lines that call one-job functions in order; longest function is now `call_meal_plan_api` (28 lines, mostly its five `except` clauses) |
| Secrets | email address and password typed into the config cell | read from `.env` (listed in `.gitignore`); the notebook only prints set / MISSING |
| Missing API key | `TypeError: str expected, not NoneType` in the env cell | `call_meal_plan_api()` says the key is not set and how to add it |
| API call | outside `try`: a wrong key or no network crashes the app | inside `try`, with separate handling for authentication, rate limit, timeout, connection and other API errors |
| Error messages | `str(e)`: what broke, never where | `make_error()`: function, error type, message, location, suggestion |
| Result shape | success has 4 keys, failure has 3 | always the same 4 keys (`make_result()`) |
| Email button | generates a new plan (second paid call, different recipes) | sends the plan on screen (`gr.State`), no extra call |
| Validation rules | Pydantic models plus `run_basic_validation()` repeating them, with 7 and 5 typed again | Pydantic models only, counts from constants |
| Repeated code | ingredient line x2, textbox defaults x3 (two different defaults, crash on `None`), fragile fence split | `format_ingredients()`, `text_or_default()`, `extract_json_text()` |
| Dead code | shopping prompt and parser, `EXCLUDED_BASICS`, `DAYS`, `DietaryPreference`, `Optional`, two unused packages | removed, or now used |
| Input and tests | inline `TEST_CASES`, 4 paid calls per run, no file to break | `data/meal_requests.json`, `malformed.json`, `invalid_requests.json`; offline tests; 2 clearly marked paid calls |
| App launch | `share=True` public link | local only |
| Kept the same on purpose | | prompt text sent to the model, email text, UI layout, 7 x 5 plan structure (checked in Step 6 of the notebook) |

## Same broken input, before and after

The "before" text is what the original code returns for that input (captured by running it); the "after" text comes from the refactored functions.

**The model answers `{"recipes": [}`**

Before:
```
JSON parsing error: Expecting value: line 1 column 14 (char 13)
```
After:
```
ERROR in parse_json_text()
  Type:       JSONDecodeError
  Message:    Expecting value: line 1 column 14 (char 13)
  Location:   model output, line 1, column 14, near '{"recipes": [}'
  Suggestion: The model sent broken JSON: click Generate again.
```

**The model returns 6 recipes**

Before:
```
1 validation error for MealPlan
recipes
  Value error, Meal plan must have exactly 7 recipes, got 6 [type=value_error, input_value=[{'day': 'Monday', 'theme... everything together.'}], input_type=list]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
```
After:
```
ERROR in validate_data()
  Type:       ValidationError
  Message:    1 invalid field(s)
              - recipes: Value error, Meal plan must have exactly 7 recipes, got 6
  Location:   model output (checked against MealPlan)
  Suggestion: The model broke a meal-plan rule (7 recipes, 5 ingredients each, unique themes): click Generate again.
```

**No `.env` file**

Before:
```
TypeError: str expected, not NoneType
```
After:
```
ERROR in call_meal_plan_api()
  Type:       ValueError
  Message:    OPENAI_API_KEY is not set
  Location:   .env file next to this notebook
  Suggestion: Copy .env.example to .env and paste your OpenAI API key.
```

The messages for a missing input file, a malformed file, invalid requests, a wrong API key and a network failure are in section 6 of `lab_proof.md`, filled from the notebook run.
