# CP3: MyCarAI Build

**Team:** Will Webster, Trey Adleta, Sang Lian, Ryan Ballard

**Repository:** submitted as a zip made with `git archive` (no `.venv`, no `.env`, no database files). Start it with [README.md](README.md).


## 1. Final suite run

Run on November 4, 2026, with `python -m pytest -v` from the repo root, on the code being submitted: commit `0f65434` plus the changes made after the audit in section 5, committed together as the submission. Those changes are the fixes in `ai.py`, `app.py`, `validators.py`, `static/chat.js`, the templates, and `requirements.txt`; the new eval file `tests/test_review_findings.py` (section 2); and the read-only agent files and `CLAUDE.md` rule (section 8). The 62 CP2 evals are unchanged. Python 3.13.14, pytest 9.2.0. The tests use the fake provider (`TESTING=1` from `tests/conftest.py`) and make no Gemini calls.

**Result: 102 passed, 0 failed** (the 62 CP2 evals plus 40 added since). No test fails, so there is nothing to explain.

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\.venv\Scripts\python.exe
rootdir: C:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0
collecting ... collected 102 items

tests/test_acceptance.py::test_e01_signup_creates_driver_with_hashed_password PASSED [  0%]
tests/test_acceptance.py::test_e02_signup_rejects_bad_email[-Email is required.] PASSED [  1%]
tests/test_acceptance.py::test_e02_signup_rejects_bad_email[not-an-email-Enter a valid email address.] PASSED [  2%]
tests/test_acceptance.py::test_e03_signup_rejects_short_password PASSED  [  3%]
tests/test_acceptance.py::test_e04_signup_rejects_duplicate_email_case_insensitive PASSED [  4%]
tests/test_acceptance.py::test_e05_login_lands_on_vehicle_then_chat_and_logout PASSED [  5%]
tests/test_acceptance.py::test_e06_login_failure_message_is_the_same PASSED [  6%]
tests/test_acceptance.py::test_e07_vehicle_list_only_has_vehicles_with_manuals PASSED [  7%]
tests/test_acceptance.py::test_e08_vehicle_post_is_validated_on_server[9999] PASSED [  8%]
tests/test_acceptance.py::test_e08_vehicle_post_is_validated_on_server[abc] PASSED [  9%]
tests/test_acceptance.py::test_e08_vehicle_post_is_validated_on_server[RAV4] PASSED [ 10%]
tests/test_acceptance.py::test_e09_chat_requires_a_vehicle PASSED        [ 11%]
tests/test_acceptance.py::test_e10_admin_adds_vehicle_and_uploads_manual PASSED [ 12%]
tests/test_acceptance.py::test_e11_add_vehicle_is_validated[fields0-Enter make, model, a 4-digit year, and trim.] PASSED [ 13%]
tests/test_acceptance.py::test_e11_add_vehicle_is_validated[fields1-Enter make, model, a 4-digit year, and trim.] PASSED [ 14%]
tests/test_acceptance.py::test_e11_add_vehicle_is_validated[fields2-This vehicle already exists.] PASSED [ 15%]
tests/test_acceptance.py::test_e12_upload_rejects_non_pdf[manual.docx-PK\x03\x04 not really a docx] PASSED [ 16%]
tests/test_acceptance.py::test_e12_upload_rejects_non_pdf[manual.pdf-just some text] PASSED [ 17%]
tests/test_acceptance.py::test_e13a_upload_requires_a_file PASSED        [ 18%]
tests/test_acceptance.py::test_e13b_upload_rejects_pdf_over_50_mb PASSED [ 19%]
tests/test_acceptance.py::test_e14_one_manual_per_vehicle PASSED         [ 20%]
tests/test_acceptance.py::test_e15_failed_embedding_rolls_back_upload PASSED [ 21%]
tests/test_acceptance.py::test_e16_answer_is_grounded_with_source PASSED [ 22%]
tests/test_acceptance.py::test_e17_off_topic_question_gets_not_sure PASSED [ 23%]
tests/test_acceptance.py::test_e18_empty_question_is_rejected[] PASSED   [ 24%]
tests/test_acceptance.py::test_e18_empty_question_is_rejected[     ] PASSED [ 25%]
tests/test_acceptance.py::test_e19_question_length_is_checked_on_server PASSED [ 26%]
tests/test_acceptance.py::test_e20_provider_failure_is_handled[missing_key] PASSED [ 27%]
tests/test_acceptance.py::test_e20_provider_failure_is_handled[rate_limit] PASSED [ 28%]
tests/test_acceptance.py::test_e21_question_html_is_escaped PASSED       [ 29%]
tests/test_acceptance.py::test_e22_follow_up_uses_the_conversations_vehicle PASSED [ 30%]
tests/test_acceptance.py::test_e23_history_lists_newest_first_with_full_thread PASSED [ 31%]
tests/test_acceptance.py::test_e24_missing_conversation_is_404 PASSED    [ 32%]
tests/test_acceptance.py::test_e25_delete_removes_conversation_messages_and_citations PASSED [ 33%]
tests/test_acceptance.py::test_e26_visitors_are_sent_to_login[/chat] PASSED [ 34%]
tests/test_acceptance.py::test_e26_visitors_are_sent_to_login[/conversations] PASSED [ 35%]
tests/test_acceptance.py::test_e26_visitors_are_sent_to_login[/vehicle] PASSED [ 36%]
tests/test_acceptance.py::test_e26_visitors_are_sent_to_login[/admin/manuals] PASSED [ 37%]
tests/test_acceptance.py::test_e27_driver_cannot_read_another_drivers_conversation PASSED [ 38%]
tests/test_acceptance.py::test_e28_driver_cannot_change_another_drivers_conversation PASSED [ 39%]
tests/test_acceptance.py::test_e29_drivers_cannot_use_admin_pages PASSED [ 40%]
tests/test_acceptance.py::test_e30_admin_cannot_use_driver_pages PASSED  [ 41%]
tests/test_acceptance.py::test_e31_signup_ignores_role_field PASSED      [ 42%]
tests/test_acceptance.py::test_e32_chat_js_loads_only_on_chat_pages_and_server_still_guards_length PASSED [ 43%]
tests/test_acceptance.py::test_e33_chat_and_delete_work_with_plain_form_posts PASSED [ 44%]
tests/test_constraints.py::test_required_file_exists[app.py] PASSED      [ 45%]
tests/test_constraints.py::test_required_file_exists[models.py] PASSED   [ 46%]
tests/test_constraints.py::test_required_file_exists[validators.py] PASSED [ 47%]
tests/test_constraints.py::test_required_file_exists[ai.py] PASSED       [ 48%]
tests/test_constraints.py::test_required_file_exists[seed.py] PASSED     [ 49%]
tests/test_constraints.py::test_required_file_exists[static/chat.js] PASSED [ 50%]
tests/test_constraints.py::test_sql_only_in_models PASSED                [ 50%]
tests/test_constraints.py::test_sql_is_parameterized PASSED              [ 51%]
tests/test_constraints.py::test_no_orm_or_forbidden_libraries PASSED     [ 52%]
tests/test_constraints.py::test_ai_provider_only_called_from_ai_py PASSED [ 53%]
tests/test_constraints.py::test_requirements_only_allowed_packages PASSED [ 54%]
tests/test_constraints.py::test_templates_do_not_disable_escaping PASSED [ 55%]
tests/test_constraints.py::test_question_box_has_no_maxlength PASSED     [ 56%]
tests/test_constraints.py::test_only_chat_js_and_no_external_scripts PASSED [ 57%]
tests/test_constraints.py::test_env_is_ignored_and_not_committed PASSED  [ 58%]
tests/test_constraints.py::test_no_api_keys_in_source PASSED             [ 59%]
tests/test_constraints.py::test_debug_mode_not_hard_coded PASSED         [ 60%]
tests/test_review_findings.py::test_e04_signup_trims_and_lowercases_email PASSED [ 61%]
tests/test_review_findings.py::test_e02_signup_rejects_an_overlong_email PASSED [ 62%]
tests/test_review_findings.py::test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers[99999999999999999999] PASSED [ 63%]
tests/test_review_findings.py::test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers[-1] PASSED [ 64%]
tests/test_review_findings.py::test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers[1_0] PASSED [ 65%]
tests/test_review_findings.py::test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers[\u0661] PASSED [ 66%]
tests/test_review_findings.py::test_e10_upload_accepts_uppercase_extension PASSED [ 67%]
tests/test_review_findings.py::test_e11_add_vehicle_rejects_blank_short_and_oversized_fields[fields0] PASSED [ 68%]
tests/test_review_findings.py::test_e11_add_vehicle_rejects_blank_short_and_oversized_fields[fields1] PASSED [ 69%]
tests/test_review_findings.py::test_e11_add_vehicle_rejects_blank_short_and_oversized_fields[fields2] PASSED [ 70%]
tests/test_review_findings.py::test_e11_add_vehicle_rejects_blank_short_and_oversized_fields[fields3] PASSED [ 71%]
tests/test_review_findings.py::test_e11_add_vehicle_rejects_blank_short_and_oversized_fields[fields4] PASSED [ 72%]
tests/test_review_findings.py::test_e11_extra_spaces_do_not_make_a_new_vehicle PASSED [ 73%]
tests/test_review_findings.py::test_e12_upload_rejects_a_corrupt_pdf PASSED [ 74%]
tests/test_review_findings.py::test_e12_a_chosen_file_with_no_bytes_is_not_a_pdf PASSED [ 75%]
tests/test_review_findings.py::test_e12_a_pdf_with_no_readable_text_is_refused_with_a_clear_message PASSED [ 76%]
tests/test_review_findings.py::test_e14_upload_for_a_missing_vehicle_is_refused PASSED [ 77%]
tests/test_review_findings.py::test_e15_a_short_embedding_reply_rolls_back_the_upload PASSED [ 78%]
tests/test_review_findings.py::test_e15_wrong_size_embeddings_roll_back_the_upload PASSED [ 79%]
tests/test_review_findings.py::test_e19_a_new_line_counts_once_like_the_live_counter PASSED [ 80%]
tests/test_review_findings.py::test_e19_one_more_character_after_new_lines_is_still_refused PASSED [ 81%]
tests/test_review_findings.py::test_e19_spaces_around_the_question_do_not_count PASSED [ 82%]
tests/test_review_findings.py::test_e20_unavailable_message_is_a_calm_notice_not_a_typing_error PASSED [ 83%]
tests/test_review_findings.py::test_e17_the_not_sure_reply_is_marked_so_it_can_look_calm PASSED [ 84%]
tests/test_review_findings.py::test_e16_a_sourced_answer_is_not_marked_not_sure PASSED [ 85%]
tests/test_review_findings.py::test_e24_a_conversation_id_too_big_for_the_database_is_a_404 PASSED [ 86%]
tests/test_review_findings.py::test_e25_get_on_delete_shows_a_plain_405_page PASSED [ 87%]
tests/test_review_findings.py::test_e29_a_post_from_another_site_is_refused PASSED [ 88%]
tests/test_review_findings.py::test_e29_posts_from_our_own_pages_and_typed_links_still_work PASSED [ 89%]
tests/test_review_findings.py::test_e29_an_unknown_admin_action_shows_a_plain_400_page PASSED [ 90%]
tests/test_review_findings.py::test_e13_a_driver_posting_too_much_is_not_told_about_pdfs PASSED [ 91%]
tests/test_review_findings.py::test_security_headers_are_on_every_page[/login] PASSED [ 92%]
tests/test_review_findings.py::test_security_headers_are_on_every_page[/signup] PASSED [ 93%]
tests/test_review_findings.py::test_security_headers_are_on_every_page[/chat] PASSED [ 94%]
tests/test_review_findings.py::test_security_headers_are_on_every_page[/conversations] PASSED [ 95%]
tests/test_review_findings.py::test_security_headers_are_on_every_page[/vehicle] PASSED [ 96%]
tests/test_review_findings.py::test_a_head_request_is_treated_like_a_get PASSED [ 97%]
tests/test_review_findings.py::test_the_session_cookie_is_http_only_and_same_site PASSED [ 98%]
tests/test_review_findings.py::test_the_nav_marks_the_page_you_are_on PASSED [ 99%]
tests/test_review_findings.py::test_the_chat_page_suggests_questions_only_before_the_first_one PASSED [100%]

