# Reentry Decision

Date: 2026-04-10

Decision: controlled reentry is intentionally out of scope for the Phase 2 governance minimum closure sprint.

Reason: this sprint is limited to making the existing proposal -> decision -> approve/reject -> event -> object_version flow coherent and observable. Reentry needs the materialization/edit loop to be defined more completely, so introducing it here would widen scope beyond the sprint boundary.

Operational effect:
- no `/proposals/reentry` flow is introduced in this sprint;
- no `/reentry/*` surface is introduced in this sprint;
- the existing `reentry_jobs` table remains structural only;
- future reentry work must be proposed explicitly as a later slice.
