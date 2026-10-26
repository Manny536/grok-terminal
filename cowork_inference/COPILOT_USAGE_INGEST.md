# Copilot usage-export ingest

**Status:** PARTIAL. **Org-wide Cowork optimization:** **OPEN.**
**Observer:** Grok terminal. Not Grok Bot.
**Code:** `cowork_inference/copilot_usage.py`, called from `cowork_inference/ingest_usage.py`.

## The plain intended outcome

**Goal.** `ingest_usage.py` can read a real Microsoft 365 Copilot usage-by-user
export and turn it into per-seat rows and counts that anyone can compare with the
Microsoft 365 admin center.

**Why it is needed.** Until now `ingest_usage.py` only passed through a
hand-copied `snapshot.json`. It had no Copilot usage data to test against, so
`license_rightsizer.py` and every later step had nothing to stand on. A reader
that works on a real export is the first piece that can be tested on Copilot.

**How it is checked.**
1. Synthetic fixtures with known counts (`tests/fixtures/copilot_usage/`) are run in
   `tests/test_copilot_usage.py`. The parser must return exactly the counts known
   from the fixture file.
2. Every run accounts for every row: `input_rows == accepted + excluded`, and each
   excluded row has a reason.
3. On real data, the totals printed by the script are compared with the totals the
   admin center shows for the same report window (steps below).

**What this does not do.** It does not measure tokens, cost, or savings. It does
not read prompts. The snapshot fallback is unchanged and still returns PARTIAL.
Without an export, `ingest()` returns exactly what it returned before.

## What is read, and what is not stored

| Item | Handling |
|---|---|
| User principal name | Replaced by a salted HMAC-SHA256 pseudonym (first 32 hex characters). The salt is passed as an argument or read from the `COWORK_INFERENCE_SALT` environment variable. It is never written to the output or to disk. There is no default salt; without one the script stops. |
| Display name | Never read. |
| Prompts | Not part of this report. Never read or stored. |
| Dates | Last activity date, report refresh date, and per-app last activity dates are kept as ISO dates. |

Use a different salt per tenant so pseudonyms cannot be linked across tenants.
Keep the salt somewhere other than this repo. If you change the salt, pseudonyms
change, so keep it fixed for any comparison across runs.

Microsoft's own Graph example shows the user principal name and display name
already hashed when the tenant hides user details. The reader does not depend on
that. It hashes whatever identifier it receives.

## Column names

Headers are matched on a normalised key (lower case, letters and digits only), so
`Last Activity Date` (Graph CSV) and `lastActivityDate` (Graph beta JSON) are the same column.

**VERIFIED** means the exact name appears in the Microsoft Learn Graph reference
(URLs below). **OPEN** means the name is a metric label or a v2 field from those
pages, but the exact header in a downloaded file was not checked. The script
reports, for each field, which header it matched and with which status
(`column_resolution` in the output). Any column can be overridden with
`column_map` (Python) or `--map field=Header` (command line), and the result is
then marked CONFIGURED. A configured header that is not in the file stops the run.

| Field | VERIFIED header (Graph v1 CSV / beta JSON) | OPEN aliases |
|---|---|---|
| `user_id` | `User Principal Name` / `userPrincipalName` | `User name` (admin center label) |
| `report_refresh_date` | `Report Refresh Date` / `reportRefreshDate` | |
| `report_period` | `Report Period` / `copilotActivityUserDetailsByPeriod[].reportPeriod` | |
| `last_activity` | `Last Activity Date` / `lastActivityDate` | `Last activity date (UTC)` |
| `teams` | `Microsoft Teams Copilot Last Activity Date` | `Last activity date of Teams Copilot (UTC)` |
| `word`, `excel`, `powerpoint`, `outlook`, `onenote`, `loop` | `<App> Copilot Last Activity Date` | `Last activity date of <App> Copilot (UTC)` |
| `copilot_chat` | `Copilot Chat Last Activity Date` | |
| `copilot_chat_work`, `copilot_chat_web` | none | `Copilot Chat (work) Last Activity Date`, `Copilot Chat (web) Last Activity Date`, and the admin center labels |
| `m365_app`, `edge`, `copilot_agent` | none | `Microsoft 365 Copilot Last Activity Date`, `Edge Last Activity Date`, `Copilot Agent Last Activity Date`, and the admin center labels |

Not verified and left OPEN:
- The exact header text of the admin center **Export** CSV. The admin center page
  documents the table by metric label, not by file header.
- The exact header text of the v2 columns in a Graph CSV.
- The date format in the admin center export. The reader accepts `YYYY-MM-DD`
  (or an ISO date-time starting with that). Any other non-empty date is counted
  as `bad_date` and excluded, so a format difference shows up in the accounting.

Sources (read on 2026-10-26):
- Graph reference, v1 CSV headers, v2 field list, permission `Reports.Read.All`:
  https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/api/admin-settings/reports/copilotreportroot-getmicrosoft365copilotusageuserdetail
- Graph beta reference, JSON property names and CSV header list:
  https://learn.microsoft.com/en-us/graph/api/reportroot-getmicrosoft365copilotusageuserdetail?view=graph-rest-beta
