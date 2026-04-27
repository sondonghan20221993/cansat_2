# 07. cFS Integration Requirements

## 1. Purpose

Define requirements for integrating modules into the cFS environment.

## 2. cFS App Structure

- **CFS-APP-01**: Each runtime module SHALL be integrated as a cFS-compatible app or app-managed component with an explicit initialization path.
- **CFS-APP-02**: The integration layer SHALL initialize configuration, Software Bus subscriptions, timers, and event services before entering the main processing loop.
- **CFS-APP-03**: The main loop SHALL process subscribed messages, timer events, and module status updates without blocking unrelated module execution.
- **CFS-APP-04**: Shutdown behavior SHALL release module resources and record final status through cFS event/log mechanisms.
- **CFS-APP-05**: `telemetry_app` SHALL be implemented as the cFS app responsible for active transport monitoring and publication of `TELEMETRY_STATUS_MID`.
- **CFS-APP-06**: `telemetry_app` SHALL publish link-state classification using `ALIVE`, `DEGRADED`, or `LOST`.
- **CFS-APP-07**: `img_app` SHALL publish `IMAGE_META_MID` containing image metadata and artifact reference information only.
- **CFS-APP-08**: `imu_app` and `gps_app` SHALL publish timestamped sensor state messages onto SB using the interface definitions in 03-interface-specification.md.

## 3. Software Bus Message Handling

The baseline required SB input set SHALL consist of `IMU_STATE_MID (0x1901)`,
`GPS_STATE_MID (0x1902)`, `TELEMETRY_STATUS_MID (0x1903)`, and
`IMAGE_META_MID (0x1904)`. `IMAGE_META_MID` SHALL carry metadata and artifact
reference fields only and SHALL NOT carry raw image binary payload in the
baseline SB path.

- **CFS-SB-01**: The integration layer SHALL route UWB Position_Result messages through cFS Software Bus for downstream alignment and logging.
- **CFS-SB-02**: The integration layer SHALL route reconstruction request/result metadata through cFS Software Bus or a documented bridge when the payload is too large for direct SB transport.
- **CFS-SB-03**: The integration layer SHALL preserve message timestamp, source module identifier, status, and payload reference fields across module boundaries.
- **CFS-SB-04**: Message IDs, source IDs, and payload schema ownership SHALL follow 03-interface-specification.md.
- **CFS-SB-05**: `imu_app` SHALL publish `IMU_STATE_MID (0x1901)` on SB.
- **CFS-SB-06**: `gps_app` SHALL publish `GPS_STATE_MID (0x1902)` on SB.
- **CFS-SB-07**: `telemetry_app` SHALL publish `TELEMETRY_STATUS_MID (0x1903)` on SB.
- **CFS-SB-07A**: The telemetry monitor-input producer SHALL provide `active_transport_id`, `valid`, and `update_age_ms` to `telemetry_app` for link-state assessment.
- **CFS-SB-08**: `img_app` SHALL publish `IMAGE_META_MID (0x1904)` on SB at a controlled low rate appropriate for image capture events.
- **CFS-SB-09**: The Pose / Frame Alignment Module SHALL subscribe to `IMU_STATE_MID (0x1901)` and `GPS_STATE_MID (0x1902)`.
- **CFS-SB-10**: The Reconstruction Module SHALL subscribe to `IMAGE_META_MID (0x1904)`.
- **CFS-SB-11**: The cFS Integration Layer SHALL subscribe to `TELEMETRY_STATUS_MID (0x1903)` for runtime health and communication-state handling.
- **CFS-SB-12**: When UWB is disabled, the absence of UWB-specific SB messages SHALL NOT prevent IMU, GPS, telemetry, image metadata, reconstruction, or non-UWB alignment flows from entering nominal operation.

## 3A. Communication Link Separation Requirements

The system operates two distinct communication link roles. Each link SHALL be independently managed, monitored, and reported within the cFS integration layer.

### Link Role Assignment

- **CFS-LNK-01**: The LoRa telemetry link (`link_role = LORA`) SHALL carry heartbeat, housekeeping (HK), status, fault/event reports, and uplink command traffic only.
- **CFS-LNK-02**: The image/video link (`link_role = IMG_VID`) SHALL carry image frames, video streams, large payload transfers, and reconstruction artifact traffic only.
- **CFS-LNK-03**: Traffic classes assigned to the LoRa link SHALL NOT be routed over the image/video link, and vice versa, unless an explicit fallback policy is documented and approved.

### Independent Health State Management

- **CFS-LNK-04**: The LoRa link health state SHALL be managed exclusively by `telemetry_app` and published via `TELEMETRY_STATUS_MID (0x1903)` with `link_role = LORA`.
- **CFS-LNK-05**: The image/video link health state SHALL be managed by a dedicated monitor component (e.g., `img_link_app` or equivalent) and published via a separate SB message with `link_role = IMG_VID`. The MID for this message is TBD (see OI-CFS-04).
- **CFS-LNK-06**: The health state of the LoRa link SHALL NOT be inferred from or overridden by the health state of the image/video link, and vice versa.
- **CFS-LNK-07**: Both link health states SHALL independently use the `ALIVE`, `DEGRADED`, and `LOST` classification defined in 03-interface-specification.md Section 3.6.2.
- **CFS-LNK-08**: Both link health states SHALL support independent configuration of degraded and lost thresholds.

