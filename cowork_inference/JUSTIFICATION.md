# Why these six scripts are narrowed

**Observer:** Grok terminal. Not Grok Bot.  
**Org repo:** not committed. `agreeya-org1-scout/CoWork-Inference` is unchanged by this pass.  
**Org-wide Cowork optimization:** **OPEN**.

The planned scripts in that repo expect ledgers this seat does not have: Graph Copilot usage reports, an Analytics CSV, Studio/AOAI logs, exact prompts, and a cross-team corpus (Marketing, Sales, Delivery, HR, IT, MISC). The scripts here run on the three Chrome surfaces that were open on 2026-10-23.

## What was visible

| Surface | What it actually is |
|---|---|
| Azure sponsorship balance | One seat. Cap $10,000. Card shows $2,007 used and $7,993 remaining. Offer active, 252 days left, window 13 Aug 2026–1 Jul 2027. Usage through 23 Oct 2026. |
| Azure sponsorship usage table | Same seat, 13 Aug 2026–24 Oct 2026, spend $2,006.78. One subscription row. No service or model split. The date boxes did not move to September. |
| Loop “Azure Sponsorship Spending” | Monthly sheet. Five rows, sum $4,920. Principal seat last posted $1,520 on 6 Oct 2026. One row is dated in September, and it is not the principal seat. Other seats are not copied into this public ledger. |
| Cowork, My tasks | September contains one task: “Create and Document Personal Skill,” last activity 25 Sep 2026. It produced research files and a skill file. It is not a usage export. Prompt text was not stored. |

The card ($2,007) and the usage table ($2,006.78) differ by rounding. The unposted gap versus the 6 Oct sheet is $486.78 over 17 days.

## What that gap is not

The meter is an Azure sponsorship total for Digital & App Innovation. It is not a Cowork token ledger. A linear daily rate is an assumption. No team owns a measured share. No script below emits a Cowork savings dollar.

## Script by script

| Planned script | Planned “In” | What can run now | Status |
|---|---|---|---|
| `ingest_usage` | Graph reports, Analytics CSV, Studio/AOAI logs | Balance card, usage-table total, September task count | PARTIAL |
| `license_rightsizer` | Usage plus licence assignments | Cap utilization for one seat. Empty reassignment list | NOT EVALUATED |
| `response_cache` | Prompt/response logs | One September title. Repeat rate unset | NOT EVALUATED |
| `prompt_compressor` | Prompts and grounding context | Zero prompts on hand | NOT EVALUATED |
| `model_router` | Request features | One subscription, no model mix | NOT EVALUATED |
| `savings_report` | Ledger plus usage | Live spend versus last posted monthly figure | PROPOSED burn, Cowork savings unset |

Teams stay **UNRESOLVED**. A cache, a compressor, or a router would need an opted-in export of prompts and a real inference meter. Those exports are not in this snapshot.
