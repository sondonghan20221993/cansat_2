# 05. Reconstruction Requirements

## 1. Purpose

This document defines the requirements for the image-based 3D reconstruction module.

The module shall use a DUSt3R-family pipeline as the primary reconstruction approach.
It shall accept image inputs collected from the drone, execute reconstruction on a
remote GPU server, and return 3D reconstruction outputs and quality metadata for
downstream integration.

At the current system planning stage, GLB is expected to be the most likely primary
external output format. However, both the reconstruction model and the output format
may change in future revisions, so the module shall be structured to support
replacement without breaking the module boundary contract.

Coordinate systems, timestamps, and shared interface rules shall follow the top-level
system documents and the interface specification.

## 2. Functional Scope

The reconstruction module scope includes:

- image input validation
- image and metadata packaging
- remote job submission to the reconstruction server
- DUSt3R-family inference and reconstruction processing
- 3D result generation
- quality evaluation
- result packaging and return to the ground-side system

The reconstruction module scope excludes:

- UWB-based position estimation
- cFS application lifecycle control
- final system-level frame alignment policy
- low-level camera device driver implementation

## 3. Input Requirements

### 3.1 Required Inputs

- REC-IN-01: The reconstruction module SHALL accept a set of input images captured by the drone.
- REC-IN-02: Each input image SHALL include a unique identifier and an acquisition timestamp.
- REC-IN-03: The reconstruction module SHALL reject corrupted or undecodable images.
- REC-IN-04: The reconstruction module SHALL require at least the minimum image count defined by the system before starting reconstruction.

### 3.2 Calibration and Metadata Inputs

- REC-IN-05: The reconstruction module SHALL accept camera intrinsic parameters when available.
- REC-IN-06: The reconstruction module SHALL accept image-associated metadata including timestamp and source identifier.
- REC-IN-07: The reconstruction module SHALL be able to operate without external camera pose input.
- REC-IN-08: The reconstruction module SHALL accept external pose, UWB position, or other localization information as optional auxiliary input when available.
- REC-IN-09: Optional auxiliary input SHALL not be a mandatory precondition for running reconstruction.

### 3.3 Ground-Side and Server-Side Input Handling

- REC-IN-10: The ground-side computer SHALL receive the input images and associated metadata before reconstruction request submission.
- REC-IN-11: The ground-side computer SHALL package reconstruction inputs and forward them to the remote reconstruction server.
- REC-IN-12: The reconstruction server SHALL execute DUSt3R-family inference on an NVIDIA RTX A6000-class GPU environment or equivalent.

## 4. Reconstruction Pipeline Requirements

### 4.1 Input Preparation

- REC-PROC-01: The reconstruction module SHALL validate image completeness and metadata consistency before launching reconstruction.
- REC-PROC-02: The reconstruction module SHALL record the number of input images, image resolution, and metadata availability at job start.
- REC-PROC-03: The reconstruction module SHALL support preprocessing steps required by the selected DUSt3R-family pipeline.

### 4.2 Reconstruction Processing

- REC-PROC-04: The reconstruction module SHALL use a DUSt3R-family method as the primary reconstruction pipeline.
- REC-PROC-05: The reconstruction module SHALL estimate scene structure from image inputs using the selected DUSt3R-family model.
- REC-PROC-06: The reconstruction module SHALL be modularized so that the selected reconstruction model can be replaced, upgraded, or reconfigured without changing the module boundary contract.
- REC-PROC-07: The reconstruction module SHALL use optional external pose or localization input only as auxiliary information when provided.
- REC-PROC-08: The reconstruction module SHALL continue to support image-only reconstruction when no auxiliary pose input is available.

### 4.3 Remote Execution

- REC-PROC-09: The ground-side computer SHALL submit reconstruction jobs to the remote GPU server.
- REC-PROC-10: The remote GPU server SHALL return reconstruction outputs and execution status to the ground-side computer after processing.
- REC-PROC-11: The reconstruction module SHALL preserve job identity between request and response so that returned outputs can be matched to the originating image set.
- REC-PROC-12: The reconstruction module SHALL record reconstruction failure status when remote execution fails, times out, or returns invalid outputs.

### 4.4 Result Packaging

