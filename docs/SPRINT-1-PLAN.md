# Sprint 1 — Records Core (CLS / MTD / CAP / VER)

## Implemented in this import (domain starter)
- Approved class gate, maker-checker helper, dynamic mandatory metadata validator,
  record status content lock and stored-version prerequisite for declare.
- Pure unit tests with fictitious data; NO database/API integration yet.

## Remaining work and Definition of Done
1. Maker/checker classification version persistence with effective dates; negative tests.
2. Dynamic metadata/picklist definitions owned by Bank, inheritance, secure validation.
3. Capture from upload/scanner/email/API, AV scan, SHA-256, S3 object store;
   failed ingest never creates a valid declared record.
4. Unique Bank numbering format from TBD-BANK:RECORD_NUMBER_FORMAT; concurrency test.
5. Transactional versions, check-in/out, immutable declaration and change rationale;
   all state changes audited with rejection evidence.
6. RBAC gate for endpoints before Sprint 2 ABAC build; isolate PoC data.
7. Integration tests using real database, storage, and Keycloak; traceability rows
   and OpenAPI updated; UAT-CAP-01, UAT-VER-01 explicitly verified.
8. Obtain Bank decisions before 'Build' or claim any Must FR complete.

## Control mapping
- FR-CLS-01 -> PED-3 (provisional), maker/checker; test_records_domain
- FR-MTD-01 -> SOP-D metadata (provisional), dynamic required metadata
- FR-VER-02 -> SOP-D declare (provisional), immutable content policy
- FR-CAP-01/02/04, FR-VER-01: planned, no implementation claim
