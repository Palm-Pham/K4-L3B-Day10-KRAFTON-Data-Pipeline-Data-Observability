# Step 6 — Final acceptance summary

Date: 2026-09-26. **Both entrypoints passed the approved isolated rerun. All 40 artifact checks passed. Two additional agent/provider defects were fixed with explicit approval, and the affected offline checks passed. Submission still has student-owned and unverified items listed below; full marks are not claimed.**

The user approved isolated outputs and asked to skip TEAM.md. TEAM.md is recorded as waived for this task, not as a verified complete submission document. No student identities or contributions were invented.

## 1. Submission checklist

Statuses reflect evidence gathered during Step 6, not earlier summaries. Paths prefixed `RUN/` below mean `acceptance_runs/step6_20260926_01/`.

| Check | Status | Evidence |
| --- | --- | --- |
| Baseline entrypoint exits 0 | PASS | `RUN/logs/phase1.execution.json`: exit 0, 44.2248763 seconds; unchanged `script/run_phase1.py` executed through runpy with isolated settings. |
| Corruption entrypoint exits 0 | PASS | `RUN/logs/corruption.execution.json`: exit 0, 46.2752519 seconds; unchanged `script/run_corruption_flow.py`. |
| Importability with configured environment | PASS | Both entrypoints imported and completed with absolute PYTHONPATH pointing to src. |
| Raw snapshots and lineage | PASS | Both original raw JSON files contain 24 records; parsed DOI sets agree; hashes unchanged. |
| Required generated artifacts | PASS | Inventory in section 7: clean data, all three collections/manifests, 10-question test set, six quality/freshness reports, three metrics/answers pairs, log, two generated reports. |
| Three-state report table | PASS | All ten table rows checked against JSON; `RUN/data/reports/corruption_report.md`. |
| Three metrics files and sample counts | PASS | `RUN/data/results/{baseline,corrupted,repaired}_metrics.json`: 10 samples each; independently recalculated from answers. |
| Same questions in all states | PASS | All 10 answer records per state match test set on ID, type, question, ground truth and ground-truth IDs; test set also equals original. |
| Six corruption scenarios | PASS | Every log before/after value agrees with baseline/corrupted rows; deterministic rerun in memory matches persisted corruption. |
| Repair reconstructs baseline | PASS | Rebuilt twice from original raw at recorded run date; matches baseline exactly. Repaired retrieval/answers were repeated by corruption_flow. |
| Quality/freshness conclusions | PASS | GX executed: 7/7, 3/7, 7/7; freshness recomputed independently. Threshold checks confirm 25% passes and above 25% fails. |
| Cached model loads offline | PASS | Both runs loaded all-MiniLM-L6-v2 from the existing cache, no download; vectors indexed successfully. |
| Environment reproducibility | PASS on this machine; fresh installation NOT VERIFIED | System Python and exact versions in section 5; repository venv lacks dependencies. No package installation or clean-venv recreation authorized/performed. |
| Repository naming | FAIL | Current origin name/local folder `K4-L3B-Day10-KRAFTON-Data-Pipeline-Data-Observability` differs from required `K4-L3B-DAY10-TenNhom-DataPipelineDataObservability`. |
| No committed .env | PASS for local reachable history | `git ls-files` and `git log --all --format=%h -- .env` returned no .env entry. Remote/deleted history not verified. |
| Secret exposure check | PASS for bounded local scan | Common token/private-key patterns scanned in tracked files, 45 unique Git blobs across 3 commits and 36 existing JSON/Markdown/CSV artifacts/documents; no matches. No values printed. An additional scan of 39 new output/source text files after the fixes found no common token/private-key matches. Remote exposure and unknown formats not proven absent. |
| TEAM.md | NOT VERIFIED — waived by user | Explicit latest instruction: skip TEAM.md. File retained unchanged; no claim that the course requirement is satisfied. |
| Group/individual reports | FAIL / student action | Group and individual templates remain placeholders. Three named `<MSSV>_HoTen.md` reports are absent. |
| Each student has a main-branch commit / GitHub Insights | NOT VERIFIED | Local main has 3 commits by tainx287 and ngducmanh21; cannot establish contributions by all three students. No GitHub Insights inspection. |
| Live demo and understanding | NOT VERIFIED | The mock tool-agent now passes the offline tests; students must personally demonstrate and explain their work. |
| Honest generated results | PASS for this rerun | Both scripts created the isolated artifacts; numbers independently validated; no metrics/report hand editing. Independent authorship remains a student responsibility. |
| Each student's LMS submission and deadline | NOT VERIFIED | No LMS access/submission. README gives 2026-09-26 23:59:59 GMT+7; each student must submit personally. |