============================ 102 passed in 57.83s =============================
```

We also ran the submission the way the peer audit will, on the evening of November 4: a clean copy of exactly the files being submitted (no `.venv`, no `.env`, no database), a new virtual environment, `pip install -r requirements.txt` (about 66 seconds), and a test-mode `.env` as in README Option B. `seed.py` ran twice without error, the suite gave 102 passed, and `flask --app app run` served the app: a new driver signed up, chose the Camry, got the lane keep assist answer with "Source: 2024 Toyota Camry XSE Owner's Manual, PDF page 2", got "I'm not sure" with no Source line for the World Series question, and deleted a conversation (then 404). The admin signed in and saw the Camry manual, and got 403 on `/chat`. The server log showed no traceback.

## 2. Evals added or changed since CP2

No CP2 eval was removed or edited. The 62 evals in `tests/test_acceptance.py` and `tests/test_constraints.py` are the same as at CP2 (commit `866754e`, November 3). Commit `59b38d3` deleted `tests/run_output_2026-11-02.txt`, a saved CP2 run log rather than a test, so the submission does not carry a stale run.

We added one file, `tests/test_review_findings.py`: 29 tests, 40 cases, all passing. Each was added because the validator-reviewer run (sections 5 and 6), the security review, or the design review found a gap. A test that extends a criterion is named `test_eNN_...` after it, so eval NN still checks criterion NN; the five tests for the cookie, the headers, HEAD requests, the nav, and the example questions have no matching criterion and are not named eNN.

| Eval(s) added | Reason |
|---|---|
| `test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers` (4 cases) | F1: a 20-digit id gave a 500; `-1`, `1_0` and a non-Latin digit are covered too |
| `test_e24_a_conversation_id_too_big_for_the_database_is_a_404` | F1: the same 500 on the conversation page, its delete, and follow-ups |
| `test_e14_upload_for_a_missing_vehicle_is_refused` | F1 and F10: an upload for a missing or oversized vehicle id was untested |
| `test_e19_a_new_line_counts_once_like_the_live_counter`, `test_e19_one_more_character_after_new_lines_is_still_refused` | F2: the server counted each new line as 2 characters and the counter as 1 |
| `test_e19_spaces_around_the_question_do_not_count` | F4: surrounding spaces must not count toward 500 |
| `test_e15_a_short_embedding_reply_rolls_back_the_upload`, `test_e15_wrong_size_embeddings_roll_back_the_upload` | F3: a short or wrong-size embedding reply saved part of a manual |
| `test_e02_signup_rejects_an_overlong_email` | F8: no length limit on email |
| `test_e11_add_vehicle_rejects_blank_short_and_oversized_fields` (5 cases) | F8 and F10: blank make, 3- and 5-digit years, year `0000`, a 51-character make |
| `test_e11_extra_spaces_do_not_make_a_new_vehicle` | F8: spaces and case must not create a duplicate vehicle |
| `test_e12_a_chosen_file_with_no_bytes_is_not_a_pdf`, `test_e12_a_pdf_with_no_readable_text_is_refused_with_a_clear_message` | F9: unclear messages for an empty file and a scanned PDF |
| `test_e12_upload_rejects_a_corrupt_pdf`, `test_e10_upload_accepts_uppercase_extension`, `test_e04_signup_trims_and_lowercases_email` | F10: behavior was already right but had no test |
| `test_e25_get_on_delete_shows_a_plain_405_page`, `test_e29_an_unknown_admin_action_shows_a_plain_400_page`, `test_e13_a_driver_posting_too_much_is_not_told_about_pdfs` | F7: Werkzeug's default 400 and 405 pages, and a driver told about PDFs on a 413 |
| `test_e29_a_post_from_another_site_is_refused`, `test_e29_posts_from_our_own_pages_and_typed_links_still_work` | F5 and the security review: no protection against posts from other sites |
| `test_the_session_cookie_is_http_only_and_same_site`, `test_security_headers_are_on_every_page` (5 pages) | F6 and the security review: cookie flags and security headers |
| `test_a_head_request_is_treated_like_a_get` | The cross-site POST check must not block HEAD requests that link previewers send |
| `test_e20_unavailable_message_is_a_calm_notice_not_a_typing_error`, `test_e17_the_not_sure_reply_is_marked_so_it_can_look_calm`, `test_e16_a_sourced_answer_is_not_marked_not_sure` | Design review: the unavailable and "I'm not sure" replies are styled so a driver does not think they did something wrong |
| `test_the_nav_marks_the_page_you_are_on`, `test_the_chat_page_suggests_questions_only_before_the_first_one` | Design review: page-shell changes with no matching criterion, so they are not named eNN |

## 3. Spec conformance table

How to repeat the evidence: run `python -m pytest -v` and find the named test. Hand checks use the setup in the spec: `TESTING=1` and `FAKE_DELAY_SECONDS=3` in `.env`, then `python seed.py`, `flask --app app run`, sign in as a driver, and choose the Camry.

| # | Status | Evidence |
|---|---|---|
| 1 | Met | Signing up lands on `/vehicle`, the header shows the email, the role is `driver`, and the stored password is hashed (`test_e01_signup_creates_driver_with_hashed_password`). No gap found. |
| 2 | Met | An empty email shows "Email is required." and a malformed one shows "Enter a valid email address." (`test_e02_signup_rejects_bad_email`, both cases). The audit found that an email of any length was accepted; `validators.py` now refuses one over 254 characters, and `test_e02_signup_rejects_an_overlong_email` passes. |
| 3 | Met | A 7-character password is refused with the right message (`test_e03_signup_rejects_short_password`). A password of 8 spaces is accepted, which the spec allows because it sets only a length. |
| 4 | Met | A duplicate email in a different case is refused and the row count does not change (`test_e04_signup_rejects_duplicate_email_case_insensitive`). An email typed with spaces around it is trimmed and lowercased before it is saved (`test_e04_signup_trims_and_lowercases_email`, added after the audit). |
| 5 | Met | Sign-in lands on `/vehicle` or `/chat`, and signing out shows "You are signed out." and locks `/chat` again (`test_e05_login_lands_on_vehicle_then_chat_and_logout`). No gap found. |
| 6 | Met | A wrong password and an unknown email show the same message (`test_e06_login_failure_message_is_the_same`). The test checks the message only. The audit noted that an unknown email may answer faster than a wrong password, because no hash is checked; we read this in `app.py` and did not measure it. |
| 7 | Met | The vehicle list shows the Camry and not the RAV4 (which has no manual), and Save goes to `/chat` (`test_e07_vehicle_list_only_has_vehicles_with_manuals`). No gap found. |
| 8 | Met | A POST with `9999`, `abc`, or the RAV4 id is refused and the driver's vehicle does not change (`test_e08_vehicle_post_is_validated_on_server`, 3 cases). Gap found on November 4: a 20-digit id returned a 500 page instead of "Choose a vehicle from the list.", because SQLite cannot compare an integer that large; we reproduced it with the Flask test client (section 6, F1). `validators.py` now accepts only 1 to 18 ASCII digits, and `test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers` passes for a 20-digit id, `-1`, `1_0`, and the Arabic-Indic digit `١`. |
| 9 | Met | `/chat` with no vehicle chosen redirects to `/vehicle` with "Choose your vehicle first." (`test_e09_chat_requires_a_vehicle`). No gap found. |
| 10 | Met | The admin adds a 2025 Camry SE, uploads the sample PDF, and the manual row and chunks for pages 1 to 3 appear (`test_e10_admin_adds_vehicle_and_uploads_manual`). An upload named `MANUAL.PDF` also works (`test_e10_upload_accepts_uppercase_extension`, added after the audit). |
| 11 | Met | An empty make, the year `20x5`, and a duplicate vehicle are each refused and the row count does not change (`test_e11_add_vehicle_is_validated`, 3 cases). Gaps found on November 4 by running it: year `0000` and a 100,000-character make were accepted. `validators.py` now refuses a year starting with 0 and any make, model, or trim over 50 characters, and `test_e11_add_vehicle_rejects_blank_short_and_oversized_fields` passes (5 cases). Spaces and case around a field are ignored when checking for a duplicate, so a trim of "  le " is caught as a duplicate of "LE", and repeated spaces inside a field are collapsed to one (`test_e11_extra_spaces_do_not_make_a_new_vehicle`). |
| 12 | Met | A `.docx` file, and text renamed to `.pdf`, both show "Upload a PDF file." and add no rows (`test_e12_upload_rejects_non_pdf`, 2 cases). Added after the audit: a file that starts with `%PDF-` but is not a real PDF, and a chosen file with no bytes, also get "Upload a PDF file." (`test_e12_upload_rejects_a_corrupt_pdf`, `test_e12_a_chosen_file_with_no_bytes_is_not_a_pdf`). A PDF with no readable text now gets its own message (see departure 2). |
| 13 | Met | Pressing Upload with no file shows "Choose a PDF to upload.", and a file over 50 MB shows "PDFs must be 50 MB or smaller.", with no rows added in either case (`test_e13a_upload_requires_a_file`, `test_e13b_upload_rejects_pdf_over_50_mb`). Both tests use the Flask test client; we have not uploaded an over-50 MB file through a real browser. A file of exactly 50 MB also gets the 413 message, because the request is slightly larger than the file. |
| 14 | Met | A second manual for the Camry is refused and the manual and chunk counts do not change (`test_e14_one_manual_per_vehicle`). An upload for a vehicle id that does not exist, or is too large for the database, is refused with "Choose a vehicle from the list." (`test_e14_upload_for_a_missing_vehicle_is_refused`, added after the audit). |
| 15 | Met | When the embedding step fails, the page shows "The manual could not be processed. Try again." and no `manuals` or `chunks` row remains (`test_e15_failed_embedding_rolls_back_upload`). Gap found on November 4: when we made the provider return one vector too few, the upload succeeded and saved a 3-page manual with only pages 1 and 2, shown as "Ready" (section 6, F3). `ai.py` now checks the number and size of the vectors and fails the whole upload if they do not match, and `test_e15_a_short_embedding_reply_rolls_back_the_upload` and `test_e15_wrong_size_embeddings_roll_back_the_upload` pass. |
| 16 | Partly met | The question about lane keep assist gets the grounded answer with "Source: ... PDF page 2" (`test_e16_answer_is_grounded_with_source`). That answer comes from the fake provider and the sample PDF. The spec's hand check against the real Camry manual with Gemini, to confirm the Source page contains "lane", was not done before submission. |
| 17 | Partly met | The World Series question gets "I'm not sure", shows no Source line, and both messages are saved (`test_e17_off_topic_question_gets_not_sure`). That uses the fake provider and the fixed 0.55 cutoff. The hand check against the real manual was not done, and the real-manual cutoff is still the untuned 0.55 (departure 1). |
| 18 | Met | An empty question, or one made of spaces only, shows "Type a question first." and no rows are added (`test_e18_empty_question_is_rejected`, 2 cases). No gap found. |
| 19 | Met | A 501-character question is refused by a direct POST, and exactly 500 characters is saved and answered (`test_e19_question_length_is_checked_on_server`). Gap found on November 4: browsers send each new line as two characters (`\r\n`) while the counter counts one, so a driver using Shift+Enter could see "500 / 500" and still be refused; we reproduced it with a 509-character POST (section 6, F2). `validators.py` now counts a new line once, and `test_e19_a_new_line_counts_once_like_the_live_counter` and `test_e19_one_more_character_after_new_lines_is_still_refused` pass. We have not tried it by typing in a browser. |
| 20 | Met | A missing API key and a 429 both show the unavailable message, never the word "Traceback", and save no rows (`test_e20_provider_failure_is_handled`, 2 cases). Both cases come from the fake provider; we have not seen a real 429 from Gemini. One call with a made-up key showed that the key does not appear in the logged error (section 6, L3). |
| 21 | Met | A question containing `<script>` is escaped in the page (`test_e21_question_html_is_escaped`). The constraint test `test_templates_do_not_disable_escaping` also checks that no template uses `\|safe` or `Markup()`. No gap found. |
| 22 | Met | A follow-up adds two messages and no new conversation, and after the driver switches vehicles it still answers from the conversation's own vehicle (`test_e22_follow_up_uses_the_conversations_vehicle`). No gap found. |
| 23 | Met | History lists conversations newest first, with the 60-character title, the vehicle, the date, and the full thread (`test_e23_history_lists_newest_first_with_full_thread`). No gap found. |
| 24 | Met | `/conversations/9999` shows a 404 with "Conversation not found." (`test_e24_missing_conversation_is_404`). Gap found on November 4: a 20-digit id returned a 500 page instead of the 404 (section 6, F1). `app.py` now sends such ids to the same 404, and `test_e24_a_conversation_id_too_big_for_the_database_is_a_404` passes for the page, the delete, and a follow-up. |
| 25 | Met | Delete removes the conversation, its messages, and its citations, and a GET on the delete address gives 405 (`test_e25_delete_removes_conversation_messages_and_citations`). The 405 page used to be Werkzeug's plain page; it now uses our own error page (`test_e25_get_on_delete_shows_a_plain_405_page`). |
| 26 | Met | A visitor who is not signed in is redirected to `/login` from `/chat`, `/conversations`, `/vehicle`, and `/admin/manuals` (`test_e26_visitors_are_sent_to_login`, 4 cases). No gap found. |
| 27 | Met | Driver A gets a 404 on driver B's conversation and B's question text does not appear (`test_e27_driver_cannot_read_another_drivers_conversation`). The 20-digit id gap from criterion 24 applied here too and has the same fix and test. |
| 28 | Met | Driver A's delete or follow-up on driver B's conversation gets a 404 and the counts do not change (`test_e28_driver_cannot_change_another_drivers_conversation`). The delete route also returned a 500 for a 20-digit id on November 4; it has the same fix as criterion 24. |
| 29 | Met | A driver gets 403 on `/admin/manuals` and on its POSTs, and no rows are added (`test_e29_drivers_cannot_use_admin_pages`). After the security review we also refuse a POST that the browser labels as coming from another site (`test_e29_a_post_from_another_site_is_refused`), while posts from our own pages still work (`test_e29_posts_from_our_own_pages_and_typed_links_still_work`). |
| 30 | Met | An admin gets a 404 on a driver's conversation and a 403 on the driver pages (`test_e30_admin_cannot_use_driver_pages`). No gap found. |
| 31 | Met | A signup that sends `role=admin` still creates a driver (`test_e31_signup_ignores_role_field`). The audit confirmed that `app.py` never reads a `role` field. |
| 32 | Partly met | On the server side, `chat.js` loads only on the chat pages and a 501-character follow-up is refused (`test_e32_chat_js_loads_only_on_chat_pages_and_server_still_guards_length`). The four browser behaviors (Send disables and shows "Thinking..." for 3 seconds, a double send saves one copy, the counter is normal at "500 / 500" and red at "501 / 500") need JavaScript, which the test client does not run, and the hand check in a browser was not done before submission. |
| 33 | Partly met | The server handles the same plain form posts a browser sends with JavaScript off: asking shows the answer with "PDF page 2", and Delete works as a plain form post (`test_e33_chat_and_delete_work_with_plain_form_posts`). The hand check in a browser with JavaScript turned off, including that no confirm box appears, was not done before submission. |

The build rules in the spec's Constraints section are also checked automatically in `tests/test_constraints.py` (12 tests, 17 cases): SQL only in `models.py` and always parameterized, no ORM or forbidden libraries, AI calls only in `ai.py`, only the five allowed packages, no `|safe` or `Markup()`, no `maxlength` on the question box, only `chat.js` and no external scripts, `.env` ignored and never committed, no API keys in source, and debug mode not hard-coded.

### Where the build departs from the spec

1. **`SIMILARITY_CUTOFF` for the real manual was not tuned.** The spec says the team tunes it against the real Camry manual before CP2. `REAL_SIMILARITY_CUTOFF` in `ai.py` is still the starting value, 0.55, the same as the fixed test value. We ran out of time to tune it before CP3: tuning means asking many questions against the real manual on Gemini's free tier, and we spent the last days on the audit fixes. The test value is unaffected, because the spec fixes it at 0.55.
2. **Two messages the spec does not list.** After the audit, the build added "This PDF has no text we can read. Upload a PDF with selectable text." for a scanned PDF (`validators.py`), and "That was too much to send at once. Please try something shorter." for a driver whose request is over the size limit (`app.py`, 413 handler). Criterion 13 only covers the admin's PDF message, which is unchanged, so no eval is affected. The spec should list both before the next checkpoint.
3. **Four hand checks were not done.** The real-manual checks for criteria 16 and 17 and the browser checks for criteria 32 and 33 were not done before submission, so those criteria are marked Partly met. Their automated parts pass.
4. **The chat page has a one-line hint above the question box and three example questions below it**, shown only before the first question. `CLAUDE.md` says the chat should have nothing in front of the box. Our design review added them because drivers are unsure what to ask; the box and Send button are unchanged and nothing must be clicked first. We will update `CLAUDE.md` to match.
5. **Security additions the spec does not ask for**, from the security and validator reviews: `app.py` refuses POSTs that the browser labels as coming from another site, sends `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` and `Content-Security-Policy` headers, and lets `SESSION_COOKIE_SECURE` be turned on from `.env`. `requirements.txt` now pins exact versions of the same five packages. None of these adds a feature.

Nothing out of scope was added. There is no AR, video, phone sign-in, password reset, VIN lookup, dashboard, rating, streaming, vector database, RAG framework, or JavaScript framework. The database tables and columns are the seven in the spec's Data section, created by `models.init_db`.

## 4. Custom subagent: `validator-reviewer`

**File:** [.claude/agents/validator-reviewer.md](.claude/agents/validator-reviewer.md), committed in the repository.

### Scope definition

**What it is for.** It audits MyCarAI's input validation and data flow. It checks that every input rule lives in `validators.py` and runs on the server before anything is saved. It checks that `chat.js` and the templates hold no rule the server lacks, and that the validation and upload settings (`MAX_CONTENT_LENGTH`, the 500-character question limit, the 8-character password, `SIMILARITY_CUTOFF`) match the spec. It also checks that nothing leaks to the browser, the logs, the repo, or Gemini. It is narrower than our `senior-security-review` agent: it does no threat modeling and sends anything outside its scope to that agent.

**What it may read.** Every file in the repository except `.env`: the routes, models, validators, `ai.py`, templates, `chat.js`, the tests, `CLAUDE.md`, and the spec.

**What it may run.** Nothing. Its tools line is `tools: Read, Grep, Glob`, so it cannot edit files or run commands. When a check needs a command (the test suite, a git history check, a test-client request), it writes the command under "Commands for the main agent", with the result that would confirm or clear the finding. The team decides whether the main agent runs it.

**What it must never do:**

1. Edit any file, or apply a fix. This is enforced by the tools line, which has no Edit, Write, or Bash. Fixes are suggested diffs only, and the team decides on each one.
2. Read, open, or print `.env`. It checks that `.env` is ignored by reading `.gitignore`, and it shows any key it finds as the first 4 characters plus `****`.
3. Call Gemini, or suggest a command that does. The only test command it gives is `python -m pytest`, which uses the fake provider.
4. Suggest editing a test to make it pass. A disagreement between a test and the code is reported as a finding.
5. Report a finding without evidence: a file and line and the code path. Anything it cannot prove by reading is labeled "Needs check", with the command that would prove it.

**Who fixes it when it breaks:** Will Webster. That person updates the agent file when the spec, the route list, or the validators change, and re-checks that the tools line is still read-only.

## 5. One real run

Run once on November 4, 2026, against the working tree at commit `0f65434` plus our uncommitted README, CLAUDE.md, and agent-file changes. The agent had `tools: Read, Grep, Glob`. There was no follow-up question and no second run.

> **Request:** Run a full audit of this repository.

**Output (as given):**

````markdown
**Verdict.** Every input is checked on the server, before anything is saved or sent to Gemini. I found no Blockers and no Highs. Ownership filters, role checks, escaping, what goes to Gemini, and secret handling all match the spec. There are three Medium edge cases. Two of them only need a hand-edited request to trigger, and none of them leaks anything. **It is safe to demo.**

### 1. Input inventory

| Route | Method | Field | Validator | Runs before save? | Message matches spec? |
|---|---|---|---|---|---|
| /signup | POST | email | `validate_signup` (validators.py:25) | Yes | Yes (E02, E04) |
| /signup | POST | password | `validate_signup` | Yes; hashed at app.py:165, never echoed back | Yes (E03) |
| /signup | POST | role | Never read; `create_user` defaults to driver | n/a | Ignored as spec requires (E31) |
| /login | POST | email, password | `clean_email` + `check_password_hash` | Nothing is saved | Same message for both failures (E06) |
| /vehicle | POST | vehicle_id | `validate_vehicle_choice` (validators.py:46) | Yes | Yes (E08). Huge ids fail, see F1 |
| /chat | POST | question | `validate_question` (validators.py:93) | Yes, before Gemini and before any row | Yes (E18, E19). See F2 |
| /conversations/<id> | GET/POST | URL id | `<int:>` converter + `models.get_conversation(id, user_id)` | Yes | 404 as spec. Huge ids fail, see F1 |
| /conversations/<id> | POST | question | `validate_question` | Yes | Yes (E32) |
| /conversations/<id>/delete | POST | URL id | `models.delete_conversation(id, user_id)` | n/a | 404 as spec (E28, E30) |
| /admin/manuals | POST | action (hidden) | Dispatch only; unknown value gives `abort(400)` | n/a | Both branches are behind `admin_required` |
| /admin/manuals add_vehicle | POST | make, model, year, trim | `validate_new_vehicle` (validators.py:54) | Yes | Yes (E11) |
| /admin/manuals upload | POST | vehicle_id | `validate_upload_vehicle` (validators.py:63) | Yes | Yes (E14) |
| /admin/manuals upload | POST | manual (file) | `MAX_CONTENT_LENGTH` + 413 handler, then `validate_pdf` (validators.py:73) | Yes; embedding happens before any write and the save is one transaction | Yes (E12, E13a, E13b, E15) |
| (all) | n/a | session `user_id` | Reloaded from the DB each request (app.py:54) | n/a | n/a |

There are no reads of `request.args`, `get_json`, or cookies. Every field a form sends is read, and every field the server reads is sent by a form.

### 2. Findings

| # | Severity | Area | Title | Location | Test covers it? |
|---|---|---|---|---|---|
| F1 | Medium (Needs check) | Vehicles, ownership | Ids above 2^63-1 crash with a 500 instead of the spec message or 404 | validators.py:39-43; app.py:276, 309 | No |
| F2 | Medium | Questions | Server counts each new line as 2 characters, the counter counts 1 | validators.py:94; static/chat.js:14 | No |
| F3 | Medium | Manual upload | Too few embeddings returned are silently dropped, so part of a manual gets saved | ai.py:117, 164-166 | No |
| F4 | Low | Client | Counter includes surrounding spaces and counts emoji as 2, the server does neither | static/chat.js:14 | No |
| F5 | Low | Forms | No CSRF tokens (known gap; `SameSite=Lax` limits it) | app.py:26 | n/a |
| F6 | Low | Session | `SESSION_COOKIE_SECURE` not set | app.py:26 | n/a |
| F7 | Low | Errors | 400 and 405 use Flask's default pages; a driver's 413 shows the PDF message | app.py:133-138, 346 | No |
| F8 | Low | Inputs | No length cap on email, make, model, trim; year `0000` is accepted | validators.py:12, 55-56 | No |
| F9 | Low | Upload | Unclear messages: an empty file says "Choose a PDF", a PDF with no text says "Try again" | validators.py:78-79; app.py:376-377 | No |
| F10 | Low | Coverage | Several Phase 2 edge cases have no tests | tests/test_acceptance.py | See section 7 |

### 3. Finding details

**F1. Ids too big for SQLite give a 500.**
- `_vehicle_id` accepts any `int()`, including `"99999999999999999999"`, `"1_0"`, and non-ASCII digits. Werkzeug's `<int:>` converter has no maximum either. Python's `sqlite3` raises `OverflowError` when it binds an int above 2^63-1.
- Path: `POST /vehicle vehicle_id=99999999999999999999` → `validate_vehicle_choice` → `models.vehicle_has_manual` → OverflowError → 500 "Something went wrong."
- The same thing happens with `GET /conversations/99999999999999999999` (via `get_conversation`), its delete POST, and the upload `vehicle_id`.
- It breaks criterion 8 (should show "Choose a vehicle from the list.") and criteria 24 and 27 (should be the same "Conversation not found." 404).
- No traceback leaks, because debug is off and the 500 page is plain.
- Fix in validators.py:

```diff
+MAX_DB_ID = 2**63 - 1
+
 def _vehicle_id(raw):
