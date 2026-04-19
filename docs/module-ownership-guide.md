# Module Ownership Guide

## 1. Purpose

This guide defines how to split requirements across parallel development tracks so that UWB, 3D mapping, pose alignment, and cFS integration can be developed independently and merged cleanly.

## 2. Recommended Team Split

### 2.1 UWB Team

Owns:

- Distance message reception from anchors
- Distance filtering and validation
- Distance set construction
- Trilateration logic
- Residual calculation
- Valid and invalid result generation
- UWB-side performance and algorithm tests

Primary documents:

- [03-interface-specification.md](03-interface-specification.md)
- [04-uwb-requirements.md](modules/04-uwb-requirements.md)
- [08-verification-plan.md](verification/08-verification-plan.md)

### 2.2 3D Mapping Team

Owns:

- Image and sensor input requirements
- Reconstruction pipeline
- Reconstruction outputs and quality criteria
- Mapping-side tests

Primary documents:

- [03-interface-specification.md](03-interface-specification.md)
- [05-reconstruction-requirements.md](modules/05-reconstruction-requirements.md)
- [08-verification-plan.md](verification/08-verification-plan.md)

### 2.3 Pose / Frame Alignment Team

Owns:

- UWB frame, camera frame, and map frame definitions
- Transform logic
- Calibration and offset parameters
- Alignment validation

Primary documents:

- [03-interface-specification.md](03-interface-specification.md)
- [06-pose-frame-alignment-requirements.md](modules/06-pose-frame-alignment-requirements.md)
- [08-verification-plan.md](verification/08-verification-plan.md)

### 2.4 cFS Team

Owns:

- cFS app lifecycle
- SB message routing
- Timer behavior
- Configuration loading
- Logging and event handling
- Runtime integration between modules

Primary documents:

- [02-system-architecture.md](02-system-architecture.md)
- [03-interface-specification.md](03-interface-specification.md)
- [07-cfs-integration-requirements.md](modules/07-cfs-integration-requirements.md)
- [08-verification-plan.md](verification/08-verification-plan.md)

## 3. Document Allocation Rules

Use the following rule of thumb when writing or moving requirements.

| If the requirement is about... | Put it in... |
| --- | --- |
| Overall mission, scope, common units, system-wide constraints | [01-system-requirements.md](01-system-requirements.md) |
| Which module connects to which module | [02-system-architecture.md](02-system-architecture.md) |
| Message fields, structure definitions, timestamp rules, coordinate conventions, error representation | [03-interface-specification.md](03-interface-specification.md) |
| UWB distance handling and trilateration behavior | [04-uwb-requirements.md](modules/04-uwb-requirements.md) |
| Image-based 3D reconstruction behavior | [05-reconstruction-requirements.md](modules/05-reconstruction-requirements.md) |
| Coordinate frame transform and calibration behavior | [06-pose-frame-alignment-requirements.md](modules/06-pose-frame-alignment-requirements.md) |
| cFS execution, SB, timers, config, and event logging | [07-cfs-integration-requirements.md](modules/07-cfs-integration-requirements.md) |
| How to test or verify any requirement | [08-verification-plan.md](verification/08-verification-plan.md) |

## 4. How To Place The UWB Requirement Set

Your current UWB requirement draft should not be copied into only one file. It should be split as follows.

### 4.1 Move to System Requirements

- Coordinate system definition as a system-wide rule
- Anchor coordinate loading as a top-level operating constraint
- Global timestamp policy
- Global logging policy
- System-level update-rate and performance targets

### 4.2 Move to Interface Specification

- Distance message format
- `Position_Result` field definitions
- Units, timestamp basis, `NaN` and `-1` conventions
- Error code representation and propagation rules

### 4.3 Move to UWB Requirements

- Distance reception and filtering behavior
- Duplicate distance handling
- Distance set construction
- Output cycle timer behavior for UWB positioning
- Planar trilateration behavior
- Residual calculation
- Valid and invalid position decision rules
- UWB-side performance requirements

### 4.4 Move to Verification Plan

- Python algorithm tests
- Round-trip trilateration tests
- Invalid input tests
- Residual validation tests
- Duplicate-distance handling tests
- Hardware integration tests with anchors and tag

## 5. Merge Strategy

To merge parallel development work cleanly:

1. Freeze shared interface definitions first.
2. Let each team update only its owned module document for internal logic.
3. Route any cross-team contract change through the interface document.
4. Reflect integration impacts in the architecture document.
5. Add or update verification items whenever a requirement changes.

## 6. Anti-Patterns To Avoid

- Do not define the same message field in multiple module documents.
- Do not redefine coordinate systems independently in different module documents.
- Do not put cFS runtime behavior inside the UWB algorithm document.
- Do not put reconstruction internals inside the cFS integration document.
- Do not place test procedures only inside module documents without traceability in the verification plan.

## 7. Suggested Next Step

Use this guide to refactor the current UWB draft into:

- system rules in `01-system-requirements.md`
- message and result contracts in `03-interface-specification.md`
- algorithm behavior in `04-uwb-requirements.md`
- test content in `08-verification-plan.md`