## 2. RUBRIC.md review

No score is assigned: the instructor decides scores. A passing pipeline does not establish every rubric requirement.

| Rubric item | Status | Evidence / gap |
| --- | --- | --- |
| 1. Structure and environment (10) | PASS execution; full reproducibility NOT VERIFIED | Modular src, pyproject.toml and requirements.txt present; imports work with PYTHONPATH. Existing venv is empty of required packages; no clean installation tested. |
| 2. Raw ingestion and lineage (15) | PASS offline requirement | Two preserved raw snapshots; 24 parsed records; DOI lineage check passes. No live API call needed or performed. |
| 3. Cleaning and modeling (15) | PASS tested snapshot | 24 unique IDs, no summary XML tags, correct date/age data, five embedding sections; CSV/JSON reproduced exactly. |
| 4. Embeddings and indexing (10) | PASS | Cached MiniLM loaded; SQLite evidence gives baseline 24, corrupted 20, repaired 24; manifests match row contents. |
| 5. Multi-provider QA agent (10) | PASS offline checks; remote integration NOT VERIFIED | Approved fixes make google an alias for Gemini and enable mock tool calls. Five provider routes pass; 13 agent cases pass with real LangChain tool execution over an in-memory index backed by the generated manifest. Remote clients were stubbed; no paid API was called. |
| 6. Baseline evaluation (10) | PASS | 10 questions, four types, actual Hit Rate and Token F1; baseline report matches JSON. |
| 7. GX 1.x and freshness (15) | PASS | Great Expectations 1.23.2 executed seven checks across four required types; strict age >180 and stale share >25% boundary verified. |
| 8. Corruption, repair, impact (15) | PASS mechanics; maximum-score impact claim not established | All six corruptions real; Hit Rate falls 1.0 to 0.8 then returns to 1.0. F1 falls only to 0.974074. This is a measured decline, not a broad performance collapse; analysis below explains why. |
| B1. Dashboard (+5) | NOT VERIFIED / no evidence found | No dashboard artifact identified. Not implemented as part of acceptance. |
| B2. Automatic self-healing (+5) | NOT VERIFIED for bonus | Script performs repair automatically in its comparison sequence, but does not implement a quality-triggered serving rollback/recovery controller. |
| B3. CI tests / >80% coverage (+5) | NOT VERIFIED / not demonstrated | In-memory acceptance checks are not a pytest CI suite and establish no coverage percentage. |

No hardcoded machine-specific paths were found in executable repository source during the scan. Runtime manifests/reports and acceptance execution logs contain resolved local paths by design. No old GX syntax crash, fabricated metric, or committed secret was found in the tested local evidence. TEAM.md deductions are not evaluated because the user waived that work; course rules still belong to the instructor.

### Defects fixed after explicit scope approval

Initial failures are preserved in `RUN/logs/acceptance.stdout.log`. The user explicitly approved editing the following two existing files.

| Existing file / function | Demonstrated defect | Change | Verification |
| --- | --- | --- | --- |
| `src/core/config.py`, `normalized_provider` | LLM_PROVIDER=google raised unsupported-provider RuntimeError | Normalize google to the existing gemini provider | google, gemini, openai and anthropic select the expected stubbed client; mock also succeeds. |
| `src/retrieval/llm.py`, `build_llm` and new private `_MockPaperChatModel` class | Tool-agent invocation with mock raised NotImplementedError | Mock binds only the two local paper tools, emits deterministic lookup/search calls, falls back from missing lookup to search, and extracts an answer from the first tool result. Unsupported structured judging retains the explicit heuristic fallback. | 10 benchmark questions answered correctly with recorded lookup calls; unquoted search, missing-lookup fallback and empty-index cases pass. All 30 saved judge verdicts are reproduced exactly. |

Post-fix evidence: `RUN/logs/acceptance_after_fix.stdout.log` and `acceptance_after_fix.execution.json`: exit **0**, **37.1679660 seconds**, all_checks_pass=true. All 40 artifact checks were repeated and passed. `git diff --check -- src/core/config.py src/retrieval/llm.py` passed; Git emitted only line-ending conversion notices.

