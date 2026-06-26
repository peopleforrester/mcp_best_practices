# Remediation Progress

- [x] Phase 1 (H3): redaction covers sk-proj/sk-svcacct/sk-admin + bounded email host
- [x] Phase 2 (H1): rate-limit identity from X-Forwarded-For
- [x] Phase 3 (H2): streaming body cap + answer key/value length bounds
- [x] Phase 4 (H4): LICENSE (Apache-2.0) + CHANGELOG
- [x] Phase 5 (M5): capstone recursive redaction/scan
- [x] Phase 6 (M6): honest pagination naming (offset)
- [x] Phase 7 (M8): k8s find_pods error contract
- [x] Phase 8 (M10): type enforcement (mypy/tsc/tsconfig)
  - surfaced: Taskfile `ts:test` uses `pnpm -r` which fails at repo root (no workspace);
    CI loops per-package instead. New finding, deferred (pre-existing, out of M10 scope).
- [x] Phase 9 (M11): incremental report_progress
- [ ] Phase 10 (M7 + low): fingerprint docstring + server.json $schema
- [ ] Phase 11 (low): lock contracts (OpenAPI hide, detector bypass, hits eviction)

## Deferred
- M9 eval namespacing metric (only applied where correct)
- A2A async seam (labeled demo)
- pagination DRY (cross-package independence is intentional)