### Timestamp and Correlation at the cFS Boundary

- **CFS-LNK-09**: All messages published on the cFS Software Bus SHALL carry a vehicle-generated `cFS_TIME` timestamp set at the point of creation on the vehicle. Relay or bridge components SHALL NOT overwrite the vehicle-generated `timestamp` field.
- **CFS-LNK-10**: `img_app` SHALL assign a unique `image_id` to each image capture event at the time of capture and SHALL include this `image_id` in `IMAGE_META_MID`.
- **CFS-LNK-11**: Any LoRa status or event message that references the same image capture event SHALL carry the same `image_id` value as the corresponding `IMAGE_META_MID`.
- **CFS-LNK-12**: Reconstruction-related messages SHALL carry the `job_id` assigned at job submission time. The `job_id` SHALL be preserved unchanged through the reconstruction request, result, and any associated LoRa event messages.
- **CFS-LNK-13**: The `seq` field SHALL be assigned by the originating module and SHALL NOT be reassigned by relay or bridge components.

## 4. Timer Requirements

- **CFS-TMR-01**: The UWB Output_Cycle_Timer period SHALL be 66 ms nominal to support 15 Hz output.
- **CFS-TMR-02**: The UWB missing-distance grace timeout SHALL be 30 ms after Output_Cycle_Timer expiry.
- **CFS-TMR-03**: Timers SHALL use cFS timer services or an equivalent cFS-managed scheduling mechanism.
- **CFS-TMR-04**: Timer callbacks SHALL enqueue work or signal module state; they SHALL NOT perform long-running reconstruction or blocking I/O directly.
- **CFS-TMR-05**: For the baseline deployment, the telemetry monitor-input producer SHALL assume a nominal heartbeat period of `500 ms`.
- **CFS-TMR-06**: For the baseline deployment, the telemetry monitor-input producer SHALL evaluate and publish telemetry monitor freshness at least every `100 ms`.
- **CFS-TMR-07**: `telemetry_app` SHALL transition to `DEGRADED` after `1000 ms` without a valid monitor update.
- **CFS-TMR-08**: `telemetry_app` SHALL transition to `LOST` after `3000 ms` without a valid monitor update.
- **CFS-TMR-09**: `telemetry_app` SHALL support configuration of degraded and lost-link thresholds distinct from the nominal heartbeat period.
- **CFS-TMR-10**: `telemetry_app` SHALL transition from `DEGRADED` or `LOST` to `ALIVE` after one valid telemetry monitor update in the baseline deployment.
- **CFS-TMR-11**: `img_app` SHALL publish `IMAGE_META_MID` on image capture completion events only and SHALL support a configurable low-rate publication policy.

## 5. Configuration Management

- **CFS-CFG-01**: Startup configuration SHALL include Anchor coordinates, module enable flags, reconstruction endpoint settings, output format, and alignment transform parameters.
- **CFS-CFG-02**: Configuration validation SHALL occur during initialization before publishing module outputs.
- **CFS-CFG-03**: Invalid required configuration SHALL prevent the affected module from entering nominal operation and SHALL emit a traceable event.
- **CFS-CFG-04**: Runtime parameter updates SHALL be accepted only for fields explicitly marked runtime-changeable in the owning module specification.
- **CFS-CFG-05**: The UWB module SHALL be individually enableable/disableable through configuration. When disabled, missing UWB-specific configuration such as Anchor coordinates SHALL NOT prevent non-UWB modules from entering nominal operation.
- **CFS-CFG-06**: `telemetry_app` SHALL support configuration of nominal, degraded, and lost-link thresholds.
- **CFS-CFG-07**: `telemetry_app` SHALL support configuration of the active transport identifier used for link-state assessment.
- **CFS-CFG-08**: `img_app` SHALL support configuration of image metadata publication rate limits.
- **CFS-CFG-09**: The baseline active transport identifier for telemetry link-state assessment SHALL be `1`.
- **CFS-CFG-10**: Runtime updates to telemetry timing parameters SHALL first be written to a pending configuration buffer.
- **CFS-CFG-11**: A pending telemetry configuration SHALL be validated before activation.
- **CFS-CFG-12**: Invalid pending telemetry configuration values SHALL NOT overwrite the active configuration.
- **CFS-CFG-13**: The active telemetry configuration SHALL only be replaced at a documented safe application point.
- **CFS-CFG-14**: `telemetry_app` housekeeping SHALL expose the currently active telemetry timing parameters and configuration update status.

## 5A. Deployment-Specific Telemetry Link Rules

