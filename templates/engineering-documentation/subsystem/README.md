# L1 subsystem profiles

Use an L1 profile only when a subsystem has an independently reviewable
responsibility boundary and meaningful failure, security, lifecycle, contract,
change, or quality complexity.

- [`compact/`](./compact/) — bounded component with modest internal structure.
- [`standard/`](./standard/) — durable state, command, trust, or recovery owner.
- [`full/`](./full/) — independently deployed or restarted failure domain.

Copy the selected directory under the adopting repository's architecture tree,
replace template prompts, add it to the subsystem index, and link it from the L0
chapters. Profile selection changes documentation depth, not system
architecture.
