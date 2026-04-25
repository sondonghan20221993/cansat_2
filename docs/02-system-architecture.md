# 02. System Architecture

## 1. Overview

Describe the overall architecture and design intent.

The baseline cFS input path for the current system architecture uses the following SB
messages:

- `IMU_STATE_MID (0x1901)` from `imu_app`
- `GPS_STATE_MID (0x1902)` from `gps_app`
- `TELEMETRY_STATUS_MID (0x1903)` from `telemetry_app`
- `IMAGE_META_MID (0x1904)` from `img_app`

`IMAGE_META_MID` carries metadata and artifact references only. Raw image payload
transport is outside the baseline SB path.

## 2. Module Composition

List the major modules and their relationships.

| Module | Responsibility | Depends On |
| --- | --- | --- |
| UWB Module | Optional position estimation from anchor/tag data | Sensor input; may be disabled by mission configuration |
| GPS Interface | Global position acquisition and local frame conversion support | GPS receiver |
| IMU Interface | Attitude, angular rate, and acceleration acquisition | IMU sensor |
| Telemetry Interface | Communication-link state assessment and publication | Mission transport path |
| Image Interface | Image capture metadata publication | Camera capture path |
| Reconstruction Module | 3D reconstruction from image/sensor input | Camera and sensor input |
| Pose / Frame Alignment Module | Coordinate frame alignment and calibration | UWB, GPS, IMU, camera, and reconstruction outputs |
| cFS Integration Layer | Runtime integration, messaging, configuration, logging | All functional modules |

## 3. Module Responsibilities

### 3.1 UWB Module

- Estimate distance and position
- Validate ranging data
- Provide structured outputs
- Support clean disable/removal through configuration without blocking GPS, IMU, reconstruction, or alignment processing

### 3.2 Reconstruction Module

- Process input images and sensor data
- Generate 3D reconstruction outputs
- Apply quality checks

### 3.3 GPS Interface

- Receive GPS position and timestamp data
- Preserve raw WGS84 measurements
- Provide local-frame conversion inputs to the alignment module

### 3.4 IMU Interface

- Receive vehicle attitude, angular rate, and acceleration data
- Preserve IMU/body-frame metadata
- Provide orientation constraints to the alignment module

### 3.5 Telemetry Interface

- Assess communication-link health from the active transport path
- Publish `TELEMETRY_STATUS_MID (0x1903)`
- Report `ALIVE`, `DEGRADED`, and `LOST` link-state transitions

### 3.6 Image Interface

- Detect completed image capture events
- Publish `IMAGE_META_MID (0x1904)` at low rate
- Carry image identifiers, timestamps, and artifact references only

### 3.7 Pose / Frame Alignment Module

- Manage frame transforms
- Apply offsets and calibration
- Produce unified coordinate outputs
- Align UWB, GPS, IMU, camera, and reconstruction frames into the World / Map frame

### 3.8 cFS Integration Layer

- Manage application lifecycle
- Publish and subscribe messages
- Handle configuration, events, and timers

## 4. Data Flow

Describe how information moves between modules.

1. `imu_app`, `gps_app`, `telemetry_app`, and `img_app` publish the baseline required
   SB input set.
2. The Reconstruction Module consumes `IMAGE_META_MID` and fetches the referenced image
   artifact outside SB.
3. UWB processing runs only when the optional UWB source path is enabled.
4. Alignment logic transforms source outputs into a common World / Map frame.
5. cFS integration distributes outputs to downstream consumers.

If UWB is disabled or unavailable, data flow SHALL continue with the remaining enabled sources and the alignment output SHALL record UWB as unavailable.

## 5. Connectivity Between Modules

| Source Module | Target Module | Interface Type | Notes |
| --- | --- | --- | --- |
| UWB Module | Pose / Frame Alignment Module | Data message | Position and ranging result |
| GPS Interface | Pose / Frame Alignment Module | Data message | GPS position and timestamp |
| IMU Interface | Pose / Frame Alignment Module | Data message | Attitude, angular rate, acceleration |
| Telemetry Interface | cFS Integration Layer | SB message | `TELEMETRY_STATUS_MID (0x1903)` |
| Image Interface | Reconstruction Module | SB message | `IMAGE_META_MID (0x1904)`; metadata/reference only |
| Reconstruction Module | Pose / Frame Alignment Module | Data message | 3D result and metadata |
| Pose / Frame Alignment Module | Reconstruction Module / Map Manifest | Metadata update | Per-chunk transform and alignment_status update via accumulated map manifest interface |
| Pose / Frame Alignment Module | cFS Integration Layer | Data message | Unified output |
| cFS Integration Layer | All Modules | Control/config interface | Runtime control |

## 6. Architecture Constraints

- Use consistent interface definitions across modules.
- Preserve traceability from requirements to verification.
- Isolate module responsibilities where possible.
- Treat UWB as an optional source module, not as a mandatory dependency of reconstruction or accumulated map visualization.

## 7. Open Items

- OI-ARCH-01: Deployment split between ground-side Raspberry Pi, remote GPU server, and any onboard/drone-side process needs to be finalized.
- OI-ARCH-02: Large artifact transfer path for reconstruction outputs needs to be finalized against cFS SB payload limits and storage constraints.
- OI-ARCH-03: Failure isolation policy between UWB, reconstruction, alignment, and cFS integration needs to be finalized.