- Admin center report, definitions of Enabled Users, Active Users, the user table and export:
  https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide

## Accounting

Every data row is either accepted or excluded with one reason. Checks run in this order:

| Reason | Meaning |
|---|---|
| `malformed_row` | A JSON item that is not an object. |
| `missing_user_id` | Empty or blank user principal name. |
| `bad_date` | A non-empty date field that is not an ISO date. Empty means no activity and is valid. |
| `duplicate_user_id` | The id (compared in lower case) was already accepted. The first row wins. A row excluded for another reason does not reserve its id. |

The output holds `input_rows`, `accepted`, `excluded`, `excluded_by_reason`, the
row numbers of excluded rows, and `balanced`. Row numbers start at 1 for the first
data row. No ids are listed.

## Aggregates, and the numbers to compare with the admin center

| Output | Meaning | Admin center counterpart |
|---|---|---|
| `enabled_users` | Accepted rows | Enabled Users (see the note below) |
| `users_with_activity_date` | Accepted rows with a non-empty last activity date | none; the date does not depend on the window |
| `active_users_in_window` | Last activity within `window_days` of `as_of` | Active Users for the same window |
| `active_per_app.<app>.active_in_window` | Same, using that app's last activity date | Adoption by app, active users |
| `active_per_app.<app>.with_activity_date` | Rows with a date for that app | none |
| `never_active` | Rows with no last activity date | none |
| `idle_seats` | No activity in the last `idle_days` days, or never active | none; this is a script output, not an admin center number |

`as_of` defaults to the latest Report Refresh Date in the file, and `window_days`
defaults to the single Report Period value, if the file has only one. Both can be
set by argument.

OPEN items for these counts:
- **Window boundary.** The script treats a user as active when
  `(as_of - last activity)` in days is below `window_days`. How the admin center
  counts the first and last day of the window was not checked. If the totals
  are off by users whose last activity falls on the boundary day, this is why.
- **Enabled Users.** The admin center page says the user table lists everyone
  licensed at any point in the past 180 days. `enabled_users` is the row count of
  the file, so it can differ from the Enabled Users card for the same window.
- **Active Users definition.** The admin center counts users who sent a prompt or
  took an intentional action in the window. The last activity date is the only
  signal in this report, so the two are expected to match only when both use the same window.

**Idle seats.** `idle_days` has no default. The right threshold is a policy choice:
**value to be set by the data owner.** Without it, `idle_seats` is `null`. An idle
count is a list of seats to look at, not a decision to remove a licence.

## How to test on real Copilot data

You need a Microsoft 365 admin role that can open usage reports (for example
Reports Reader or AI Administrator). Do not commit the export. Keep it out of the repo.

1. **Download the report.** In the Microsoft 365 admin center go to Reports, then
   Usage, then Microsoft Copilot, then Copilot, and open the Usage tab. Pick the
   window (7, 28, 90, or 180 days). In the table, select **Export**. Write down the
   **Enabled Users** and **Active Users** cards, and the per-app counts under
   **Adoption by app**, for that same window.
   Alternative with the same data: the Graph function
   `getMicrosoft365CopilotUsageUserDetail` (needs `Reports.Read.All` with admin
   consent). Save the response as a file. This repo makes no network calls.
2. **Choose a salt** and put it in your shell only:
   `export COWORK_INFERENCE_SALT='<a long random string for this tenant>'`
3. **Run it** from the repo root:
   `python3 -m cowork_inference.ingest_usage --export /path/to/export.csv --window-days 28`
   Add `--as-of YYYY-MM-DD` if the file has no Report Refresh Date column. Add
   `--idle-days N` only once the data owner has chosen N.
4. **Read the accounting first.** In the `copilot_usage_export` row, check
   `accounting.balanced` is true and look at `excluded_by_reason`. Rows excluded
   as `bad_date` mean the date format differs from what the reader accepts.
5. **Read `column_resolution`.** Every field you expect should show a header.
   Fields with status OPEN matched a label that was not verified. If a column you
   need shows ABSENT, pass `--map field=Header` using the header in your file.
6. **Compare totals with the admin center** for the same window:
   - `aggregates.enabled_users` against Enabled Users
   - `aggregates.active_users_in_window` against Active Users
   - `aggregates.active_per_app.<app>.active_in_window` against the app counts
7. **Record the result** as OBSERVED with the window, the date, and both sets of
   numbers, including any difference and your reading of the cause (for example the
   window boundary). A match supports the reader for that export. A mismatch is a
   finding to explain before anything else uses these counts.
8. **Delete the export** when done.

If you cannot get an export, the same checks run on the synthetic fixtures with
`python3 -m pytest tests/test_copilot_usage.py`.

## Still OPEN

- Exact admin center export headers and date format (above).
- The window boundary rule (above).
- Tokens, cost, and savings: this report has none. Cowork's My tasks page showed no token meter.
- Analytics CSV, Studio/AOAI logs, exact prompts, and the cross-team prompt corpus.
- Org-wide Cowork optimization.
