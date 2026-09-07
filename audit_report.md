# PitchGen Codebase Audit Report

**Date:** 2026-09-07  
**Auditor:** researcher agent  
**Goal ID:** 01M1X4D6M4HJA3JX8ME2N432A2  
**Task:** Audit existing pitchgen codebase, identify issues, and recommend CLI refactoring

---

## 1. Codebase Inventory

### 1.1 Top-level Python service files (root /root/automaton/)

| File | Framework | Lines | CLI Support | Purpose |
|------|-----------|-------|-------------|---------|
| `pitchgen_service.py` | Flask | ~100 | None | Single-file Flask with rate limiting |
| `pitchgen_app.py` | FastAPI | ~120 | None | Single-file FastAPI with Pydantic |
| `pitchgen_microservice.py` | Flask | ~50 | None | Minimal stub, returns template pitch |
| `pitchgen_demo.py` | FastAPI | ~60 | None | Demo FastAPI, template-based pitch |
| `pitchgen_server.py` | FastAPI | ~140 | None | Multi-section pitch (deck, landing, pricing) |
| `pitchgen_test.sh` | Bash | ~30 | N/A | Integration test script |
| `pitchgen_demo_test.sh` | Bash | ~20 | N/A | Smoke test script |

### 1.2 Structured project directories

| Directory | Framework | CLI Files | HTTP Files | Notes |
|-----------|-----------|-----------|------------|-------|
| `/root/automaton/pitchgen/` | FastAPI + Node.js | None | `main.py`, `pitchgen_server.py`, `server.js` | Has `requirements.txt` (empty), tests dir, static, docs |
| `/root/automaton/pitchgen-demo/` | Python stdlib + HTTP | **`cli.py`** | `server.py`, `app.py` | **Only codebase with working argparse CLI** |
| `/root/automaton/pitchgen-service/` | Python FastAPI | None | `main.py`, `tests.py` | Service-oriented, ARCHITECTURE.md present |
| `/root/automaton/pitchgen_service/` | Python FastAPI | None | `main.py` | Similar to above, slightly different structure |
| `/root/automaton/pitchgen-service/` (Node.js) | Node.js Express | None | `index.js` | Express server, template-based, `package.json` present |

### 1.3 Specification and documentation

| File | Content |
|------|---------|
| `pitchgen_spec.md` | Specifies stdlib-only CLI + HTTP mode, input schema (product_name, target_audience, key_features, value_proposition) |
| `pitchgen_service/ARCHITECTURE.md` | Documents FastAPI service architecture |
| `pitchgen_demo/README.md` | None |
| `pitchgen-demo/pitchgen_demo.py` | Contains docstring referencing Flask template engine |

### 1.4 Existing CLI in pitchgen-demo/cli.py

```python
# Reads JSON from file or stdin
# Outputs JSON result + markdown preview
# Uses argparse with single positional arg for input_file
```

This is the **only CLI implementation** found. It has issues:
- Reads from file/stdin only, no command-line flags for individual fields
- Depends on `app.py` (not in same import path — uses relative `from app`)
- No `--help` for individual pitch parameters
- No output format options (JSON only, markdown optional hardcoded)

---

## 2. Identified Issues

### Issue 1: Severe Code Duplication
**Severity: High**

At least 6+ top-level Python files implement the same pitch generation concept with different frameworks, schemas, and output formats. No canonical implementation exists.

**Affected files:**
- `pitchgen_service.py` (Flask)
- `pitchgen_app.py` (FastAPI)
- `pitchgen_microservice.py` (Flask)
- `pitchgen_demo.py` (FastAPI)
- `pitchgen_server.py` (FastAPI)
- `pitchgen/pitchgen_server.py` (FastAPI)
- `pitchgen-demo/pitchgen_demo.py` (stdlib)
- `pitchgen_service/main.py` (FastAPI)
- `pitchgen_service/pitchgen_service.py` (FastAPI)
- `pitchgen_demo/main.py` (FastAPI)

**Recommendation:** Consolidate into one canonical service + one CLI wrapper.

### Issue 2: No Unified CLI
**Severity: High**

Only `pitchgen-demo/cli.py` has any CLI. The spec (`pitchgen_spec.md`) describes a CLI mode but it is not implemented in the canonical service. All other codebases are HTTP-only.

**What the CLI should support (per spec):**
- Read JSON input from file or stdin
- Accept individual fields as flags
- Output JSON result + markdown preview
- No external dependencies (Python stdlib only)

**What's missing:**
- No argparse-based unified entry point
- No click or typer (even though other pitchgen projects use these patterns)
- No unified `--help`, `--version`, `--output` flags
- No integration between CLI mode and HTTP mode

**Recommendation:** Build a unified CLI using `argparse` (stdlib) that can:
1. Accept JSON input from file or stdin
2. Accept individual fields as flags
3. Output JSON or markdown
4. Optionally call HTTP endpoint (with `--remote` flag)

### Issue 3: Inconsistent Input Schemas
**Severity: Medium**