- REC-PROC-13: The reconstruction module SHALL package the 3D reconstruction output together with quality metadata and processing status.
- REC-PROC-14: The reconstruction module SHALL distinguish successful, degraded, and invalid reconstruction outcomes.
- REC-PROC-15: The reconstruction module SHALL make the returned result available to downstream alignment or integration modules through a defined interface.

## 5. Output Requirements

### 5.1 Reconstruction Output

- REC-OUT-01: The reconstruction module SHALL output a 3D reconstruction result in a system-defined representation such as GLB, point cloud, mesh, or equivalent 3D scene structure.
- REC-OUT-02: The output SHALL include a reconstruction job identifier and processing timestamp.
- REC-OUT-03: The output SHALL include the set or identifier of input images used to generate the reconstruction.
- REC-OUT-04: At the current planning stage, GLB SHALL be treated as the most likely primary external output format for reconstruction result delivery.
- REC-OUT-05: The reconstruction module SHALL be modularized so that the external output format can be changed in future revisions without requiring redesign of the full reconstruction module.

### 5.2 Quality Metadata

- REC-OUT-06: The reconstruction module SHALL include quality metadata in each output.
- REC-OUT-07: Quality metadata SHALL include, at minimum, the number of input images used, processing status, and one or more reconstruction quality indicators.
- REC-OUT-08: The exact quality indicators shall be finalized in the interface specification and verification plan.

### 5.3 Failure Output

- REC-OUT-09: When reconstruction fails, the module SHALL return an invalid or failed result structure that downstream modules can detect consistently.
- REC-OUT-10: When only partial or low-confidence reconstruction is available, the module SHALL be able to mark the result as degraded.

## 6. Quality Requirements

- REC-QUAL-01: The reconstruction module SHALL provide a measurable indicator of reconstruction quality for each output.
- REC-QUAL-02: The reconstruction module SHALL support quality evaluation against system-defined thresholds.
- REC-QUAL-03: Detailed numeric thresholds for acceptable reconstruction quality SHALL be finalized before system verification.

## 7. Performance Requirements

- REC-PERF-01: The reconstruction pipeline SHALL be executable in a remote GPU server environment separate from the ground-side receiver.
- REC-PERF-02: The reconstruction module SHALL support NVIDIA RTX A6000-class GPU execution as the baseline deployment target.
- REC-PERF-03: The reconstruction module SHALL record job execution outcome and processing duration for each reconstruction request.
- REC-PERF-04: Detailed runtime and throughput targets SHALL be finalized in the system requirements and verification plan.

## 8. Error Handling Requirements

- REC-ERR-01: The reconstruction module SHALL stop or reject processing when the minimum required image input is not satisfied.
- REC-ERR-02: The reconstruction module SHALL report corrupted or unusable input images in logs or status metadata.
- REC-ERR-03: The reconstruction module SHALL report remote server execution failure or timeout as a reconstruction failure condition.
- REC-ERR-04: The reconstruction module SHALL provide a consistent degraded or invalid status when the returned result quality is below the accepted threshold.
- REC-ERR-05: All failure cases SHALL be traceable through logs, status fields, or verification artifacts.

## 9. Verification Requirements

- REC-VER-01: The test suite SHALL verify successful end-to-end reconstruction using representative image sets.
- REC-VER-02: The test suite SHALL verify reconstruction behavior when auxiliary pose input is absent.
- REC-VER-03: The test suite SHALL verify reconstruction behavior when auxiliary pose or localization input is provided.
- REC-VER-04: The test suite SHALL verify failure handling for corrupted images, insufficient images, and remote execution failure.
- REC-VER-05: The integration test plan SHALL verify remote job submission from the ground-side computer to the A6000-class reconstruction server and result return.

## 10. Open Items

- OI-01: Minimum image count for starting DUSt3R-family reconstruction needs to be finalized.
- OI-02: Camera intrinsic parameter provisioning method needs to be finalized.
- OI-03: GLB is currently the most likely primary external output format, but the officially frozen output representation format still needs to be finalized.
- OI-04: Reconstruction quality indicators and thresholds need to be finalized.
- OI-05: Degraded versus invalid status criteria need to be finalized.
- OI-06: The exact remote execution protocol between the ground-side computer and the A6000 server needs to be finalized.
