# Refactoring Checklist

## Scope

I am following Path 2 using the instructor-provided Meal Planner starter notebook.

The original generation flow has run successfully, and I have captured a baseline screenshot. The issues below were identified through code inspection. Failure scenarios will be tested during refactoring.

Baseline location: `meal_planner_refactored.ipynb`, the code cell immediately after `run_basic_validation`, identified by the comment
`# Baseline: single manual generation and evidence export`.

This cell performs one manual generation call and saves its input and output. The original four-call TEST_CASES cell is not part of this baseline.

## Issues Found

- [x] **1. Configuration does not clearly handle a missing API key.**
  - **Location:** Configuration cells, especially `os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY`.
  - **Problem:** `os.getenv()` can return `None`, which cannot be assigned to an environment variable.
  - **Consequence:** Setup fails with a technical error instead of explaining that the API key is missing.
  - **Verification plan:** Test configuration with the key absent from both the environment and `.env`. Confirm that the error identifies the configuration function and suggests setting `OPENAI_API_KEY`.
  - **Completed:** Added explicit API key validation before environment assignment. Offline checks passed for missing, empty, and whitespace-only values, including a simulated missing environment key. Loading from an actual .env file was not independently tested.

- [x] **2. Email credentials are configured inside the notebook.**
  - **Location:** Configuration cell: `EMAIL_SENDER` and `EMAIL_PASSWORD`.
  - **Problem:** The notebook encourages replacing placeholder strings with actual email credentials.
  - **Consequence:** Credentials could be exposed through GitHub, shared notebooks, or screenshots.
  - **Verification plan:** Move credential loading to environment variables. Confirm that email configuration errors are clear and that ordinary meal generation works without SMTP credentials.
  - **Completed:** Email credentials are loaded from environment variables. Missing email settings are rejected before SMTP access without exposing credential values. Offline checks passed for either or both settings missing and for a whitespace-only password. SMTP was not called.

- [x] **3. The API invocation is outside the protected error-handling block.**
  - **Location:** `MealPlanGenerator.generate()`, at `recipe_chain.invoke(...)`.
  - **Problem:** The `try` block starts after the API call.
  - **Consequence:** Authentication, rate-limit, connection, and timeout errors can escape the intended failure-result handling.
  - **Verification plan:** Use a fake API dependency to raise each relevant exception. Confirm that the actual invocation is protected and the caller receives a clear failure result.
  - **Completed:** Moved the API invocation inside the protected block. Offline tests passed for authentication, rate-limit, timeout, connection, server, and unexpected errors.

- [x] **4. The generation method has too many responsibilities.**
  - **Location:** `MealPlanGenerator.generate()`.
  - **Problem:** It prepares input values, invokes the model, extracts response content, parses JSON, validates the plan, measures time, and constructs the result.
  - **Consequence:** Parsing and validation are difficult to test independently from the API.
  - **Verification plan:** Extract focused functions and test them with handmade data. Confirm that `generate()` mainly coordinates these functions.
  - **Completed:** Split request preparation, model invocation, JSON parsing, schema validation, and failure-result construction into focused helpers. generate() now coordinates these steps and handles timing and exceptions. Offline helper and integration checks passed.

- [x] **5. JSON code-fence extraction relies on fragile string splitting.**
  - **Location:** `MealPlanGenerator.generate()`, in the checks for triple backticks.
  - **Problem:** The code does not explicitly define which response formats are accepted.
  - **Consequence:** Unexpected or incomplete fences may produce confusing parsing failures.
  - **Verification plan:** Test plain JSON, correctly fenced JSON, malformed JSON, incomplete fences, and surrounding text. Define which formats are supported and reject unsupported formats clearly.
  - **Completed:** Extracted `parse_model_json()` with explicit support for plain JSON and complete outer JSON or unlabeled fences. Direct helper and generation integration checks passed, including non-object payloads, unsupported fence labels, incomplete fences, and surrounding text.

- [x] **6. Success and failure results have different keys.**
  - **Location:** The return dictionaries in `MealPlanGenerator.generate()`.
  - **Problem:** Successful results include `generation_time`, but failure results omit it.
  - **Consequence:** Callers must handle different result shapes, increasing the risk of missing-key errors.
  - **Verification plan:** Define one result contract and assert the expected keys and value types for both successful and failed generation.
  - **Completed:** Standardized all generation results to contain success, meal_plan, generation_time, and error. Offline contract checks passed for success, JSON parsing, schema validation, and unexpected failures.

- [ ] **7. Error messages lack consistent location and recovery guidance.**
  - **Location:** Exception handlers in `generate()` and `send_meal_plan_email()`.
  - **Problem:** Messages generally report exception text without consistently identifying the function, affected field or operation, and a suggested fix.
  - **Consequence:** Users may know that something failed without knowing where to investigate.
  - **Verification plan:** Trigger parsing, validation, API, and SMTP failures. Check that messages include the function, error type, safe context, and a helpful suggestion without exposing credentials.

