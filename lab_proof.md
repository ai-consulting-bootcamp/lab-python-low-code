# Lab proof: Weekly Meal Planner refactor (Path 1)

**Reviewer entry point.** One workflow path: one meal-plan request (input file) goes through one transformation (OpenAI + validation) into one saved output record. Sections 1 to 6 contain evidence that the last cells of `meal_planner_refactored.ipynb` fill in from a real run; re-running the notebook refreshes them.

| What | Where |
|---|---|
| Refactored code | `meal_planner_refactored.ipynb` (one section per lab step) |
| Original code, unchanged | `original/meal_planner_starter.ipynb` |
| Input file | `data/meal_requests.json` (the original 4 test cases, now a file) |
| Broken inputs for the error tests | `data/malformed.json`, `data/invalid_requests.json`, a missing file |
| Output record (destination) | `output/meal_plan_record.json` |
| Baseline run of the original code | `output/baseline_original.json` |
| Before/after comparison | `before_after.md` |
| Summary paragraph | `lab_summary.md` |

## 1. Workflow configuration

`INPUT -> DECIDE -> BUILD (trigger -> transform -> action) -> VERIFY`

| Stage | Function(s) | What happens |
|---|---|---|
| Trigger | `run_workflow(REQUESTS_FILE, PROOF_REQUEST)` | starts one run (the app's Generate button uses the same core, `create_meal_plan`) |
| Input | `load_json_file` | reads `data/meal_requests.json` |
| Decide | `validate_data(RequestFile)` | required field: `dietary_preference` (omnivore, vegetarian, vegan, keto). Optional text: `theme_requests`, `additional_preferences` (blank or missing becomes "random diverse cuisines" / "none"). **Routing rule:** an invalid file or request stops here, before the paid API call |
| Transform | `call_meal_plan_api` -> `extract_json_text` -> `parse_json_text` -> `validate_data(MealPlan)` | the request fills the prompt, OpenAI answers, the answer must be JSON with 7 recipes, 5 ingredients each and 7 different themes |
| Action | `save_json_file` | writes input + plan + run facts to `output/meal_plan_record.json` |

Run settings (filled from the notebook constants; the API key is never written out):

<!-- config:start -->
```json
{
  "input_file": "data/meal_requests.json",
  "request_number": 2,
  "output_file": "output/meal_plan_record.json",
  "model": "gpt-4o-mini",
  "temperature": 0.7,
  "timeout_seconds": 60,
  "max_retries": 2,
  "recipes_per_plan": 7,
  "ingredients_per_recipe": 5,
  "api_key": "read from .env, never written out"
}
```
<!-- config:end -->

## 2. Execution trace

<!-- trace:start -->
```
14:04:32 | run_workflow       | started: data/meal_requests.json, request #2
14:04:32 | load_json_file     | OK  data/meal_requests.json read
14:04:32 | validate_data      | OK  4 valid requests, using #2: {'dietary_preference': 'vegetarian', 'theme_requests': 'Italian, Asian, Mexican', 'additional_preferences': 'no mushrooms'}
14:04:32 | call_meal_plan_api | sending request to gpt-4o-mini ...
14:04:33 | run_workflow       | STOPPED, error below
```
<!-- trace:end -->

## 3. Input payload

<!-- input:start -->
```json
{
  "dietary_preference": "vegetarian",
  "theme_requests": "Italian, Asian, Mexican",
  "additional_preferences": "no mushrooms"
}
```
<!-- input:end -->

## 4. Output record

<!-- output:start -->
The run failed, so there is no output record:

```
ERROR in call_meal_plan_api()
  Type:       OpenAIAuthenticationError
  Message:    Error code: 401 - {'error': {'message': 'Your API key has been invalidated.', 'type': None, 'code': 'token_invalidated', 'param': None}, 'status': 401}
  Location:   OpenAI chat API, model gpt-4o-mini, HTTP 401
  Suggestion: Check OPENAI_API_KEY in .env: the key is wrong, expired or revoked.
```
<!-- output:end -->

## 5. Verify: did the input reach the output correctly?

<!-- checks:start -->
- Not verified: the run failed (see sections 2 and 4).
<!-- checks:end -->

## 6. Error messages (no silent failures)

Each message names the function, the error type, the location and a suggestion.

<!-- errors:start -->
**API error: missing key**

```
ERROR in call_meal_plan_api()
  Type:       ValueError
  Message:    OPENAI_API_KEY is not set
  Location:   .env file next to this notebook
  Suggestion: Copy .env.example to .env and paste your OpenAI API key.
```

**API error: wrong key**

```
ERROR in call_meal_plan_api()
  Type:       OpenAIAuthenticationError
  Message:    Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-fake-****************only. You can find your API key at https://platform.openai.com/account/api-keys.', 'type': 'invalid_request_error', 'code': 'invalid_api_key', 'param': None}, 'status': 401}
  Location:   OpenAI chat API, model gpt-4o-mini, HTTP 401
  Suggestion: Check OPENAI_API_KEY in .env: the key is wrong, expired or revoked.
```

**Network error: server unreachable**

```
ERROR in call_meal_plan_api()
  Type:       OpenAIConnectionError
  Message:    Connection error.
  Location:   OpenAI chat API, model gpt-4o-mini, network detail: ConnectionRefusedError: [Errno 61] Connection refused
  Suggestion: Check your internet connection, VPN or proxy, then try again.
```

**Missing file: data/does_not_exist.json**

```
ERROR in load_json_file()
  Type:       FileNotFoundError
  Message:    [Errno 2] No such file or directory: 'data/does_not_exist.json'
  Location:   file /Users/macbook-air/Desktop/AI consulting/Week2/Day5/lab-python-low-code/data/does_not_exist.json
  Suggestion: Check the file name and that the file is in the data/ folder next to this notebook.
```

**Malformed JSON: data/malformed.json**

```
ERROR in parse_json_text()
  Type:       JSONDecodeError
  Message:    Expecting ',' delimiter: line 4 column 5 (char 120)
  Location:   data/malformed.json, line 4, column 5, near 'nal_preferences": "none"}\n    {"dietary_preference": "keto",'
  Suggestion: Fix the JSON at that spot: usually a missing comma, bracket or quote.
```

**Invalid data: data/invalid_requests.json**

```
ERROR in validate_data()
  Type:       ValidationError
  Message:    4 invalid field(s)
              - requests.0.dietary_preference: Input should be 'omnivore', 'vegetarian', 'vegan' or 'keto'
              - requests.1.dietary_preference: Field required
              - requests.2.theme_requests: Input should be a valid string
              - requests.2.additional_preferences: Input should be a valid string
  Location:   data/invalid_requests.json (checked against RequestFile)
  Suggestion: Fix the listed requests in the file (requests.0 is the first one). dietary_preference must be one of: omnivore, vegetarian, vegan, keto; themes and preferences must be text.
```
<!-- errors:end -->

## 7. Explain

**Mapping.** Every input field has one place in the prompt and one place where its effect is visible in the output:

| Input field | Used in the prompt as | Visible in the output as |
|---|---|---|
| `dietary_preference` | "Diet:" line + the diet guidelines | `meal_plan.dietary_preference` and the ingredients chosen |
| `theme_requests` | "Theme requests:" line | `recipes[].theme` |
| `additional_preferences` | "Preferences:" line | the ingredients (for example no mushrooms) |

The request is validated before it reaches the prompt, and the answer is validated against the same `MealPlan` rules the prompt states, so both ends of the transformation are checked by code rather than by eye.

**Operational risks.**
1. The model output is probabilistic: it can break the 7 x 5 rules or send broken JSON. `parse_json_text` and `validate_data` catch it, but the user has to click Generate again (automatic retry is the optional Step 7).
2. Every run is a paid call: a revoked key or an empty balance stops all runs (`AuthenticationError`, `RateLimitError`).
3. Preferences such as "no mushrooms" are only requested in the prompt; code reports them in section 5 but does not enforce them.

**First failure mode I would monitor if this ran daily:** the share of runs that fail `parse_json_text` or `validate_data(MealPlan)`, meaning the model answer breaks the schema. Key and quota errors are loud and stop the run at once, while schema failures creep in quietly when the model version or the prompt changes, so I would track that rate per day and alert when it rises.