- **CFS-DEP-01**: For Linux-based deployments using a serial-connected telemetry radio, the telemetry monitor-input producer SHOULD use a stable device path under `/dev/serial/by-id/` when available.
- **CFS-DEP-02**: Enumeration-dependent serial paths such as `/dev/ttyUSB*` SHOULD be treated as fallback or debug-only paths unless the deployment environment guarantees stable naming.
- **CFS-DEP-03**: The deployment configuration SHALL document the serial device path, baud rate, and active transport identifier used by the telemetry monitor-input producer.

## 6. Logging and Event Handling

- **CFS-LOG-01**: The integration layer SHALL define log/event levels: INFO, WARNING, ERROR, and DIAGNOSTIC.
- **CFS-LOG-02**: Residual threshold exceedance in the UWB module SHALL be logged as WARNING with a stable event identifier.
- **CFS-LOG-03**: Invalid_Position, remote reconstruction failure, alignment failure, and configuration validation failure SHALL be logged as ERROR unless the owning module explicitly marks the condition as degraded-but-usable.
- **CFS-LOG-04**: Diagnostic logs SHALL preserve enough context for post-run analysis, including timestamp, source module, status/error code, and relevant payload references.
- **CFS-LOG-05**: `telemetry_app` SHALL log transitions into `DEGRADED` and `LOST` at `WARNING` and `ERROR` levels respectively.
- **CFS-LOG-06**: `telemetry_app` SHALL log recovery from `LOST` to `ALIVE` or `DEGRADED` at `INFO` level.
- **CFS-LOG-07**: Invalid or unreachable image artifact references SHALL be logged as `ERROR` by `img_app` or the Reconstruction Module.

## 7. Module Integration Method

| Module | Integration Pattern | Trigger | Output Destination |
| --- | --- | --- | --- |
| `imu_app` | SB publisher | IMU sample ready | `IMU_STATE_MID (0x1901)` |
| `gps_app` | SB publisher | GPS sample ready | `GPS_STATE_MID (0x1902)` |
| `telemetry_app` | SB publisher | LoRa link status update | `TELEMETRY_STATUS_MID (0x1903)` with `link_role = LORA` |
| `img_link_app` (or equivalent) | SB publisher | Image/video link status update | Image/video link health MID (TBD) with `link_role = IMG_VID` |
| `img_app` | SB publisher | Image capture complete | `IMAGE_META_MID (0x1904)` with `image_id` assigned at capture |
| UWB Module | Timer-driven processing app/component | Output_Cycle_Timer and distance messages | Position_Result SB topic, logs/events |
| Reconstruction Module | Request/response bridge to remote execution path | Image-set ready event or explicit job request | Reconstruction result metadata SB topic, artifact reference |
| Pose / Alignment Module | Message-driven transform processor | New source pose/result or transform config update | Aligned pose/transform metadata SB topic |

## 8. Test Requirements

- **CFS-VER-01**: The verification plan SHALL include tests for app initialization and shutdown behavior.
- **CFS-VER-02**: The verification plan SHALL include tests for Software Bus routing and payload reference preservation.
- **CFS-VER-03**: The verification plan SHALL include tests for timer behavior and non-blocking callback policy.
- **CFS-VER-04**: The verification plan SHALL include tests for configuration validation and runtime update policy.
- **CFS-VER-05**: The verification plan SHALL include failure-injection tests for event and logging behavior.
- **CFS-VER-06**: The verification plan SHALL include tests for baseline SB input publication and subscription for `0x1901` through `0x1904`.
- **CFS-VER-07**: The verification plan SHALL include tests for `telemetry_app` degraded/lost/recovery transitions.
- **CFS-VER-08**: The verification plan SHALL include tests verifying that LoRa link health state transitions are independent of image/video link health state transitions (CFS-LNK-06).
- **CFS-VER-09**: The verification plan SHALL include tests verifying that `image_id` assigned by `img_app` at capture time is preserved unchanged in `IMAGE_META_MID` and in any associated LoRa event message referencing the same capture event (CFS-LNK-10, CFS-LNK-11).
- **CFS-VER-10**: The verification plan SHALL include tests verifying that vehicle-generated `timestamp` fields are not overwritten by relay or bridge components (CFS-LNK-09).
- **CFS-VER-11**: The verification plan SHALL include tests verifying that `job_id` is preserved unchanged from reconstruction request through result and associated LoRa event messages (CFS-LNK-12).

## 9. Open Items

- OI-CFS-01: Exact cFS message IDs and source IDs need to be assigned.
- OI-CFS-02: Stable event IDs for UWB residual warning and module failure cases need to be assigned.
- OI-CFS-03: Runtime-changeable configuration fields need to be finalized per module.
- OI-CFS-04: MID assignment for the image/video link health state message (Section 3A, CFS-LNK-05) needs to be finalized.
- OI-CFS-05: The app name and integration pattern for the image/video link monitor component (Section 3A, CFS-LNK-05) need to be decided — standalone `img_link_app` vs. component within `img_app`.
- OI-CFS-06: Degraded and lost threshold defaults for the image/video link (CFS-LNK-08) need to be defined, analogous to CFS-TMR-07 and CFS-TMR-08 for the LoRa link.
