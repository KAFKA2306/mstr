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