The two full entrypoint runs preceded these fixes. After the fixes, the affected provider/agent/judge paths and artifact consistency checks were rerun in memory. No second set of pipeline outputs was generated, and no saved metrics or generated reports were rewritten. These targeted checks establish unchanged judge behavior for all existing evaluations; they do not claim paid-provider integration or another complete end-to-end run on the post-fix source.

## 3. Actual isolated rerun results

| Measure | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| Indexed records | 24 | 20 | 24 |
| Questions | 10 | 10 | 10 |
| Retrieval Hit Rate | 1.0 | 0.8 | 1.0 |
| Mean Token F1 | 1.0 | 0.9740740740740741 | 1.0 |
| Judge accuracy | 1.0 | 1.0 | 1.0 |
| Mean judge score | 5 | 4.8 | 5 |
| GX expectations passed | 7/7 | 3/7 | 7/7 |
| Quality gate | True | False | True |
| Stale papers (age >180) | 1/24 | 2/20 | 1/24 |
| Stale ratio | 4.1667% | 10% | 4.1667% |
| Freshness SLA | True | True | True |

Corrupted quality fails row count, DOI uniqueness, title length and summary length. Freshness still passes because 10% does not exceed 25%. Data was retained for evaluation despite quality failure.

All 40 artifact checks in `RUN/logs/acceptance.stdout.log` passed. The validation process itself exited 0 in 33.2172314 seconds; that exit code means the audit completed, not that the separately reported provider/agent probes passed.

### Causal interpretation and benchmark limits

- Dropping the five latest papers removes the ground-truth documents for q001 and q002; these two retrieval misses explain the fall from 10/10 to 8/10 hits.
- q002 still receives an answer matching the ground truth from another retrieved document. Only q001 lowers mean F1; a retrieval miss need not cause an answer mismatch.
- The other corruptions cause real data-quality violations but are not all measured by these ten questions. Noise added after a summary's first sentence may not affect the summary answer.
- Repair rebuilds the trusted raw content, restores both missing question documents, and returns Hit Rate and F1 to baseline.
- All ten questions quote a DOI. Exact DOI lookup is prioritized over vector-search ranking, limiting what Hit Rate proves about semantic retrieval.
- Answers are extracted from metadata. All 30 judge results use the fallback heuristic; 100% judge accuracy is not independent LLM judgment. Token F1 is based on sets of whitespace-separated tokens. Ragas is disabled.
- Neither corruption nor the test set was tuned to force a larger metric drop.

## 4. Comparison with preserved evidence

The original `data/` files and pre-Step-6 documents remain unchanged. Comparing every recorded hash identifies only the two explicitly approved source changes: src/core/config.py and src/retrieval/llm.py.

| Artifact class | Comparison |
| --- | --- |
| Clean CSV (all states) | Identical bytes |
| Clean JSON, shared test set, quality/freshness JSON, metrics, answers, corruption log | Identical JSON to prior run |
| Embedding manifests | Same model, collections and documents; only isolated persist_path differs |
| phase1_report.md | Only actual run timestamp differs |
| corruption_report.md | Only isolated test-set path differs |
| Chroma files | New SQLite/HNSW files with new UUID directories; collection names and counts agree. Binary equality is neither expected nor claimed. |

Thus there are **no numeric changes** from the previous run. Generated reports and metrics were not edited.

## 5. Reproduction environment and exact execution evidence

Use **`C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe`**, Python 3.11.9, 64-bit Windows. Do not use the repository's untracked `venv/Scripts/python.exe`: its package metadata check found every declared requirement missing. No packages were installed.

| Package | Installed version |
| --- | --- |
| chromadb | 1.5.9 |
| datasets | 5.0.1 |
| great-expectations | 1.23.2 |
| langchain | 1.4.2 |
| langchain-anthropic | 1.7.4 |
| langchain-google-genai | 4.4.0 |
| langchain-ollama | 1.1.0 |
| langchain-openai | 1.6.6 |
| pandas | 3.0.6 |
| python-dotenv | 1.2.3 |
| ragas | 0.4.3 (disabled) |
| requests | 2.34.2 |
| sentence-transformers | 6.1.0 |
| numpy | 2.4.6 |
| scipy | 1.17.1 |
| torch | 2.14.0 |
| transformers | 5.17.0 |
| huggingface-hub | 1.33.0 |

