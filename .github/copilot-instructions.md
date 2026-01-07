# GitHub Copilot instructions — PySH1995 🚀

Purpose: short, actionable guidance to help an AI coding agent be productive in this repository.

## Quick summary (big picture)
- This repo parses the original SH1995 ASCII gzipped files (from the `VI_64` data release), converts them into Pandas DataFrames and writes them into a SQLite database in `databases/`.
- Data flow: `scripts/download_data.py` → extract into `VI_64/` → `scripts/mk_db.py` / `scripts/init_db.py` parse files → `src/utils/parsing/*` produce `DataBlock`/`PhysicalState` → `src/utils/writing.py` creates DB and writes tables (`emi`, `rec`, `opa`, `dep`).

---

## Key files & their intent 🔧
- `scripts/download_data.py` — download and extract the remote tarball into `VI_64/` (uses `requests`, `tqdm`).
- `scripts/mk_db.py` — create an empty sqlite DB: calls `src.utils.writing.initialise_db` to create standard tables.
- `scripts/init_db.py` — main pipeline: reads `VI_64/`, builds DataFrames (`create_dataframes`) and writes them into `databases/<name>.db`.
- `scripts/rm_dbs.py` — helper to remove generated DB files (skips `databases/notes`).
- `src/utils/parsing/data_block.py` — core fixed-width parser. Important behaviors:
  - Values are parsed from fixed-width 13-character blocks.
  - `parse_float` expects mantissa + `E` + 3-digit exponent format (mantissa = all but last 4 chars, exponent = last 3 digits after an `E`).
- `src/utils/parsing/physical_state.py` — groups `DataBlock`s by physical state and selects blocks by data type (map: `E`→`emi`, `R`→`rec`, `A`→`opa`, `B`→`dep`).
- `src/utils/writing.py` — DB location (`db_dir` = `databases/`) and helpers: `connect_to_db`, `initialise_db`, `create_dataframes`, `write_dfs_to_db`.
- `src/utils/reading.py` — lightweight SQL `Query` builder for easy access to DB results. Returns a dict of column→list.

---

## Commands / developer workflow (exact examples) ⚙️
1. Install deps (recommended Python 3.12):
   - `pip install -r requirements.txt`
2. Download raw data into `VI_64/`:
   - `python scripts/download_data.py`
3. Create DB skeleton (if needed):
   - `python scripts/mk_db.py --name db`
4. Parse and populate DB:
   - `python scripts/init_db.py --name db`
5. Quick query example in Python REPL:

```python
from src.utils.reading import Query
with Query.START('db') as q:
    data = (q.FROM('emi')
             .SELECT('wave','val')
             .WHERE('z', 'z == 1')
             .ORDER_BY('wave')
             .LIMIT(10)
             .STOP())
print(data)
```

Note: run scripts from repository root so the `scripts/` sys.path hack works (scripts append the repository parent to `sys.path`).

---

## Project-specific conventions & gotchas ⚠️
- Filename pattern required for data files: must end with `.d.gz` and follow the `r{z}{case}{tttt}.d.gz` convention (code expects `fname[1]` numeric, `fname[2]` alphabetic, `fname[3:7]` numeric). Typical Z values are 1–8 for SH1995.
- Parser is brittle by design and tuned to the legacy SH1995 formatting: fixed-width blocks of 13 characters and a specific `E`-format float. When modifying parsing, add unit tests that include real example lines from `VI_64/`.
- Database schema is fixed by `initialise_db()` — tables are `emi`, `rec`, `opa`, `dep` with columns `(wave, rec_case, z, n_u, n_l, temp, dens, val)`.
- `create_dataframes()` accepts `rec_case`, `data_types` and `z_bounds` — use these to limit runs for quick debugging.

---

## Suggested places to add tests / instrumentation 🧪
- Unit tests for `DataBlock.parse_float` / `DataBlock.processRawData` using extracted lines from `VI_64/`.
- Tests for `PhysicalState.from_lines` and `create_dataframes()` (small `z_bounds` and a single `data_type`).
- Tests for `Query` building and `.STOP()` result format.

---

## When changing behavior (checklist) ✅
- If you change how data types are detected, update both `PhysicalState.from_lines` and `DataBlock.from_lines` mappings.
- If you change table shape, update `initialise_db()` and any consumers (the `Query` class and docstrings).
- Keep sample/real `VI_64/` lines for regression tests when updating parsing.

---

If anything above is unclear or you'd like more detailed examples (e.g., unit-test snippets or a suggested small CI job to validate parsing), say which section to expand and I will iterate. 👍
