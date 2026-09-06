# Bitcoin Treasury Evidence Agent Contract

`AGENTS.md` is the only repository-wide agent instruction source.

This repository owns issuer evidence for corporate Bitcoin holdings, financing, dilution, and related treasury disclosures. Do not duplicate modeling owned by other repositories.

## Data rules

- Prefer SEC/issuer IR and other official corporate disclosures.
- Preserve issuer identity, source URL, filing/publication date, effective period, units/currency, and source hash when the current dataset requires them.
- Keep issuer observations separate from derived treasury metrics and investment interpretation.
- Never infer purchases, sales, conversions, dilution, debt exercise, financing, or treasury actions that an issuer has not disclosed.
- Bitcoin price movement is not a corporate treasury transaction.

## Execution and verification

Proceed with read-only and reversible work without unnecessary confirmation. Reuse one canonical workline and one evidence path per outcome. Materialize primary evidence before downstream calculations.

Run the smallest relevant deterministic checks first. CI proves only what it executed. Merge and data/product release are separate; release requires the merged evidence/artifact/API/UI or fresh filing acquisition in scope to be directly verified.

Do not execute trades, financing, wallet transfers, or account actions.

## Completion

Re-read state before writes, read back after writes, and stop when the requested issuer evidence or release state is directly verified. Unchecked outcomes remain `UNVERIFIED`.
