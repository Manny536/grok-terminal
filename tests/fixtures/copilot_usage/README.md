# Synthetic Copilot usage fixtures

Every file here is invented. User ids are `user-NNN`, display names are
`Synthetic User NNN`, and no value comes from a real tenant. They follow the
column layout documented for the Microsoft Graph Copilot usage report and the
admin center report labels, so the parser can be tested offline.

Known counts (used by `tests/test_copilot_usage.py`):

| File | Rows | Notes |
|---|---|---|
| `synthetic_graph_v1.csv` | 10 | Report refresh 2026-10-20, period 28. 8 users with an activity date, 2 never active |
| `synthetic_messy.csv` | 8 | 2 accepted, 2 duplicate ids, 2 missing ids, 2 bad dates |
| `synthetic_graph_beta.json` | 4 | Graph beta JSON shape, period 7 |
| `synthetic_admin_center_labels.csv` | 3 | Admin center metric labels as headers (header text is OPEN) |
| `synthetic_header_only.csv` | 0 | Headers, no rows |
