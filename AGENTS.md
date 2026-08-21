# Repository Agent Contract

## Mission

Own Bitcoin-treasury company evidence for this repository: corporate Bitcoin holdings, capital raises, dilution/funding structure and directly related issuer disclosures. Preserve filing-backed facts separately from derived treasury metrics or investment interpretation.

## Canonical authority

- Prefer SEC/issuer IR and other official corporate disclosures for holdings, financing and share/convertible terms.
- Preserve issuer identity, filing/source URL, publication/filing date, effective/as-of period, units/currency and source hash where the current dataset supports them.
- Do not duplicate convertible-bond benchmark modeling owned by `BMAX`, Bitcoin network evidence owned by `btc_dashboard`, or derivatives evidence owned by `option`; reference their versioned artifacts when required.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, canonical treasury records, workflows/tests and any public view.
2. Resume one canonical existing workline before creating another collector, ledger, branch or Issue.
3. Prefer new verified issuer records, correction of identity/period/dilution semantics, reproducible treasury metrics, user-visible evidence, then simplification.
4. Materialize primary evidence before downstream calculations; keep observations and derived metrics distinct.
5. Run focused deterministic checks and verify the exact reviewed revision before merge.
6. Stop at the fixed point; do not create speculative valuation or financing scenarios merely because new filings exist.

## Branch lifecycle

- Aside from the default branch and unavoidable platform-managed/protected branches, a persistent branch is permitted only while it is the head branch of a currently open PR.
- Creating a work branch creates an obligation to open or reuse its canonical PR immediately; do not use branches as backlog, continuation state, backup, archive, or evidence storage.
- After a PR is merged or closed, delete its head branch after verifying PR/main state. A branch with no open PR is an orphan and must be deleted.
- Before and after work, compare repository branches with open PR heads. Do not report cleanup/fixed point while an orphan task branch remains.
- If the available tool cannot delete a branch, record that as a tooling blocker and do not claim cleanup complete. Never create another orphan branch as a workaround.

## Merge and release are separate

### PR merge conditions

A PR may merge when the repository-local issuer/treasury contract is correct on the exact head revision: filing provenance and period/unit semantics are preserved, focused deterministic tests pass, generated artifacts are reproducible where affected, and no unresolved review or correctness blocker remains.

A future issuer filing, live SEC/IR fetch after merge, public deployment, or observed corporate outcome is **not** a merge condition unless the PR specifically changes the release/live-acquisition mechanism and that mechanism must be validated before merge.

### Product/data release conditions

Release is a separate post-merge decision. Treat treasury evidence/views as released only after the merged `main` revision is read back and the release surfaces in scope are actually verified, including fresh primary-source acquisition when required, published artifacts/API/UI, deployment identity, and rollback/rebuild path where applicable.

A merged PR does not prove a new filing was acquired or a product was released. A live-source/deployment blocker may block release without invalidating a correctly merged repository change. Report merge and release independently.

## Boundaries

- Never infer purchases, sales, conversions, dilution, debt exercise or treasury actions that an issuer has not disclosed.
- Do not treat Bitcoin price movement as a corporate treasury transaction.
- Do not execute trades, financing, wallet transfers or account actions.
- Unobserved filing fetches, CI, market data, deployment or corporate outcomes remain unverified.

## Completion report

Report verified issuer/treasury evidence Before -> After, canonical artifact/source, Issue/PR/commit/check evidence, then report `merged` and `released` separately with direct evidence for each. Include branch cleanup state, duplication/manual work removed and remaining blocker.