Model cache: `C:\Users\User\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2\snapshots\1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. No download was attempted.



The exact Python argv, full in-memory wrapper, working directory, environment overrides, start timestamp, duration and exit code are saved in:

- `RUN/logs/phase1.execution.json`
- `RUN/logs/corruption.execution.json`
- `RUN/logs/acceptance.execution.json`
- `RUN/logs/acceptance_after_fix.execution.json`

The actual command form for both entrypoints was:

```text
C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe -B -c <full wrapper in execution JSON> run_phase1.py
C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe -B -c <full wrapper in execution JSON> run_corruption_flow.py
```

Each command ran in the repository root in a separate child process. The parent captured stdout/stderr to exclusive-create log files and measured elapsed wall time with time.perf_counter.

| Entrypoint | Started UTC | Seconds | Exit |
| --- | --- | ---: | ---: |
| run_phase1.py | 2026-09-26T05:02:28.530035+00:00 | 44.2248763 | 0 |
| run_corruption_flow.py | 2026-09-26T05:03:29.053117+00:00 | 46.2752519 | 0 |

The environment overrides were:

```text
PYTHONPATH=<repository>/src
PYTHONDONTWRITEBYTECODE=1
LLM_PROVIDER=mock
RUN_RAGAS=0
REFRESH_SOURCE=0
REFRESH_TEST_SET=0
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
HF_DATASETS_OFFLINE=1
HF_HUB_DISABLE_TELEMETRY=1
OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
TOKENIZERS_PARALLELISM=false
GX_ANALYTICS_ENABLED=false
ANONYMIZED_TELEMETRY=false
TEMP=<RUN>/tmp
TMP=<RUN>/tmp
XDG_CACHE_HOME=<RUN>/cache
HF_HUB_CACHE=C:\Users\User\.cache\huggingface\hub
PYTHONIOENCODING=utf-8
```

The wrapper replaces core.config.load_settings in memory, using Paths under the isolated root and retaining the original raw input paths. It executes the unchanged scripts via runpy.run_path(..., run_name="__main__"). Python audit hooks reject writes outside the isolated root and socket connections. No config or pipeline file was edited to redirect outputs.

The output root was absent before the approved run. Neither entrypoint's existing-output guard was removed or bypassed. Do not rerun these exact commands into the now-populated isolated directory; a further clean output location requires approval.

No errors or warnings were found in the successful entrypoint stderr logs; they contain GX progress and model-loading progress. Earlier protected pre-approval import probes exited 1 because the audit guard blocked a Windows NUL-device open and then a temporary-file probe. Those probes created no files; normal imports passed once the approved temporary directory was available.

## 6. Changes made during Step 6

- **Pre-existing repository files modified:** `src/core/config.py` and `src/retrieval/llm.py`, for the demonstrated provider-alias and mock-tool defects detailed in section 2. Both fixes passed their affected checks.
- **Final report:** `docs/STEP_6_FINAL_ACCEPTANCE_SUMMARY.md` was created during the read-only-audit turn and updated after this approved rerun.
- **Generated artifacts:** only the approved isolated directory and its contents below.
- No original raw/clean/metrics/report/Chroma file was overwritten, moved or removed.
- Existing untracked venv and earlier summary files were preserved. No install, download, paid API call, commit, push or LMS submission occurred.

## 7. Every retained file and directory created in Step 6

### Final report

`docs/STEP_6_FINAL_ACCEPTANCE_SUMMARY.md` — acceptance audit, evidence and remaining work.

### Isolated generated files

All paths below are relative to `acceptance_runs/step6_20260926_01/`.

```text
data/chroma/chroma.sqlite3
data/chroma/40769bf0-7e0c-4eeb-a2be-ce0f1caed1f7/data_level0.bin
data/chroma/40769bf0-7e0c-4eeb-a2be-ce0f1caed1f7/header.bin
data/chroma/40769bf0-7e0c-4eeb-a2be-ce0f1caed1f7/length.bin
data/chroma/40769bf0-7e0c-4eeb-a2be-ce0f1caed1f7/link_lists.bin
data/chroma/comparison/chroma.sqlite3
data/chroma/comparison/3342edd8-0380-431c-b469-fbf8f6f795ef/data_level0.bin
data/chroma/comparison/3342edd8-0380-431c-b469-fbf8f6f795ef/header.bin
data/chroma/comparison/3342edd8-0380-431c-b469-fbf8f6f795ef/length.bin
data/chroma/comparison/3342edd8-0380-431c-b469-fbf8f6f795ef/link_lists.bin
data/chroma/comparison/813f34d5-f3fe-467e-a5e2-c8a0a4d37166/data_level0.bin
data/chroma/comparison/813f34d5-f3fe-467e-a5e2-c8a0a4d37166/header.bin
data/chroma/comparison/813f34d5-f3fe-467e-a5e2-c8a0a4d37166/length.bin
data/chroma/comparison/813f34d5-f3fe-467e-a5e2-c8a0a4d37166/link_lists.bin
data/clean/papers_clean.csv
data/clean/papers_clean.json
data/clean/papers_clean_corrupted.csv
data/clean/papers_clean_corrupted.json
data/clean/papers_clean_repaired.csv
data/clean/papers_clean_repaired.json
data/embeddings/papers_embeddings.json
data/embeddings/papers_embeddings_corrupted.json
data/embeddings/papers_embeddings_repaired.json
data/eval/test_set.json
data/quality/baseline_quality_report.json
data/quality/corrupted_freshness_report.json
data/quality/corrupted_quality_report.json
data/quality/freshness_report.json
data/quality/repaired_freshness_report.json
data/quality/repaired_quality_report.json
data/reports/corruption_report.md
data/reports/phase1_report.md
data/results/baseline_answers.json
data/results/baseline_metrics.json
data/results/corrupted_answers.json
data/results/corrupted_metrics.json
data/results/corruption_log.json
data/results/repaired_answers.json
data/results/repaired_metrics.json
logs/acceptance.execution.json
logs/acceptance.stderr.log
logs/acceptance.stdout.log
logs/acceptance_after_fix.execution.json
logs/acceptance_after_fix.stderr.log
logs/acceptance_after_fix.stdout.log
logs/corruption.execution.json
logs/corruption.stderr.log
logs/corruption.stdout.log
logs/phase1.execution.json
logs/phase1.stderr.log
logs/phase1.stdout.log
```

### Directories and temporary artifacts

```text
acceptance_runs/
acceptance_runs/step6_20260926_01/
acceptance_runs/step6_20260926_01/cache/
acceptance_runs/step6_20260926_01/data/
acceptance_runs/step6_20260926_01/logs/
acceptance_runs/step6_20260926_01/tmp/
acceptance_runs/step6_20260926_01/data/chroma/
acceptance_runs/step6_20260926_01/data/clean/
acceptance_runs/step6_20260926_01/data/embeddings/
acceptance_runs/step6_20260926_01/data/eval/
acceptance_runs/step6_20260926_01/data/quality/
acceptance_runs/step6_20260926_01/data/reports/
acceptance_runs/step6_20260926_01/data/results/
acceptance_runs/step6_20260926_01/data/chroma/40769bf0-7e0c-4eeb-a2be-ce0f1caed1f7/
acceptance_runs/step6_20260926_01/data/chroma/comparison/
acceptance_runs/step6_20260926_01/data/chroma/comparison/3342edd8-0380-431c-b469-fbf8f6f795ef/
acceptance_runs/step6_20260926_01/data/chroma/comparison/813f34d5-f3fe-467e-a5e2-c8a0a4d37166/
acceptance_runs/step6_20260926_01/tmp/torchinductor_User/
```

The libraries also create and clean up randomized temporary probe/work files under the approved tmp directory. No such files remain. Their transient basenames were not retained by the initial execution logger; the inventory above is complete for retained outputs, not an exact historical list of deleted temporary basenames. tmp/torchinductor_User is an empty runtime directory; cache/ is empty. SQLite journals, if transiently created by Chroma, are managed by the library; no WAL/SHM/journal files remain in the final inventory.

## 8. Remaining actions

1. The approved technical fixes are complete and verified. Retain the initial failed-check logs and the post-fix passing logs as evidence.
2. The three students must write accurate group/individual reports, explain the work in the live demo, ensure each has a relevant personal commit, and each submit on LMS.
3. Resolve the repository naming mismatch; a name matching the documented pattern is `K4-L3B-DAY10-KRAFTON-DataPipelineDataObservability`. TEAM.md is skipped at the user's direction; the instructor's requirement has not been changed.
4. Fresh virtual-environment installation, paid-provider integration, GitHub contributor verification, remote/deleted-history secret review and LMS evidence remain unverified.
5. Bonus dashboard, quality-triggered self-healing and CI coverage >80% are not established. No full-score or bonus claim is made.

## 9. Git status before Step 6 writes

Branch: main. Command: git status --short.

```text
 M src/evaluation/testset.py
 M src/ingestion/cleaning.py
 M src/ingestion/corruption.py
 M src/ingestion/crossref.py
 M src/observability/quality.py
 M src/observability/reporting.py
 M src/pipelines/corruption_flow.py
 M src/pipelines/phase1.py