-    try:
-        return int((raw or "").strip())
-    except ValueError:
-        return None
+    raw = (raw or "").strip()
+    if not re.fullmatch(r"[0-9]{1,18}", raw):
+        return None
+    return int(raw)
+
+
+def valid_conversation_id(n):
+    return 0 < n <= MAX_DB_ID
```

  And in app.py, at the start of `conversation()` and `delete_conversation()`, only to call it:

```diff
-    if g.user["role"] != "driver":
+    if g.user["role"] != "driver" or not validators.valid_conversation_id(conversation_id):
         return conversation_not_found()
```

**F2. New lines count differently on the server and in the counter.**
- Browsers send each new line in a textarea as `\r\n`. `box.value` in chat.js counts it as one `\n`.
- Shift+Enter is a feature the spec allows, so a driver can type a multi-line question with the counter showing "500 / 500" in the normal color, and the server sees up to about 510 characters and refuses it.
- The server rule is still enforced. The problem is that the counter tells the driver something different from what the server decides, which is the kind of client/server mismatch Risk 2 warns about.
- Fix in validators.py:

```diff
 def validate_question(raw):
-    question = (raw or "").strip()
+    # Browsers send each new line as \r\n; count it once, as the counter does.
+    question = (raw or "").replace("\r\n", "\n").strip()
```

**F3. A short embedding response saves part of a manual.**
- `embed_manual` pairs pages with vectors using `zip`, which silently drops extras. If Gemini returns fewer vectors than texts in any batch, `save_manual` stores a manual with missing pages and shows it as "Ready".
- That goes against the rollback rule in CLAUDE.md under Fragile (a failed batch must leave no rows) and criterion 15.
- Vector size is never checked against 768 either.
- Fix in ai.py:

```diff
 def embed_manual(pages):
     numbered = [(n, text) for n, text in enumerate(pages, start=1) if text]
     vectors = embed_documents([text for _, text in numbered])