Each implementation uses a different input schema:

| Implementation | Fields |
|---------------|--------|
| `pitchgen_spec.md` | product_name, target_audience, key_features[], value_proposition |
| `pitchgen_service.py` (Flask) | topic |
| `pitchgen_app.py` | product_name, one_liner, target_audience, primary_value, tone, length |
| `pitchgen_demo.py` | product_name, one_liner, target_audience, primary_value, tone, length |
| `pitchgen_server.py` | product_name, one_liner, target_audience, primary_value, tone, length |
| `pitchgen-demo/app.py` | name, idea |
| `pitchgen-service/index.js` | productName, tagline, companyName, feature, benefit |

**Recommendation:** Standardize on one schema. The FastAPI `Pydantic` models in `pitchgen_app.py` / `pitchgen_server.py` are the most complete.

### Issue 4: No LLM Integration
**Severity: Info**

All current implementations use deterministic template-based pitch generation. The spec mentions "generates marketing pitch content" but no implementation uses any inference model. This is acceptable for demo/template mode but should be noted.

**Recommendation:** For CLI v1, keep template mode. Plan LLM integration as v2 with model selection flag.

### Issue 5: Fragmented Test Coverage
**Severity: Medium**

- `/root/automaton/pitchgen/tests/test_pitchgen_endpoints.py` imports `from src.main import app` (non-existent module path)
- `/root/automaton/pitchgen-demo/` has `smoke_test.sh` (bash script, functional)
- `/root/automaton/pitchgen_service/tests.py` exists separately
- No pytest configuration or CI

**Recommendation:** Consolidate tests, fix import paths, add `pytest.ini`.

### Issue 6: Empty requirements.txt
**Severity: Low**

`/root/automaton/pitchgen/requirements.txt` exists but is empty. The service requires `fastapi`, `uvicorn`, `pydantic` but these aren't documented as installable dependencies.

**Recommendation:** Populate `requirements.txt` with actual dependencies.

### Issue 7: Duplicate Documentation
**Severity: Low**

- `/root/automaton/pitchgen_spec.md` describes stdlib-only tool
- `/root/automaton/pitchgen_service/README.md` describes FastAPI service
- `/root/automaton/pitchgen-service/README.md` describes Node.js service
- `/root/automaton/pitchgen/README.md` describes FastAPI service

These are for different implementations and cause confusion.

**Recommendation:** One README per consolidated project.

---

## 3. Refactor Recommendations for CLI Implementation

### 3.1 Recommended Architecture

```
pitchgen/
├── cli.py              # argparse CLI entry point (NEW)
├── service.py          # FastAPI HTTP service
├── generator.py        # Core pitch generation logic
├── models.py           # Pydantic input/output schemas
├── templates.py        # Pitch templates
├── requirements.txt    # Dependencies
├── README.md
└── tests/
    ├── test_generator.py
    └── test_cli.py
```

### 3.2 CLI Interface (Recommended)

```bash
# Option 1: JSON file input
pitchgen generate input.json --format markdown --output pitch.md

# Option 2: Individual fields
pitchgen generate \
  --product-name "SuperWidget" \
  --one-liner "The best solution" \
  --target-audience "developers" \
  --primary-value "simplify development" \
  --tone "professional" \
  --length 100

# Option 3: Via HTTP service
pitchgen generate --remote --url http://localhost:8000 input.json

# Help
pitchgen --help
pitchgen generate --help
```

### 3.3 Input Schema (Recommended Standard)

```python
class PitchRequest:
    product_name: str       # required
    one_liner: str          # required  
    target_audience: str    # required
    primary_value: str      # required
    tone: str               # required (professional/casual/technical)
    length: int             # optional, default=100, max=500
```

### 3.4 Key Refactoring Tasks

| Priority | Task | Rationale |
|----------|------|-----------|
| P0 | Create unified `cli.py` with argparse | Core deliverable |
| P0 | Extract `generator.py` (core logic) | Shareable between CLI and HTTP |
| P0 | Define `models.py` with canonical Pydantic schema | Single source of truth |
| P1 | Populate `requirements.txt` | Installability |
| P1 | Fix test import paths | Test reliability |
| P2 | Consolidate README | Single documentation |
| P2 | Add `--remote` flag to CLI | HTTP integration |
| P3 | Add LLM integration (v2) | Production use |

---

## 4. Summary

The pitchgen codebase has significant fragmentation with 6+ overlapping Python implementations and 1 Node.js implementation. Only one minimal CLI exists (`pitchgen-demo/cli.py`) and it doesn't follow the spec fully. The recommended path forward is:

1. **Consolidate** around the FastAPI service (`pitchgen_app.py` / `pitchgen_server.py` — merge these)
2. **Extract** core generation logic to a shared module
3. **Build** a new argparse-based CLI that reads JSON from file/stdin or accepts individual flags
4. **Standardize** input/output schemas with Pydantic
5. **Test** the CLI end-to-end with the smoke test pattern from `smoke_test.sh`
