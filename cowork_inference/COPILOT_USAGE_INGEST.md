# Copilot usage-export ingest

**Status:** PARTIAL. **Org-wide Cowork optimization:** **OPEN.**
**Observer:** Grok terminal. Not Grok Bot.
**Code:** `cowork_inference/copilot_usage.py`, called from `cowork_inference/ingest_usage.py`.

## The plain intended outcome

**Goal.** `ingest_usage.py` can read a real Microsoft 365 Copilot usage-by-user
export and turn it into per-seat rows and counts that anyone can compare with the
Microsoft 365 admin center.

**Why it is needed.** `ingest_usage.py` used to pass through only a
hand-copied `snapshot.json`, so `license_rightsizer.py` and every later step had no
Copilot usage data to stand on. A reader that works on a real export is the first
piece that can be tested on Copilot. It was checked once on one real tenant export
(2026-10-26, 28-day window ending 2026-10-25): 62 enabled users and 59 active users,
and the prompt total, matched the admin center tiles. `license_rightsizer.py` and
`run_all.py` now use the reader's counts (section below).

**How it is checked.**
1. Synthetic fixtures with known counts (`tests/fixtures/copilot_usage/`) are run in
   `tests/test_copilot_usage.py`. The parser must return exactly the counts known
   from the fixture file.
2. Every run accounts for every row: `input_rows == accepted + excluded`, and each
   excluded row has a reason.
3. On real data, the totals printed by the script are compared with the totals the
   admin center shows for the same report window (steps below).

**Goal of the admin center header update.** The reader recognises every column of
the real admin center "Microsoft 365 Copilot usage by user" export, so a real run
leaves `columns_unrecognised` empty (apart from Display Name, which is never read).
**Why.** A real run on 2026-10-26 left the two app columns and the four numeric
columns unrecognised. **How it is checked.** The real header row is the first line
of `tests/fixtures/copilot_usage/synthetic_admin_center_usage_by_user.csv` (invented
rows, UTF-8 BOM) and `tests/test_copilot_usage.py` asserts every header resolves.

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
(URLs below). **OBSERVED** means the header was seen in a real admin center export
taken on 2026-10-26 (one tenant). **OPEN** means the name is a metric label or a v2 field from those
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
| `m365_app` | none | OBSERVED: `Last activity date of Microsoft 365 Copilot (app) (UTC)` |
| `edge` | none | OBSERVED: `Last activity date of Edge (UTC)` |
| `prompts_all_apps`, `prompts_chat_work`, `prompts_chat_web`, `active_usage_days_all_apps` | none | OBSERVED: `Prompts submitted for All Apps`, `Prompts submitted for Copilot Chat (work)`, `Prompts submitted for Copilot Chat (web)`, `Active Usage Days for All Apps` (counts, see below) |

### Observed on a real export (2026-10-26)

One real admin center "usage by user" export, one tenant, 28-day window ending
2026-10-25. Status: OBSERVED. The header row is, in order: Report Refresh Date,
User Principal Name, Display Name, Last Activity Date, Report Period, the four
numeric columns above, then `Last activity date of <app> (UTC)` for Copilot Chat
(work), Copilot Chat (web), Teams Copilot, Word Copilot, Excel Copilot, PowerPoint
Copilot, Outlook Copilot, OneNote Copilot, Loop Copilot, Microsoft 365 Copilot
(app) and Edge. The file begins with a UTF-8 BOM, which the reader strips. The
reader's totals matched the admin center: 62 enabled users, 59 active users. No
tenant name, user name or email is kept in this repo.

The four numeric columns are read as **admin center counts, not tokens, not cost,
not savings**: for each, the sum over users and the number of users with a value
above zero. A blank, negative or non-integer value is left out of the sum, counted
in `values_excluded_from_sum`, and reported as a warning. No value is guessed.
They are never stored per user.

Not verified and left OPEN:
- The admin center header text for other tenants and report windows. One real
  export is OBSERVED; the Graph CSV headers for the v2 columns are still OPEN.
- The exact header text of the v2 columns in a Graph CSV.
- The date format is not recorded as checked. The reader accepts `YYYY-MM-DD`
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

Every data row is either accepted or excluded with one reason. Checks run in this order (`future_date` sits before the duplicate check, so a future-dated row does not reserve its id):

| Reason | Meaning |
|---|---|
| `malformed_row` | A JSON item that is not an object. |
| `missing_user_id` | Empty or blank user principal name. |
| `bad_date` | A non-empty date field that is not an ISO date. Empty means no activity and is valid. |
| `future_date` | The last activity date, or an app date, is after the reference date (`as_of`). It is never counted as active. Shown in `excluded_by_reason` only when a row was excluded for it. |
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
| `active_per_app.<app>.active_in_window` | Same, using that app's last activity date. `null` when the export has no column for that app (unknown, not zero) | Adoption by app, active users |
| `active_per_app.<app>.with_activity_date` | Rows with a date for that app. `null` when the export has no column for that app | none |
| `never_active` | Rows with no last activity date | none |
| `admin_center_counts.<field>` | Sum and users with a value above zero for the numeric prompt and usage-day columns | the same columns; counts only, not tokens, not cost, not savings |
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