+    if len(vectors) != len(numbered) or any(len(v) != EMBEDDING_DIMENSIONS for v in vectors):
+        raise ProviderError("embedding response did not match the pages sent")
     return [(n, text, vec) for (n, text), vec in zip(numbered, vectors)]
```

**F4.** The counter turns red at 502 when the input is 500 characters plus two spaces, but the server strips the spaces and accepts it. It also counts an emoji as 2, while Python counts 1. A possible fix is `Array.from(box.value.trim()).length` in chat.js. That is still within the counter behavior the spec allows.

**F5.** None of the POST forms carry a CSRF token, and the spec doesn't ask for one. `SESSION_COOKIE_SAMESITE="Lax"` (app.py:26) stops modern browsers sending the cookie on cross-site POSTs. I'd accept this for the demo. Ask the security agent if the team wants an opinion.

**F6.** `HttpOnly` is on (Flask's default) and `SameSite=Lax` is set. `Secure` is off, which is fine on localhost. If the app is ever served over HTTPS, set `SESSION_COOKIE_SECURE = not ai.TESTING` or read it from the environment.

**F7.** These are cosmetic and leak nothing.
- `abort(400)` for an unknown `action`, and the 405 on GET `/delete`, show Werkzeug's plain default pages.
- A driver who posts more than 50 MB anywhere sees "PDFs must be 50 MB or smaller."
- A possible fix is a 400 handler and a 405 handler that render `error.html`.

**F8.**
- `email`, `make`, `model`, and `trim` have no maximum length. On Werkzeug 3.1+, `MAX_FORM_MEMORY_SIZE` (500 KB by default) caps them; see the version command below.
- `0000` passes `\d{4}`. The spec only says "4-digit".
- Duplicates are caught regardless of case (`COLLATE NOCASE`, models.py:15-18) and with surrounding spaces stripped. "Land  Cruiser" with a double space still gets past "Land Cruiser". The spec doesn't say either way, so this is fine as it is.

**F9.**
- A named file with zero bytes gets "Choose a PDF to upload."; "Upload a PDF file." would be more accurate.
- A PDF with no text that can be pulled out reaches `MANUAL_FAILED` ("Try again"), which retrying won't fix.
- The spec covers neither case, so these are wording suggestions only.

### 4. Settings check

- `MAX_CONTENT_LENGTH`: OK. It comes from `validators.MAX_PDF_BYTES` (app.py:25), and the 413 handler re-renders `/admin/manuals` for admins. The limit covers the whole request, so a file of exactly 50 MB gets a 413 because of the multipart overhead. That is acceptable.
- `MAX_QUESTION_LENGTH`: OK at 500. chat.js:6 hardcodes the same 500.
- `MIN_PASSWORD_LENGTH`: OK at 8. A password of 8 spaces is accepted, because the spec only sets a length.
- `SIMILARITY_CUTOFF`: OK. It is 0.55 when `TESTING=1`. `REAL_SIMILARITY_CUTOFF` is also still 0.55 (ai.py:27), but the spec says it should have been tuned before CP2. Confirm the team tuned it and 0.55 was the result.
- Debug mode: OK. It comes only from `FLASK_DEBUG` (app.py:386, Flask CLI) and is not hard-coded (`test_debug_mode_not_hard_coded`).
- Secret key: OK. It is read from the environment and `RuntimeError` is raised if it is missing (app.py:28-30). There is no fallback outside `tests/conftest.py`.
- Session cookie: it holds only `user_id` plus flash messages. `HttpOnly` is on, `SameSite` is Lax, `Secure` is off (F6).

### 5. Leak check

- **Browser: clean.** There is no `|safe`, `Markup()`, or `autoescape false` (grep, plus `test_templates_do_not_disable_escaping`). Error pages show fixed messages. The 404 for someone else's conversation is identical to a missing one (E27). No driver-facing text says "chunk", "embedding", or "similarity". No hidden trusted fields: the `action` and upload `vehicle_id` fields are both re-checked on the server.
- **Gemini: clean.** `_gemini_answer` (ai.py:127-131) sends only the chunk text and the question. Embeddings send only text. The answer model is never called below the cutoff (ai.py:189-191), and only chunks at or above it are sent and cited.
- **Logs: clean, with one Needs check.**
  - `app.logger.warning` logs `str(exc)` for provider errors (app.py:256, 298, 374), and seed.py:55 prints it.
  - google-genai sends the key in a header, so it should not appear in error text, but this should be confirmed (command below).
  - Passwords, hashes, emails, and questions are never logged.
- **Repo: clean in the working tree.**
  - `.env` is in `.gitignore`.
  - The only key-like text is placeholders in README.md:70-77.
  - `*.db` is ignored.
  - Git history still needs checking (commands below).
  - Outside my scope: `knowledge/manuals/2024_Toyota_Camry_XSE.pdf` is not in `.gitignore` (only the 2026 file is), so the real manual is probably committed. That raises copyright and repo-size questions for the security agent or the team.

### 6. Tests to add (in tests/test_acceptance.py)

```python
@pytest.mark.parametrize("value", ["99999999999999999999", "-1", "1_0"])
def test_e08_vehicle_post_rejects_out_of_range_ids(client, db, value):
    signup(client)
    resp = choose_vehicle(client, value)
    assert "Choose a vehicle from the list." in page_text(resp)
    assert db("SELECT vehicle_id FROM users WHERE email = ?", (DRIVER_EMAIL,))[0]["vehicle_id"] is None


