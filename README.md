# System Specification Documents

This repository contains the specification document framework for the overall system.

The document flow is:

`Overall Goal -> Architecture -> Interface -> Module Details -> Verification`

## Repository Structure

```text
docs/
  01-system-requirements.md
  02-system-architecture.md
  03-interface-specification.md
  modules/
    04-uwb-requirements.md
    05-reconstruction-requirements.md
    06-pose-frame-alignment-requirements.md
    07-cfs-integration-requirements.md
  verification/
    08-verification-plan.md
```

## Document Reading Order

1. [System Requirements](docs/01-system-requirements.md)
2. [System Architecture](docs/02-system-architecture.md)
3. [Interface Specification](docs/03-interface-specification.md)
4. [UWB Requirements](docs/modules/04-uwb-requirements.md)
5. [Reconstruction Requirements](docs/modules/05-reconstruction-requirements.md)
6. [Pose / Frame Alignment Requirements](docs/modules/06-pose-frame-alignment-requirements.md)
7. [cFS Integration Requirements](docs/modules/07-cfs-integration-requirements.md)
8. [Verification Plan](docs/verification/08-verification-plan.md)
9. [Module Ownership Guide](docs/module-ownership-guide.md)

## Team-Based Development Model

This repository is structured so that UWB, 3D mapping, pose alignment, and cFS integration can be developed in parallel and merged through shared architecture and interface documents.

### Ownership by document

- `docs/01-system-requirements.md`: system-level goals, common rules, global constraints
- `docs/02-system-architecture.md`: module composition, responsibilities, and end-to-end flow
- `docs/03-interface-specification.md`: contracts shared between teams
- `docs/modules/04-uwb-requirements.md`: UWB-specific logic and performance requirements
- `docs/modules/05-reconstruction-requirements.md`: 3D reconstruction module requirements
- `docs/modules/06-pose-frame-alignment-requirements.md`: frame and calibration logic
- `docs/modules/07-cfs-integration-requirements.md`: cFS app behavior, SB, timer, config, and events
- `docs/verification/08-verification-plan.md`: module and integrated verification strategy

### Development principle

- Keep module internals inside module documents.
- Keep cross-team message formats and data fields in the interface document.
- Keep system-wide assumptions and constraints in the top-level requirements.
- Keep integration behavior in the architecture and cFS documents.
- Keep test methods and acceptance evidence in the verification plan.

## Writing Rules

- Keep requirements clear, testable, and version-manageable.
- Use consistent terminology across all documents.
- Define interfaces before finalizing module implementations.
- Reflect changes in verification criteria whenever requirements change.

## Status

- This repository currently contains the initial specification template.
- Replace placeholder text with project-specific content.