- [x] **8. Ingredient formatting is duplicated.**
  - **Location:** `format_meal_plan_email()` and `format_single_recipe()`.
  - **Problem:** Both functions build the same comma-separated ingredient text.
  - **Consequence:** A formatting change must be repeated and may become inconsistent between email and UI.
  - **Verification plan:** Extract a shared formatting helper. Test it with a small recipe and confirm that both callers preserve their existing output format.
  - **Completed:** Extracted `format_ingredient_list()` and reused it in
    email and UI formatting. Offline checks passed for the helper,
    email ingredient formatting, and UI output. The UI test uses
    its own handmade recipe data.

- [x] **9. The Email Plan button generates a new plan.**
  - **Location:** `send_email_ui()`.
  - **Problem:** The callback calls `generator.generate()` instead of using the plan already displayed.
  - **Consequence:** The emailed plan may differ from the displayed plan, and sending email creates an additional paid API request.
  - **Verification plan:** Store the displayed plan in session state. With a fake sender and generation call counter, confirm that Email Plan sends that plan without another generation call. Also test clicking Email before generating a plan.
  - **Completed:** Email now consumes the displayed plan through Gradio state without another generation call. Offline callback tests passed for plan forwarding, empty state, state clearing, and the Generate-to-Email flow. Browser-session isolation and concurrent interactions have not been tested.

- [x] **10. Optional textbox handling is duplicated and does not support `None`.**
  - **Location:** `generate_plan_streaming()` and `send_email_ui()`, where `.strip()` is called.
  - **Problem:** The callbacks repeat default-value logic and assume that textbox values are strings.
  - **Consequence:** A `None` value raises an exception, while defaults may become inconsistent between callers.
  - **Verification plan:** Extract a normalization helper and test `None`, an empty string, whitespace-only input, and meaningful text.
  - **Completed:** Added `normalize_optional_text()` and reused it in both
    callbacks. Offline helper and callback checks passed for None, empty,
    whitespace-only, and padded meaningful inputs. Callback tests used a
    fake generator without API calls or email delivery.

- [x] **11. Validation rules and numeric values are repeated.**
  - **Location:** Pydantic validators and `run_basic_validation()`.
  - **Problem:** Recipe counts, ingredient counts, and unique-theme checks are implemented in multiple places. Some checks use literal values such as `5` and `7`.
  - **Consequence:** Updating one rule may leave other checks inconsistent.
  - **Verification plan:** Centralize the rules and reuse appropriate constants. Test invalid recipe counts, invalid ingredient counts, and duplicate themes through the authoritative validation path.
  - **Completed:** Centralized meal-plan rules in the Pydantic models. Both generation and basic validation use validate_meal_plan(). Recipe and ingredient counts use len(DAYS) and INGREDIENTS_PER_RECIPE. Offline checks passed for valid data, incorrect counts, duplicate themes, and propagation of generation failures.

- [x] **12. Email construction and network delivery are mixed together.**
  - **Location:** `send_meal_plan_email()`.
  - **Problem:** One function constructs the MIME message, connects to SMTP, authenticates, and sends the message.
  - **Consequence:** Testing message construction independently requires avoiding or replacing network operations inside the same function.
  - **Verification plan:** Separate message construction from delivery. Inspect the constructed message offline and use a fake SMTP dependency to test delivery failures.
  - **Completed:** Extracted build_meal_plan_message() from SMTP delivery. Offline checks passed for headers, UTF-8 body encoding, absence of network access during construction, and message forwarding through mocked SMTP. No real email was sent.

- [ ] **13. Unused shopping-list components remain in the code.**
  - **Location:** `SHOPPING_LIST_PROMPT` and `MealPlanGenerator.__init__()`, particularly `self.shopping_parser`.
  - **Problem:** These components are defined but are not used by the current generation flow.
  - **Consequence:** They make the workflow harder to understand and suggest functionality that is not actually executed.
  - **Verification plan:** Confirm their references before removing them. Re-run generation and validation checks to verify that behavior is preserved.

- [ ] **14. Test inputs, execution, and printing are combined in one API-dependent cell.**
  - **Location:** The final `TEST_CASES` cell.
  - **Problem:** Test cases are embedded in the notebook, and running the cell makes four real API calls. There is no actual file-input path for the required missing-file and malformed-file tests.
  - **Consequence:** Routine tests cost money, depend on the network, and do not cover the lab's file-handling requirements.
  - **Verification plan:** Move request cases into a JSON fixture loaded by the test runner. Add separate offline tests for a missing file, malformed JSON, and invalid request data. Keep real API tests explicitly opt-in.

## Top 3 Priorities

1. **Make configuration safe and explicit.**
   Handle missing API keys clearly and load email credentials from environment variables to reduce the risk of credential exposure.

2. **Protect the actual API invocation and standardize failure handling.**
   Handle API and network failures at the correct boundary, return a consistent result structure, and provide actionable error messages.

3. **Ensure Email Plan sends the displayed plan.**
   Preserve the successful plan in session state and prevent unnecessary regeneration when sending email.

## Completion Rule

I will check an issue off only after implementing the change and completing its verification plan. I will distinguish offline simulations from real API or email runs in the evidence.