def test_e24_huge_conversation_id_is_404(driver):
    resp = driver.get("/conversations/99999999999999999999")
    assert resp.status_code == 404
    assert "Conversation not found." in page_text(resp)
    assert driver.post("/conversations/99999999999999999999/delete").status_code == 404


def test_e19_new_lines_count_once(driver, db):
    question = ("a" * 49 + "\r\n") * 10  # 500 as the browser counts, 510 as sent
    resp = ask(driver, question)
    assert "Questions must be 500 characters or fewer." not in page_text(resp)


def test_e19_surrounding_spaces_do_not_count(driver, db):
    ask(driver, "  " + "a" * 500 + "  ")
    assert db("SELECT 1 FROM messages WHERE sender = 'driver' AND content = ?", ("a" * 500,))


def test_e15_short_embedding_response_rolls_back(admin, db, ids, monkeypatch):
    import ai
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    before = (db.count("manuals"), db.count("chunks"))
    real = ai.embed_documents
    monkeypatch.setattr(ai, "embed_documents", lambda texts: real(texts)[:-1])
    resp = upload_manual(admin, se_id)
    assert "The manual could not be processed. Try again." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == before


@pytest.mark.parametrize("fields", [("   ", "Camry", "2025", "SE"),
                                    ("Toyota", "Camry", "202", "SE"),
                                    ("Toyota", "Camry", "20255", "SE")])
