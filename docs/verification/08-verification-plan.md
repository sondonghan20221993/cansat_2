# 08. Verification Plan

## 1. Purpose

요구사항이 올바르게 구현되었는지 검증하는 방법을 정의한다.

---

## 2. Verification Strategy

검증 흐름은 아래 순서를 따른다.

1. Unit testing
2. Module integration testing
3. System integration testing
4. Hardware testing
5. Performance validation

---

## 3. Unit Test Plan

### 3.1 UWB 모듈 단위 테스트

| TC ID       | 테스트 명                        | 입력 조건                                                        | 기대 출력                                                              | 대응 요구사항                        |
|-------------|----------------------------------|------------------------------------------------------------------|------------------------------------------------------------------------|--------------------------------------|
| TC-UWB-01   | 정상 4-Anchor trilateration      | 4개 Anchor 유효 거리값, 알려진 Tag 위치                          | valid=True, x/y/z 오차 ≤ 허용값, error_code=NONE                      | UWB-PROC-09, UWB-OUT-01              |
| TC-UWB-02   | 30 ms 대기 후 정상 수신          | Timer 만료 시 3개 수신 → 30 ms 내 4번째 수신                    | valid=True, trilateration 수행                                         | UWB-PROC-02, UWB-PROC-09             |
| TC-UWB-03   | 30 ms 대기 후에도 누락           | Timer 만료 시 3개 수신 → 30 ms 후에도 1개 누락                  | Invalid_Position, error_code=MISSING_DISTANCE                          | UWB-PROC-03                          |
| TC-UWB-04   | Timer 만료 시 전체 누락          | 4개 모두 미수신                                                  | Invalid_Position, error_code=MISSING_DISTANCE                          | UWB-PROC-02, UWB-PROC-03             |
| TC-UWB-05   | Non-positive 거리값 거부         | 거리값 ≤ 0인 Anchor 포함                                        | 해당 Anchor 결측 처리, error_code=NON_POSITIVE_RANGE                  | UWB-IN-04                            |
| TC-UWB-06   | Duplicate_Distance 처리          | 동일 Anchor_ID로 동일 사이클 내 2회 수신                        | 최신값 1개만 Distance_Set에 포함                                       | UWB-PROC-05                          |
| TC-UWB-07   | Residual 20 cm 초과 — valid 유지 | trilateration 성공, residual > 20 cm                            | valid=True, 경고 로그 기록                                             | UWB-PROC-17                          |
| TC-UWB-08   | Residual 20 cm 이하 — 경고 없음  | trilateration 성공, residual ≤ 20 cm                            | valid=True, 경고 로그 없음                                             | UWB-PROC-17                          |
| TC-UWB-09   | Trilateration 수치 실패          | 수치적으로 해가 없는 거리 조합 (NaN/inf, 음수 루트 등)          | Invalid_Position, error_code=NUMERIC_FAILURE                           | UWB-PROC-14                          |
| TC-UWB-10   | 기하학적 무효 배치               | Anchor 1,2,3이 동일점 또는 거의 일직선                          | Invalid_Position, error_code=GEOMETRY_INVALID                          | UWB-PROC-13                          |
| TC-UWB-11   | Z 해 2개 중 양수 선택            | Z 해가 +z, -z 두 개 도출되는 Anchor 배치                        | Z >= 0인 해 선택, valid=True                                           | UWB-PROC-11                          |
| TC-UWB-12   | Z 해 2개 모두 음수               | 두 Z 해가 모두 음수인 Anchor 배치                               | Invalid_Position, error_code=Z_INVALID                                 | UWB-PROC-12                          |
| TC-UWB-13   | Invalid 출력 필드 검증           | 임의 Invalid 조건                                               | x=NaN, y=NaN, z=NaN, residual=NaN, valid=False, 누락 distance=-1      | UWB-OUT-04, UWB-OUT-05, UWB-OUT-06, UWB-OUT-07 |
| TC-UWB-14   | Timestamp 검증                   | 4개 거리값 수신 시각이 상이                                     | timestamp = 마지막 수신 시각(cFS_TIME)                                 | UWB-OUT-09                           |
| TC-UWB-15   | 출력 주기 검증                   | 연속 사이클 실행                                                | 매 사이클 Position_Result 정확히 1회 발행                              | UWB-OUT-10                           |
| TC-UWB-16   | Round-trip 정확도 검증           | 알려진 위치에서 역산한 이론 거리값 입력                         | 추정 위치 오차 ≤ 허용 임계값                                           | UWB-PROC-10                          |

### 3.2 기타 모듈 단위 테스트

| Module                | Test Scope                    | Pass Criteria |
|-----------------------|-------------------------------|---------------|
| Reconstruction Module | Pipeline functions            | TBD           |
| Pose / Alignment Module | Transform and calibration logic | TBD         |
| cFS Integration Layer | Message and runtime behavior  | TBD           |

---

## 4. Module Integration Test Plan

모듈 간 연동 테스트 항목:

- UWB → Alignment
- Reconstruction → Alignment
- Alignment → cFS Integration

---

## 5. System Integration Test Plan

전체 end-to-end 시나리오:

- Nominal scenario
- Fault scenario
- Degraded mode scenario

---

## 6. Hardware Test Plan

- Sensor connectivity test
- Timing synchronization test
- Real environment operational test

---

## 7. Performance Validation Criteria

| Metric     | Target | Verification Method |
|------------|--------|---------------------|
| Latency    | TBD    | TBD                 |
| Throughput | TBD    | TBD                 |
| Accuracy   | TBD    | TBD                 |
| Stability  | TBD    | TBD                 |

---

## 8. Traceability

| Requirement ID   | Document                    | Verification Method | TC ID       |
|------------------|-----------------------------|---------------------|-------------|
| UWB-IN-04        | 04-uwb-requirements.md      | Unit Test           | TC-UWB-05   |
| UWB-PROC-02      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-02, TC-UWB-04 |
| UWB-PROC-03      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-03, TC-UWB-04 |
| UWB-PROC-05      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-06   |
| UWB-PROC-09      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-01   |
| UWB-PROC-10      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-16   |
| UWB-PROC-11      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-11   |
| UWB-PROC-12      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-12   |
| UWB-PROC-13      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-10   |
| UWB-PROC-14      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-09   |
| UWB-PROC-17      | 04-uwb-requirements.md      | Unit Test           | TC-UWB-07, TC-UWB-08 |
| UWB-OUT-04~07    | 04-uwb-requirements.md      | Unit Test           | TC-UWB-13   |
| UWB-OUT-09       | 04-uwb-requirements.md      | Unit Test           | TC-UWB-14   |
| UWB-OUT-10       | 04-uwb-requirements.md      | Unit Test           | TC-UWB-15   |

---

## 9. Open Items

- OI-VER-01: 허용 위치 오차 임계값(TC-UWB-16 pass criteria) 확정 필요
- OI-VER-02: GEOMETRY_INVALID 판별 임계값(condition number 기준) 확정 후
  TC-UWB-10 pass criteria 갱신 필요
- OI-VER-03: 각 모듈 단위 테스트 pass criteria TBD 항목 확정 필요
