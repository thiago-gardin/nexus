# Start Here

`tree/` is the remote-readable publication surface for Nexus.

## How to navigate

- Start with `INDEX.md` for the current domain list and primary links.
- Use `SYSTEM_STATUS.yaml` to confirm freshness and publication scope.
- Follow each domain's `INDEX.md` to reach the published contract, object views, projections, and governance trace.
- Use the governance trace to follow proposal -> decision -> history/version trail -> publication.
- Use `tree/inbox/proposals/` only for structured proposals.

## Executable truth vs publishable truth

- Executable truth lives in the SQLite-backed runtime.
- Publishable truth is a derived treefolder snapshot generated from that runtime.
- Treefolder artifacts are publication outputs, not the source of identity or mutation authority.

## Remote write restrictions

- Remote agents may read published artifacts.
- Remote agents may write only structured proposals in `tree/inbox/proposals/`.
- Canonical artifacts and domain publications are regenerated from the executable core, not edited as sovereign truth.

## ID and status conventions

- Stable IDs come from the executable core.
- `tree/SYSTEM_STATUS.yaml` carries freshness and publication metadata.
- Domain folders are partitioned by `domain_id` and are navigation surfaces, not alternate truth sources.