def test_e11_add_vehicle_rejects_blank_and_wrong_length_year(admin, db, fields):
    before = db.count("vehicles")
    assert "Enter make, model, a 4-digit year, and trim." in page_text(add_vehicle(admin, *fields))
    assert db.count("vehicles") == before


def test_e12_upload_rejects_corrupt_pdf(admin, db, ids):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    before = (db.count("manuals"), db.count("chunks"))
    resp = upload_manual(admin, se_id, "manual.pdf", b"%PDF-1.4 not really a pdf")
    assert "Upload a PDF file." in page_text(resp)
    assert (db.count("manuals"), db.count("chunks")) == before


def test_e10_upload_accepts_uppercase_extension(admin, db, ids):
    add_vehicle(admin, "Toyota", "Camry", "2025", "SE")
    se_id = ids.lookup(2025, "Toyota", "Camry", "SE")
    upload_manual(admin, se_id, "MANUAL.PDF")
    assert db("SELECT 1 FROM manuals WHERE vehicle_id = ?", (se_id,))


def test_e14_upload_for_missing_vehicle(admin, db):
    before = db.count("manuals")
    assert "Choose a vehicle from the list." in page_text(upload_manual(admin, 9999))
    assert db.count("manuals") == before


def test_e04_signup_trims_and_lowercases_email(client, db):
    signup(client, email="  Driver1@Test.COM  ")
    assert db("SELECT 1 FROM users WHERE email = ?", ("driver1@test.com",))