?? data/chroma/43d00513-4f2c-4550-9801-13f135d7068d/
?? data/chroma/chroma.sqlite3
?? data/chroma/comparison/
?? data/clean/papers_clean.csv
?? data/clean/papers_clean.json
?? data/clean/papers_clean_corrupted.csv
?? data/clean/papers_clean_corrupted.json
?? data/clean/papers_clean_repaired.csv
?? data/clean/papers_clean_repaired.json
?? data/embeddings/papers_embeddings.json
?? data/embeddings/papers_embeddings_corrupted.json
?? data/embeddings/papers_embeddings_repaired.json
?? data/eval/test_set.json
?? data/quality/baseline_quality_report.json
?? data/quality/corrupted_freshness_report.json
?? data/quality/corrupted_quality_report.json
?? data/quality/freshness_report.json
?? data/quality/repaired_freshness_report.json
?? data/quality/repaired_quality_report.json
?? data/reports/corruption_report.md
?? data/reports/phase1_report.md
?? data/results/baseline_answers.json
?? data/results/baseline_metrics.json
?? data/results/corrupted_answers.json
?? data/results/corrupted_metrics.json
?? data/results/corruption_log.json
?? data/results/repaired_answers.json
?? data/results/repaired_metrics.json
?? docs/STEP_0_1_2_SUMMARY.md
?? docs/STEP_3_4_5_SUMMARY.md
?? venv/
```

## Existing artifact inventory and SHA-256 baseline

The following was recorded read-only before creating this report. These hashes allow preservation checks after the approved run.

| Existing path | SHA-256 |
| --- | --- |
| `data/chroma/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/chroma/chroma.sqlite3` | `0b642e076006961ca1aa5d1170b222fcbadef33e0e2331873ead42fc12e31ccb` |
| `data/chroma/43d00513-4f2c-4550-9801-13f135d7068d/data_level0.bin` | `683a8fc1b66838049fe5a881a769bf75a8b14a466a8d09fc233546275c8ba149` |
| `data/chroma/43d00513-4f2c-4550-9801-13f135d7068d/header.bin` | `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` |
| `data/chroma/43d00513-4f2c-4550-9801-13f135d7068d/length.bin` | `7a12e561363385e9dfeeab326368731c030ed4b374e7f5897ac819159d2884c5` |
| `data/chroma/43d00513-4f2c-4550-9801-13f135d7068d/link_lists.bin` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/chroma/comparison/chroma.sqlite3` | `566e163d078d122c27c6aac215131938c3b7876036196323729aba63eadf1f9c` |
| `data/chroma/comparison/8faef1cc-0bcb-4e8a-b600-d63fe0c33bb8/data_level0.bin` | `5cfc8b049f59497ffc26c27daaf6228425b7b891f9fd9f265e47c30b7101f1bf` |
| `data/chroma/comparison/8faef1cc-0bcb-4e8a-b600-d63fe0c33bb8/header.bin` | `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` |
| `data/chroma/comparison/8faef1cc-0bcb-4e8a-b600-d63fe0c33bb8/length.bin` | `e07ee3b05cea476fd3dd7f38a6c062fae368130259d2aee2cc4c6d4129e46daa` |
| `data/chroma/comparison/8faef1cc-0bcb-4e8a-b600-d63fe0c33bb8/link_lists.bin` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/chroma/comparison/b4cf75b9-719f-45fa-ab77-6a62cefe48b0/data_level0.bin` | `a36010cc27e59fe6da1f38de3b93a3ab56ba8de24a3352555da16852ba1d88e1` |
| `data/chroma/comparison/b4cf75b9-719f-45fa-ab77-6a62cefe48b0/header.bin` | `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` |
| `data/chroma/comparison/b4cf75b9-719f-45fa-ab77-6a62cefe48b0/length.bin` | `fb9f96d6dbb366921d259f9fb4fbb7e955735768bee09669e8d88a8ee16c7bfc` |
| `data/chroma/comparison/b4cf75b9-719f-45fa-ab77-6a62cefe48b0/link_lists.bin` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/clean/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/clean/papers_clean.csv` | `b673791589bd4ac480bcf1d9ab04b2869e56a23723cb4213d33f992f65a087c1` |
| `data/clean/papers_clean.json` | `9932a936a3459786f1776358674124991d4303bf938eda54260928575550ea7f` |
| `data/clean/papers_clean_corrupted.csv` | `a490dbdcb667d4a6e2790b59c3e4a87a068e46d0eaec1a9734937c8a3c846af8` |
| `data/clean/papers_clean_corrupted.json` | `f1209faf33411c3a3855cf6c08355f6b766fbeb0e4d85e097c050098ea23fb5f` |
| `data/clean/papers_clean_repaired.csv` | `b673791589bd4ac480bcf1d9ab04b2869e56a23723cb4213d33f992f65a087c1` |
| `data/clean/papers_clean_repaired.json` | `9932a936a3459786f1776358674124991d4303bf938eda54260928575550ea7f` |
| `data/embeddings/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/embeddings/papers_embeddings.json` | `b12f322fde692d7f20e2719dbcdc9d4318ca5d6a958f0c8f8ede848f085f2e5c` |
| `data/embeddings/papers_embeddings_corrupted.json` | `515648f26b35f3ff28467e9aedfed4d149450fec7b65396e3d1f81e57a1b4984` |
| `data/embeddings/papers_embeddings_repaired.json` | `103a40537761786309a823d29eb99b8b2e709569a3ee8448dbffa277cbc2e1df` |
| `data/eval/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/eval/test_set.json` | `8a9cb84cbe1f01c415e27493622d3430afc745c927b7922429a3f333e05e588e` |
| `data/quality/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/quality/baseline_quality_report.json` | `c69b6d73454bd9c83866d63f1104971f42d721fa7f8706e3fb0687caf71690df` |
| `data/quality/corrupted_freshness_report.json` | `db2ac5159f8c320acd699ed6a48d59527cfcd359ff0e59b08a1c4f6b18b44a45` |
| `data/quality/corrupted_quality_report.json` | `34d4b399d167207c67695ade57f6d5dc42afa8d671c923fefe512e11318ff5cb` |
| `data/quality/freshness_report.json` | `0825c74f5a77ff591dd52fd9d3e7faf33b33214755e3acf8a6f67dad8e169676` |
| `data/quality/repaired_freshness_report.json` | `0825c74f5a77ff591dd52fd9d3e7faf33b33214755e3acf8a6f67dad8e169676` |
| `data/quality/repaired_quality_report.json` | `c69b6d73454bd9c83866d63f1104971f42d721fa7f8706e3fb0687caf71690df` |
| `data/quality/gx/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/raw/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/raw/crossref_records.json` | `87b6413046082aa85518ebd6142aa5fccc88926dcbb65c83de60e9302e62446e` |
| `data/raw/crossref_response.json` | `d968be684bff7d7fc8245194e46544a3a3f477418437cce993bc17d4ecab5cc0` |
| `data/reports/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/reports/corruption_report.md` | `5db332f8edddfb9f77b4497fcf18ce650d4514d1d01e7b53265a34802031d2cb` |
| `data/reports/phase1_report.md` | `350ceb16b28ee22ff674794ecf04f1747fdaee3fb509c22196d069e4ee5a0a34` |
| `data/results/.gitkeep` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `data/results/baseline_answers.json` | `fd2ba7bc420a166fc943b454208b9d918516ad3f12abfa1b6e17e1de56b2509c` |
| `data/results/baseline_metrics.json` | `8ac7ecadfdb59192c91667ff7b773571087c6134b8eb5dd87af08f1199a834e5` |
| `data/results/corrupted_answers.json` | `a4a82375703c413fffe8b8565086386a87b2d930b86c1a6b594a40576d7e498f` |
| `data/results/corrupted_metrics.json` | `57a6378a1fed3ebdbfdca7145cf85f586018b72ac5cf27164e80fbd23f6aa87c` |
| `data/results/corruption_log.json` | `57b9908180b9e5444977339545073cc2a64068f6a301959944161d64f85f76ec` |
| `data/results/repaired_answers.json` | `fd2ba7bc420a166fc943b454208b9d918516ad3f12abfa1b6e17e1de56b2509c` |
| `data/results/repaired_metrics.json` | `8ac7ecadfdb59192c91667ff7b773571087c6134b8eb5dd87af08f1199a834e5` |
