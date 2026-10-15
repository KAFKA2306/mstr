# Bitcoin Treasury Evidence Agent Contract

`AGENTS.md` is the repository-wide agent instruction source.

This repository owns issuer evidence for corporate Bitcoin holdings, financing, dilution, and related treasury disclosures. Do not duplicate modeling owned by other repositories.

## Data contract

- Prefer SEC/issuer IR and other official corporate disclosures.
- Preserve issuer identity, source URL, filing/publication date, effective period, units/currency, and source hash when the current dataset requires them.
- Keep issuer observations separate from derived treasury metrics and investment interpretation.
- Never infer purchases, sales, conversions, dilution, debt exercise, financing, or treasury actions that an issuer has not disclosed.
- Bitcoin price movement is not a corporate treasury transaction.
- Materialize primary evidence before downstream calculations.

## Release boundary

Repository checks prove only the exact evidence/revision they execute. Data/product release requires direct verification of the merged evidence, artifact, API/UI, or fresh filing acquisition that owns the claim.

Do not execute trades, financing, wallet transfers, or account actions.

## Outcome-first task interpretation (Altitude / Depth / Range / Speed)

- **Altitude:** Interpret a task as a verifiable user outcome, not only the named intermediate step. Infer the smallest justified acceptance criteria from the request and current repository state; do not silently expand scope or override explicit instructions.
- **Depth:** Use primary/current evidence and real domain tools and methods. Verify the actual postcondition independently of agent self-report, preferably on the exact changed revision or target runtime.
- **Range:** Combine code, data, tests, runtime/UI, and domain expertise when that materially improves the outcome, while respecting canonical owners and avoiding duplicate systems.
- **Speed:** Complete authorized read-only and reversible work through implementation, focused checks, and read-back without unnecessary approval loops. Bound retries and stop at the proven outcome.
- These principles never bypass repository-specific security, privacy, permission, publication, spending, destructive-action, or release boundaries. State verified results and any remaining `UNVERIFIED` layers.