```

### 7. Commands for the main agent

| Command | What confirms or clears it |
|---|---|
| `python -m pytest` | All tests pass now. After adding the section 6 tests, F1 shows up as an `OverflowError` (TESTING propagates exceptions), F2 and F3 as assertion failures, and the rest should pass. |
| `python -c "import sqlite3; sqlite3.connect(':memory:').execute('select ?', (2**64,))"` | `OverflowError` confirms the cause of F1. |
| `git ls-files .env` and `git log --all --oneline -- .env` | Both empty clears the repo check. Any output means rotate both keys. |
| `git ls-files "*.db" knowledge/` | `.db` files listed means a database is committed. The PDF listed confirms the out-of-scope manual note. |
| `python -c "import werkzeug; print(werkzeug.__version__)"` | 3.1 or later means text fields are capped at 500 KB, which narrows F8. |
| Run the app with a bad `GEMINI_API_KEY`, ask a question, and read the console warning | No key text in the log line clears the log Needs check. |

### 8. Not checked

- The browser half of criteria 32 and 33: Thinking..., the red counter, Enter vs Shift+Enter, the confirm box. Check by hand as the spec describes.
- How the real dev server behaves on a 413 (the connection can reset before the page shows). Upload a file over 50 MB in a real browser.
- Real Gemini error text and real batch failures. Only the fake provider was traced.
- Out of my scope, for `senior-security-review`:
  - Login has no rate limit.
  - An unknown email returns faster than a wrong password because no hash is checked, so timing can reveal which emails exist even though the messages match.
  - PDF bomb and parsing cost.
  - The committed real manual.

**First fix:** F2, the one-line `\r\n` normalization in `validate_question`. It is the only finding a real driver can hit by normal use: Shift+Enter is a feature the spec allows, and the counter can show "500 / 500" while the server refuses the question. F1 and F3 come next and are also small. Applying any of these is up to you and the main agent.

Files referenced:
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\validators.py
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\app.py
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\ai.py
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\models.py
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\static\chat.js
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\tests\test_acceptance.py
- c:\Users\WillW\OneDrive\Desktop\AIDD\AiDD_Final_Project\.gitignore
````

## 6. Check of the run

Every item in the agent's output is marked right or wrong below. "Ran" means we ran it on November 4 with Flask's test client against a throwaway copy of the database and the fake AI provider (`TESTING=1`), with the app's error handling left on so we saw the page a visitor would see. Line numbers refer to commit `0f65434`, the code the agent read; the fixes made afterward moved some lines. Rows F1 to F9 end with what we changed afterward and the test that now passes.

| # | Agent's item | Right or wrong | Our reason (from the code or the running app) |
|---|---|---|---|
| V | Verdict: every input is validated on the server before it is saved or sent to Gemini; no Blockers or Highs; safe to demo | Right | Every route in `app.py` calls its validator before any `models.*` write or `ai.*` call (signup 163-165, vehicle 209-212, chat 250-254, follow-up 291-296, vehicle add 352-355, upload 365-379). We found no input that gets saved or sent unchecked. The only crashes are the huge-id 500 pages (F1), and nothing is saved or leaked when they happen. |
| I1 | Inventory: signup email and password go through `validate_signup`, the password is hashed and never echoed | Right | `app.py:162-169`: the validator runs, then `generate_password_hash`. The re-rendered form gets only the email back. E02, E03, E04 pass. |
| I2 | Inventory: signup never reads `role` | Right | `grep` of `app.py` shows no `form.get("role")`. `create_user` defaults to `driver`. E31 passes. |
| I3 | Inventory: login uses `clean_email` and `check_password_hash`, with one message for both failures | Right | `app.py:183-186`: one `render_template` call with "Email or password is incorrect." covers both branches. E06 passes. |
| I4 | Inventory: `/vehicle` `vehicle_id` goes through `validate_vehicle_choice`; huge ids fail (F1) | Right | `app.py:209`. Ran: id `9999` and `abc` give "Choose a vehicle from the list."; a 20-digit id gives a 500 page (see F1). |
| I5 | Inventory: the `/chat` question is validated before Gemini and before any row is saved | Right | `app.py:249-262`: `validate_question` returns before `answer()` and `create_conversation`. E18 and E19 pass. |
| I6 | Inventory: conversation routes use the URL id with `models.get_conversation(id, user_id)`; huge ids fail (F1) | Right | `app.py:276-285` and `309-315` pass `g.user["id"]` to every model call. The huge-id 500 is F1. E27, E28 and E30 pass. |
| I7 | Inventory: `/admin/manuals` `action` is only a dispatch; an unknown value gives `abort(400)`; both branches are behind `admin_required` | Right | `app.py:335-346`. Ran: `action=bogus` as admin gave 400. |
| I8 | Inventory: add-vehicle fields go through `validate_new_vehicle`; upload `vehicle_id` and file go through `validate_upload_vehicle` and `validate_pdf` | Right | `app.py:352` and `365-367`. E11, E12, E13a, E13b and E14 pass. |
| I9 | Inventory: the session `user_id` is reloaded from the database on each request | Right | `app.py:53-60`: `load_user` calls `models.get_user` and clears the session if the user is gone. |
| I10 | Inventory: no reads of `request.args`, `get_json` or cookies, and every field a form sends is read | Right | `grep` shows only `request.form` and `request.files` in `app.py`. We compared each `name=` in the templates (`email`, `password`, `vehicle_id`, `question`, `action`, `make`, `model`, `year`, `trim`, `manual`) with the 14 `form.get`/`files.get` calls. Each field matches. |
| F1 | Ids above 2^63-1 give a 500 instead of the spec message or a 404 (Medium, "Needs check") | Right | Ran: `POST /vehicle` with `99999999999999999999`, `GET /conversations/<that id>`, `POST .../delete` and an admin upload with that `vehicle_id` all returned 500 with the generic page "Something went wrong. Please try again." (no traceback). `9999` returns the correct 404. Cause: `sqlite3` raises `OverflowError` above 2^63-1 (the traceback in pytest points at `models.py:165` and `263`). This breaks criteria 8, 24 and 27 for such ids. `-1` and `1_0` are handled correctly (400 with the spec message). Extra: Arabic-Indic `١` is accepted as vehicle 1 because `int()` reads it. Severity Medium is fair: no data leaks, only a wrong page. Fixed: `validators.py` now accepts only 1 to 18 ASCII digits and `app.py` sends oversized conversation ids to the normal 404. `test_e08_vehicle_post_rejects_ids_that_are_not_plain_numbers` (including `١`), `test_e14_upload_for_a_missing_vehicle_is_refused` and `test_e24_a_conversation_id_too_big_for_the_database_is_a_404` now pass. |
| F2 | The server counts each new line as 2 characters but the counter counts 1 (Medium) | Right | `static/chat.js:14` counts `box.value.length`, and `validators.py:94` only strips. Ran: 491 letters plus 9 new lines is 500 by the counter's count. Posted with `\r\n` between lines (509 characters) it got 400 "Questions must be 500 characters or fewer."; the same text with `\n` was accepted (302). Its proposed test `test_e19_new_lines_count_once` failed on that code. Small error in the agent's comment: it says 510 sent, but the trailing new line is stripped, so it is 508. The failure holds. The test client sends the `\r\n` that the HTML form spec says browsers send. Fixed: `validate_question` now turns `\r\n` into one new line, and `test_e19_a_new_line_counts_once_like_the_live_counter` passes. We have not tried it by typing in a browser. |
| F3 | A short embedding response saves part of a manual (Medium) | Right | Ran: we made `ai.embed_documents` return one vector too few for the 3-page sample. The upload succeeded (302), the `manuals` row says 3 pages, only pages 1 and 2 were saved as chunks, and `/admin/manuals` shows "Ready". Five-float vectors were also saved. Cause: `zip` in `ai.py:164-166` with no length check. Caveat: we only simulated it, and have not seen Gemini return a short list. Its test `test_e15_short_embedding_response_rolls_back` failed on that code. Fixed: `ai.py` now raises a provider error when the number or size of the vectors is wrong, so the upload rolls back; `test_e15_a_short_embedding_reply_rolls_back_the_upload` and `test_e15_wrong_size_embeddings_roll_back_the_upload` pass. |
| F4 | The counter counts surrounding spaces and emoji differently from the server (Low) | Right | Ran: `"  " + "a"*500 + "  "` was accepted (302) and saved with length 500. The counter reads `box.value.length`, which is 504 and turns red. `node` confirms `"\u{1F600}".length` is 2, while Python counts 1. Fixed: `chat.js` now counts `Array.from(box.value.trim()).length`; `test_e19_spaces_around_the_question_do_not_count` covers the server side. |
| F5 | No CSRF tokens on the forms; `SameSite=Lax` limits it (Low) | Right | `grep -i csrf` finds nothing in `app.py` or the templates. Ran: the signup response sets `SameSite=Lax`. The spec does not ask for CSRF protection. The security agent found the same gap independently. Changed: `app.py` now refuses a POST whose `Sec-Fetch-Site` header says it came from another site; `test_e29_a_post_from_another_site_is_refused` passes. This is a header check, not a CSRF token. |
| F6 | `SESSION_COOKIE_SECURE` is not set (Low) | Right | Ran: `Set-Cookie: session=...; HttpOnly; Path=/; SameSite=Lax`, with no `Secure`. That is fine on `127.0.0.1` over HTTP. Changed: `SESSION_COOKIE_SECURE=1` in `.env` now turns it on; it stays off for the local demo. |
| F7 | 400 and 405 use Flask's default pages; a driver's 413 shows the PDF message (Low) | Right | Ran: admin `action=bogus` gave 400 and `GET /conversations/1/delete` gave 405, and both pages are Werkzeug's plain pages, not our `error.html`. A driver posting over the size limit to `/chat` (we lowered the limit to test) got 413 with "PDFs must be 50 MB or smaller." Fixed: 400 and 405 now render `error.html`, and a driver's 413 gets a general message; `test_e29_an_unknown_admin_action_shows_a_plain_400_page`, `test_e25_get_on_delete_shows_a_plain_405_page` and `test_e13_a_driver_posting_too_much_is_not_told_about_pdfs` pass. |
| F8 | No length cap on email, make, model, trim; year `0000` accepted; Werkzeug 3.1+ caps text fields at 500 KB | Partly wrong | Right: ran year `0000` (accepted), a 100,000-character make (accepted), a 5,000-character email (accepted), and an inner double space `Cr  uiser` (accepted as a new vehicle). Duplicates differing only by case or trailing space are rejected ("This vehicle already exists."), as it says. Wrong: the 500 KB cap. We run Werkzeug 3.1.9 and a 600,000-character make was accepted (302). Fixed: `validators.py` now caps email at 254 characters and make, model and trim at 50, refuses a year starting with 0, and collapses repeated spaces; `test_e02_signup_rejects_an_overlong_email`, `test_e11_add_vehicle_rejects_blank_short_and_oversized_fields` and `test_e11_extra_spaces_do_not_make_a_new_vehicle` pass. |
| F9 | Unclear messages: empty file says "Choose a PDF"; a PDF with no text says "Try again" (Low) | Right | Ran: a 0-byte `empty.pdf` gave 400 "Choose a PDF to upload." A one-blank-page PDF gave 400 "The manual could not be processed. Try again." with no `manuals` row (`app.py:376-377`). Retrying won't fix that second case. The spec covers neither. Fixed: an empty file now gets "Upload a PDF file." and a PDF with no text gets its own message (departure 2 in section 3); `test_e12_a_chosen_file_with_no_bytes_is_not_a_pdf` and `test_e12_a_pdf_with_no_readable_text_is_refused_with_a_clear_message` pass. |
| F10 | Several edge cases have no tests (Low) | Right | The test list shows E08 covers only `9999`, `abc` and the RAV4, E12 only `.docx` and text-as-`.pdf`, and E11 only three cases. We ran all 14 of its proposed tests in a scratch copy: 10 passed (the behavior is already right, so these are coverage gaps), and 4 failed on the real bugs F1 (2 tests), F2 and F3. Versions of all 14 are now in `tests/test_review_findings.py` (section 2) and pass. |
| S1 | `MAX_CONTENT_LENGTH` comes from `validators.MAX_PDF_BYTES`; the 413 handler re-renders `/admin/manuals`; exactly 50 MB gets a 413 | Right | `app.py:25` and `133-138`. Ran: the config value equals 52,428,800, and a PDF of exactly 50 MB returned 413 with the PDF message, because the multipart overhead pushes the request over the limit. |
| S2 | `MAX_QUESTION_LENGTH` is 500 and `chat.js:6` hardcodes the same 500 | Right | `validators.py:14` and `chat.js:6` both read 500. E19 passes. |
| S3 | `MIN_PASSWORD_LENGTH` is 8; a password of 8 spaces is accepted | Right | `validators.py:13`. Ran: an 8-space password signed up (302). The spec only sets a length. |
| S4 | `SIMILARITY_CUTOFF` is 0.55 under `TESTING=1`; `REAL_SIMILARITY_CUTOFF` is also still 0.55 and should have been tuned | Right | Ran: `ai.SIMILARITY_CUTOFF` is 0.55 and `ai.REAL_SIMILARITY_CUTOFF` is 0.55 (`ai.py:27-28`). We listed this as a departure in section 3. |
| S5 | Debug mode comes only from `FLASK_DEBUG` and is not hard-coded | Right | `app.py:386` reads `os.environ.get("FLASK_DEBUG")`. `test_debug_mode_not_hard_coded` passes. |
| S6 | The secret key is read from the environment, the app refuses to start without it, and there is no fallback | Right | Ran: in a clean copy with no `.env`, `import app` raised "Set FLASK_SECRET_KEY in your .env file." `grep` finds no fallback value outside `tests/conftest.py`. |
| S7 | The session cookie holds only `user_id` plus flash messages; `HttpOnly` on, `SameSite` Lax, `Secure` off | Right | Ran: we decoded the cookie. After login the keys are `['user_id']`; after logout with a flash they are `['_flashes']`. Flags as in F6. |
| L1 | Leak, browser: no `\|safe`, `Markup()` or `autoescape false`; fixed error messages; no jargon; no hidden trusted fields | Right | `grep` of templates and `app.py` finds none of those. Jargon words appear only as variable names in `app.py`, never in a template or a message. The only hidden inputs are `action` (`admin_manuals.html:37` and `55`), and `app.py:341-346` handles it. The upload `vehicle_id` is a `<select>` that `validate_upload_vehicle` re-checks. E21 and E27 pass. |
| L2 | Leak, Gemini: only the question and chunk text are sent; the answer model is not called below the cutoff | Right | `ai.py:123-131` sends the chunk text and the question; `ai.py:103-117` sends only texts. `ai.py:189-191` returns the "I'm not sure" reply before any call when no chunk passes the cutoff. E17 passes. |
| L3 | Leak, logs: nothing sensitive is logged; one "Needs check" that the API key can't appear in the logged error text | Right | `grep` finds only three `app.logger.warning(... exc)` calls and the `seed.py` prints. Ran the "Needs check": we called `ai.embed_query("hello")` once with a made-up key. The error text that `app.py` would log was "embedding failed: 400 INVALID_ARGUMENT ... API key not valid", and it contained neither the key nor its first 8 characters. This was a real call to Google with a made-up key. Not tested: the text of a real 429. |
| L4 | Leak, repo: `.env` ignored, no keys in the working tree, `*.db` ignored, real manual probably committed | Right | `git ls-files .env` and `git log --all --oneline -- .env` are both empty. `git grep` for `AIza...` finds nothing. `git check-ignore` shows `mycarai.db` ignored by `*.db`. `git ls-files knowledge/` lists `2024_Toyota_Camry_XSE.pdf`, so the manual is committed. We keep it so the peer auditors can load the real manual; Toyota publishes it free on its owner website, and we will remove it if the instructor asks. |
| T | Tests to add (10 tests, 14 cases) | Right, with one inaccuracy | They run as written with the existing helpers. Result on that code: 10 cases pass, 4 fail (details in F10). The inaccuracy is the comment in the new-line test (508 sent, not 510). |
| C1 | Command: `python -m pytest` shows F1 as `OverflowError`, F2 and F3 as assertion failures | Right | That is what happened: two `OverflowError` failures at `models.py:165` and `263`, and two assertion failures. The unchanged suite is 62 passed. |
| C2 | Command: the `sqlite3` one-liner raises `OverflowError` | Right | Ran an equivalent: "Python int too large to convert to SQLite INTEGER". |
| C3 | Command: `git ls-files .env` and `git log --all --oneline -- .env` | Right | Both returned nothing. |
| C4 | Command: `git ls-files "*.db" knowledge/` | Right | No `.db` files; one PDF. |
| C5 | Command: `python -c "import werkzeug; print(werkzeug.__version__)"` | Wrong | On Werkzeug 3.1.9 this raises `AttributeError: module 'werkzeug' has no attribute '__version__'`. The working command is `importlib.metadata.version("werkzeug")`. |
| C6 | Command: run the app with a bad `GEMINI_API_KEY` and read the log | Right | We did the equivalent (see L3). |
| N1 | Not checked: the browser half of criteria 32 and 33 | Right | The test client runs no JavaScript. Not done before submission; criteria 32 and 33 are marked Partly met. |
| N2 | Not checked: a real 413 over a real connection | Right | We only used the test client and did not upload an over-50 MB file in a browser (noted under criterion 13). |
| N3 | Not checked: real Gemini errors and batch failures | Right | We only used the fake provider, plus one invalid-key call. |
| N4 | Out of scope: no rate limit on login, timing reveals which emails exist, PDF bombs, the committed real manual | Partly verified | Code reading supports the timing claim: `app.py:185` skips `check_password_hash` when the email is unknown, and we have not measured it. We did not test PDF bombs. The security agent raised the rate limit. The committed manual is confirmed (L4). |
| Z | First fix: F2, the one-line `\r\n` normalization | Right, with a caveat | It is the only finding a driver can hit by normal use (Shift+Enter). F1 can only be hit by editing the request by hand, and F3 needs the provider to misbehave. When we checked, no fix had been applied. Fixes for F1 to F9 were then made, and the suite is now 102 passed (section 1). |

## 7. Connections list

One line for each MCP server, plugin, extension, or API key our agents used during the build.

| Connection | What it could reach | Added by |
|---|---|---|
| Claude Code (VS Code extension), Claude Opus 5.5 and Claude Sonnet 5.5 | Read, write, and run commands in the local project folder | Will Webster |
| Google Gemini API key (`GEMINI_API_KEY` in each member's own `.env`) | `gemini-embedding-001` and `gemini-3.5-flash-lite` on the free tier. The app sends only question text and manual page text. | Each team member, their own key |
| GitHub (repo `willyweb31/...` via `git`/`gh` and the GitHub MCP server) | Read and write the team repository, its branches, pull requests, and Actions | Will Webster |
| GitHub Actions ([.github/workflows/tests.yml](.github/workflows/tests.yml)) | Runs `pytest` on each push and pull request to `main`, with `TESTING=1` and a dummy secret key and no Gemini key | Will Webster |
| No other connections | Trey Adleta, Sang Lian and Ryan Ballard used no agents, MCP servers or keys beyond their own Gemini key (row above). | n/a |

## 8. Build note (AI Use Note)

**Who built what.** Claude Code in VS Code, running Claude Opus 5.5, built the application from the spec and `CLAUDE.md`. That covers `app.py`, `models.py`, `validators.py`, `ai.py`, `seed.py`, the templates, and `static/chat.js` on the `build-app` branch (merged November 3), and the acceptance tests and GitHub Actions workflow (October 27). Claude drafted the spec from our Design Thinking materials, and a separate Claude agent audited it against the CP1 rubric. The sunset color scheme in `static/style.css` was added on November 4. After the CP3 audit, Claude Code made the fixes for findings F1 to F9 and wrote `tests/test_review_findings.py`, and Claude Sonnet 5.5 helped draft this write-up. Will Webster ran the Claude Code sessions and made every commit; Trey Adleta, Sang Lian and Ryan Ballard reviewed the spec, the test results and this write-up. The suite ran on each push.

**Where an agent departed from our intent.** Our three custom subagents (`senior-security-review`, `validator-reviewer`, and `senior-UI&UX-designer-agent`) were meant to review and suggest, and the team was to decide on every change. Instead, they made the changes themselves. None of the agent files had a `tools:` line, so each one inherited every tool the main agent had, including Edit, Write, and Bash. The instructions in the files also allowed edits. The security agent said "Only apply edits if the user explicitly asks". The validator and design agents offered to "apply the fixes" and then run `pytest`. We found it on November 4 while preparing CP3: changes showed up in the working tree that we had asked the agents only to review, and reading the three agent files against the CP3 requirement that hard limits go in the tools line showed that none of them had one.

**What we changed.** We changed both the agent files and the context file:

- **Agent files.** All three now have `tools: Read, Grep, Glob`. We rewrote their instructions so they cannot edit or run anything. Each one now ends its report with "Commands for the main agent", listing the exact commands to run and what result confirms each finding.
- **Context file.** We added a rule to `CLAUDE.md` that subagents are read-only, and that only the main agent edits files, after the team approves.
