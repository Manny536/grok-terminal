# VENDORED: OA probe (PROPOSED / ONGOING)

Source: cwi-main commit `97064b1` (branch `feat/oa-probe`, local; origin agreeya-org1-scout/CoWork-Inference).

## Upstream sha256 at that commit

- `kakeya_checks/causal.py` `56557f32deaab97a3674148d7c7cf1890ec0221b5babd7c82ac930b524ab207f`
- `kakeya_checks/oa_probe.py` `ac1caec7bc27d192e9897029eb22556668f70c4f85d5fe6b64a90a22a7501cbc`
- `docs/OA_PROBE_PREREG.json` `0bbecb50e7ff3dc27ee1d0b7fb5869ae7ee76043829ed43f746b5dd4ac7a8138`
- `docs/OA_PROBE_RESULTS_v2.json` `8c7e1db61c65bf17b39252725224e3227d9788ca04db7b5b0ae133797c382ace`

## sha256 of the files as vendored here

- `docs/OA_PROBE.md` `6c11cebba7c5ec36fdefb07990440375204852d607e66f5d6f4352f8e29f3d38`
- `docs/OA_PROBE_EXPLORATORY_C.json` `e4a3396c80fbfa69ebedaedb42fdedb49955399488befa7d4f3f030ce7b99978`
- `docs/OA_PROBE_PREREG.json` `0bbecb50e7ff3dc27ee1d0b7fb5869ae7ee76043829ed43f746b5dd4ac7a8138`
- `docs/OA_PROBE_RESULTS.json` `7ddef9db43bc8f67023d9e247a3476ed567b4802b4fa2fcf8097f62f13360563`
- `docs/OA_PROBE_RESULTS_v2.json` `8c7e1db61c65bf17b39252725224e3227d9788ca04db7b5b0ae133797c382ace`
- `probes/oa/__init__.py` `12590f3fe1cc30f2b5837bda8ef980097587e7d58e293fab3eacd096c6ea0a93`
- `probes/oa/causal.py` `56557f32deaab97a3674148d7c7cf1890ec0221b5babd7c82ac930b524ab207f`
- `probes/oa/oa_probe.py` `ac1caec7bc27d192e9897029eb22556668f70c4f85d5fe6b64a90a22a7501cbc`
- `scripts/oa_experiment.py` `678a0e621b0749243f8f39403f8249ac5704b9b56a2fb80d7b4f27dc8da9672a`
- `scripts/oa_mutation_smoke.py` `1ad5fbc11a9e4abd88a2f1442fbabd2b708313a1ffed7e57b36610ab1f0803c9`
- `tests/oa_mutants.py` `33f2bdeb7c627993dbc2fd015581c66828c250448c487cc5cfc632ce9f23b363`
- `tests/test_oa_probe.py` `7167c61392fd7ae8e568e73b28a46e89386e4aa1e8522a5af4353788e9ae7e88`

Byte-identical to upstream: docs/OA_PROBE_PREREG.json, docs/OA_PROBE_RESULTS_v2.json (tests pin the prereg hash and compare outcomes to the committed results).
Changed on vendoring: import paths, test-dir paths; causal.py and oa_probe.py otherwise unmodified.

ANALOGY ONLY: the paper (arXiv:2501.02305) is about hash tables, not agents; nothing here certifies an agent or closes L²_C.

## Pylint follow-up

Each of causal.py and oa_probe.py has one inline pylint pragma added, with a reason (a deliberate (b, a) argument order, and a loop that returns or raises). No logic changed. Current sha256:
- `probes/oa/causal.py` `8c00efe04bbe332387b0738c028ab28101f30e9f62ee5048b811b53cabd5bc23`
- `probes/oa/oa_probe.py` `aa8c2936f970cecf7f7050d35cc4e9f9bf69e08a6f4d0b83a541c4a9c35f1f7a`