**Last activity when the overall date is blank or missing.** If a row's overall
Last Activity Date is blank, the reader uses that user's latest per-app date, so a
user with recent Word activity is not counted as never active or idle. The count is
reported as `last_activity_derived_from_apps`, with a warning. If the overall
column is missing, every row uses its per-app dates. If the file has neither the
overall column nor any app date column, `never_active`, `users_with_activity_date`,
`active_users_in_window` and `idle_seats` are `null` (unknown) and the run warns
`no_activity_columns`; map a column with `--map last_activity=Header`.
*Goal:* a seat is idle only when the file shows no activity. *Why:* a blank overall
date next to a recent app date was counted idle. *Checked by:* the tests
`test_blank_overall_date_with_recent_app_date_is_not_idle_or_never_active`,
`test_missing_overall_column_derives_from_app_columns` and
`test_no_activity_columns_means_unknown_not_idle`.

**Dates after the reference date.** A last activity or app date later than `as_of`
used to pass the window check (the upper bound only). Such a row is now excluded as
`future_date`, with a warning, and the accounting stays balanced. The window check
also requires the date to be on or before `as_of`. Rows with normal dates are
unchanged. *Checked by:* `test_future_last_activity_is_excluded_and_never_counted_active`,
`test_future_date_uses_a_caller_supplied_as_of_and_does_not_reserve_the_id` and
`test_normal_rows_report_no_future_date_key`.

**Idle seats.** `idle_days` has no default. The right threshold is a policy choice:
**value to be set by the data owner.** Without it, `idle_seats` is `null`. An idle
count is a list of seats to look at, not a decision to remove a licence.

## Seats, idle seats, and `run_all`

**Goal.** `license_rightsizer.py` and `run_all.py` use the counts from a real export
instead of only the sponsorship snapshot. A **seat** is one assigned Microsoft 365
Copilot license. An **idle seat** is a seat whose holder has no activity, or whose
last activity is at least `idle_days` days before `as_of`.
**Why.** The reader's counts had been checked on one real export, but the
rightsizer and the receipt still described usage as snapshot-only.
**How it is checked.** `tests/test_wire_real_export.py` runs invented exports through
`run_all` and `license_rightsizer`. It checks the counts against values known from the
fixture files, that the no-argument receipt equals a stored copy of the old one
(`tests/fixtures/cowork_inference/snapshot_receipt.json`), that no name, email or salt
appears in the receipt, and that idle seats stay `null` without a threshold.

Run it from the repo root:

    export COWORK_INFERENCE_SALT='<a long random string for this tenant>'
    python3 -m cowork_inference.run_all --copilot-export /path/to/export.csv [--window-days 28] [--as-of YYYY-MM-DD] [--idle-days N]

- `idle_days` has no default. Without it `idle_seats` is `null` and `idle_policy` reads
  "value to be set by the data owner". Idle at exactly `idle_days` days is the same
  window-boundary question as above, and stays OPEN.
- The seats counted are the rows in the export. Unassigned licenses are not in the
  export, so `unassigned_licenses` is `null` and is not inferred from it.
- `seats_not_active_in_window` is a plain subtraction. It is not the same as idle seats
  or never-active seats.
- Prompt counts are admin center counts, not tokens, not cost, not savings. The
  sponsorship total is not a Copilot seat cost.
- The receipt holds counts and salted pseudonyms only. The per-user list is left out
  of `run_all`; `idle_seat_pseudonyms` lists idle seats by pseudonym. The salt is read
  only from `COWORK_INFERENCE_SALT`, there is no flag for it, and it is never stored.
- `per_app_reconciliation` has one entry per app: the column header matched, its
  status, `active_users` in the window and `users_with_activity_date`. Compare each
  with the matching admin center tile for the same window. That comparison is the
  data owner's step; no tile number is stored in this repo. An app with no column in
  the export shows `null`.
- Status stays PARTIAL. Org-wide Cowork optimization stays **OPEN**. No savings figure.

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
`python3 -m pytest tests/test_copilot_usage.py tests/test_wire_real_export.py`.

## Still OPEN

- Admin center export headers beyond the one observed tenant, and the date format (above).
- The window boundary rule and the idle boundary (above).
- Per-app comparison with the admin center tiles: the data owner's step.
- Tokens, cost, and savings: this report has none. Cowork's My tasks page showed no token meter.
- Analytics CSV, Studio/AOAI logs, exact prompts, and the cross-team prompt corpus.
- Org-wide Cowork optimization.
