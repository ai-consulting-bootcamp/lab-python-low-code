# Meal Planner — Refactoring Lab Proof

Path: 2 — Refactor Provided Starter Code  
Project: Weekly Themed Meal Planner MVP

## Workflow and input

- Trigger: Run the meal-plan generator with user preferences.
- Input payload: `{"dietary_preference": "vegetarian", "theme_requests": "Italian, Mexican", "additional_preferences": "no mushrooms"}`
- Transformation: Prepare the prompt inputs, call the OpenAI model, parse its JSON response, and validate the meal plan with Pydantic.
- Output record: A successful result containing seven recipes, a shopping list, and a validation result of `{"passed": true, "errors": []}`.

## Before and after

Before: The original `generate()` method combined prompt preparation, the API request, JSON parsing, and validation. The API request occurred outside its `try` block. The email button generated a new plan instead of using the one already displayed.

After: The code uses focused helpers such as `build_inputs()`, `request_plan()`, `parse_json_response()`, `validate_meal_plan()`, and `error_result()`. It returns informative errors with the failing stage and uses the saved plan when preparing an email. API and email failures are not silently ignored.

## Test evidence

| Test | Observed result | Evidence |
|---|---|---|
| Original program, real API | `Success: True`; 7 recipes; validation passed | [Baseline screenshot](evidence/baseline_success.jpg) |
| Valid JSON and Pydantic schema | PASS (offline) | [Offline test screenshot](evidence/offline_tests.jpg) |
| Invalid JSON | PASS: JSON parsing error identified | [Offline test screenshot](evidence/offline_tests.jpg) |
| Invalid recipe data | PASS: six recipes rejected by validation | [Offline test screenshot](evidence/offline_tests.jpg) |
| Missing file | PASS: file path and error identified | [Offline test screenshot](evidence/offline_tests.jpg) |
| Malformed JSON file | PASS: line and column reported | [Offline test screenshot](evidence/offline_tests.jpg) |
| API error | PASS: simulated API failure reported with stage | [Offline test screenshot](evidence/offline_tests.jpg) |
| Refactored program, real API | `Success: True`; 7 recipes; validation passed | [Refactored screenshot](evidence/refactored_success.jpg) |

**Verification note:** The API-error test used a mock; it was not an actual API outage. Real API calls succeeded before and after refactoring. The email-sending feature was not tested against a live SMTP server.

## Operational risk

The model might return malformed JSON or an unavailable API might prevent meal-plan generation. The refactored code reports these failures rather than silently producing incorrect output; monitoring and retry policies would still be needed for production use.