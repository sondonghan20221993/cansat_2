# 04. UWB Requirements

## 1. Purpose

UWB Anchor 4개와 Tag 1개의 거리 측정값을 이용하여 드론의 3차원 위치를
추정하는 UWB 모듈의 동작 요구사항을 정의한다.

좌표계, 단위, 타임스탬프 기준, Position_Result 메시지 구조,
Error_Code 정의는 03-interface-specification.md를 따른다.

---

## 2. Functional Scope

- 거리 데이터 수신 (Distance Reception)
- 거리 필터링 및 유효성 검사 (Distance Filtering)
- Distance_Set 구성 (Distance Set Construction)
- Output_Cycle_Timer 기반 처리 흐름 (Timer-Based Processing)
- Planar Trilateration 계산
- Residual 계산
- Valid / Invalid 결과 분류 및 출력

---

## 3. 입력 요구사항

### 3.1 Anchor 구성

- **UWB-IN-01**: UWB 모듈은 정확히 4개의 Anchor로부터 거리 측정값을
  수신하도록 구성 SHALL.
- **UWB-IN-02**: 각 Anchor는 고유한 Anchor_ID를 가지며, 모듈은
  Anchor_ID를 기준으로 거리 측정값을 구분 SHALL.
- **UWB-IN-03**: 각 Anchor의 3차원 좌표는 시스템 설정 파라미터로부터
  로드 SHALL. *(좌표 로딩 정책은 01-system-requirements.md 참조)*

### 3.2 거리 측정값 유효성

- **UWB-IN-04**: UWB 모듈은 수신된 거리 측정값이 0 이하(non-positive)인
  경우 해당 값을 거부하고 해당 Anchor를 결측으로 처리 SHALL.
  이 경우 Error_Code = NON_POSITIVE_RANGE를 설정 SHALL.
- **UWB-IN-05**: UWB 모듈은 거리 측정값의 단위로 cm를 사용 SHALL.
  *(단위 정책은 03-interface-specification.md 참조)*

---

## 4. 처리 요구사항

### 4.1 Output_Cycle_Timer 기반 처리 흐름

- **UWB-PROC-01**: UWB 모듈은 Output_Cycle_Timer 만료 이벤트를
  트리거로 하여 위치 추정 처리를 시작 SHALL.
- **UWB-PROC-02**: Output_Cycle_Timer 만료 시점에 4개 Anchor의 거리값이
  모두 수신되지 않은 경우, 모듈은 30 ms 추가 대기 SHALL.
- **UWB-PROC-03**: 30 ms 추가 대기 후에도 하나 이상의 Anchor 거리값이
  누락된 경우, 모듈은 trilateration을 수행하지 않고
  Invalid_Position을 출력 SHALL.
  이 경우 Error_Code = MISSING_DISTANCE를 설정 SHALL.
- **UWB-PROC-04**: UWB 모듈은 Output_Cycle_Timer 만료 후 다음 사이클
  시작 전에 이전 사이클의 Distance_Set을 초기화 SHALL.

### 4.2 Duplicate Distance 처리

- **UWB-PROC-05**: 동일 Output_Cycle 내에 동일 Anchor_ID로부터 거리
  측정값이 2회 이상 수신된 경우(Duplicate_Distance), 모듈은
  가장 최근에 수신된 값 1개만 Distance_Set에 포함 SHALL.

### 4.3 Distance_Set 구성

- **UWB-PROC-06**: UWB 모듈은 Output_Cycle_Timer 처리 완료 시점에
  유효한 거리 측정값들을 모아 Distance_Set을 구성 SHALL.
- **UWB-PROC-07**: Distance_Set은 Anchor_ID와 거리 값(cm)의 쌍(pair)으로
  구성 SHALL.
- **UWB-PROC-08**: UWB 모듈은 Distance_Set 구성 시 유효 Anchor 수를
  함께 기록 SHALL.

### 4.4 Planar Trilateration

- **UWB-PROC-09**: UWB 모듈은 4개 Anchor 거리값이 모두 유효한 경우에만
  Planar_Trilateration을 수행 SHALL.

- **UWB-PROC-10**: Planar_Trilateration은 XY 좌표를 먼저 계산한 후,
  거리식을 이용하여 Z 좌표를 복원 SHALL.

- **UWB-PROC-11**: Z 해가 2개 도출된 경우, UWB 모듈은 Z >= 0인 해를
  선택 SHALL.

- **UWB-PROC-12**: 두 Z 해가 모두 음수인 경우, 모듈은 Invalid_Position을
  출력하고 Error_Code = Z_INVALID를 설정 SHALL.

- **UWB-PROC-13**: Anchor 1, 2, 3 배치가 동일점이거나 거의 일직선이어서
  XY 평면 정의가 불가능한 경우, 모듈은 Invalid_Position을 출력하고
  Error_Code = GEOMETRY_INVALID를 설정 SHALL.

- **UWB-PROC-14**: 기하 전처리를 통과한 후 수치 계산 단계에서
  NaN/inf 발생, 음수 루트, 행렬 분해 실패, condition number 임계 초과,
  연립방정식 해 계산 실패 등이 발생한 경우, 모듈은 Invalid_Position을
  출력하고 Error_Code = NUMERIC_FAILURE를 설정 SHALL.

### 4.5 Residual 계산

- **UWB-PROC-15**: UWB 모듈은 각 Anchor에 대해 계산된 거리와 입력
  거리의 절대 오차를 산출 SHALL.

- **UWB-PROC-16**: UWB 모듈은 4개 Anchor 절대 오차의 평균값을
  Residual(cm)로 산출 SHALL.

- **UWB-PROC-17**: Residual이 20 cm를 초과하는 경우, 모듈은 valid를
  유지하고 경고 로그를 기록 SHALL.
  *(로그 정책은 01-system-requirements.md 참조)*

---

## 5. 출력 요구사항

### 5.1 Valid Position 출력

- **UWB-OUT-01**: Planar_Trilateration이 성공하고 Invalid 조건에 해당하지
  않는 경우, 모듈은 valid = True인 Position_Result를 출력 SHALL.
- **UWB-OUT-02**: Valid Position_Result의 x, y, z 필드는 Planar_Trilateration
  결과값(cm)으로 설정 SHALL.
- **UWB-OUT-03**: Valid Position_Result의 residual 필드는 계산된
  Residual 값(cm)으로 설정 SHALL.

### 5.2 Invalid Position 출력

- **UWB-OUT-04**: Invalid_Position 출력 시 Position_Result의 x, y, z
  필드는 NaN으로 설정 SHALL.
- **UWB-OUT-05**: Invalid_Position 출력 시 누락된 Anchor의 distance
  필드는 -1로 설정 SHALL.
- **UWB-OUT-06**: Invalid_Position 출력 시 residual 필드는 NaN으로
  설정 SHALL.
- **UWB-OUT-07**: Invalid_Position 출력 시 valid 필드는 False로
  설정 SHALL.
- **UWB-OUT-08**: Invalid_Position 출력 시 해당 원인에 맞는 Error_Code를
  설정 SHALL. *(Error_Code 정의는 03-interface-specification.md 참조)*

### 5.3 Timestamp

- **UWB-OUT-09**: Position_Result의 timestamp는 Distance_Set 내 마지막
  거리값 수신 시각(cFS_TIME)으로 설정 SHALL.
  *(타임스탬프 기준은 03-interface-specification.md 참조)*

### 5.4 출력 주기

- **UWB-OUT-10**: UWB 모듈은 매 Output_Cycle마다 Position_Result를
  정확히 1회 발행 SHALL.

---

## 6. 성능 요구사항

- **UWB-PERF-01**: 위치 추정 처리(Distance_Set 구성 완료 시점부터
  Position_Result 발행까지)는 Output_Cycle_Timer 주기 내에
  완료 SHALL.
- **UWB-PERF-02**: 위치 추정 정확도 목표값은 01-system-requirements.md를
  따른다.

---

## 7. Open Items

- OI-01: GEOMETRY_INVALID 판정을 위한 "거의 일직선" 판별 임계값(예: condition number
  기준)을 시스템 레벨에서 확정 필요
- OI-02: Output_Cycle_Timer 주기 값은 07-cfs-integration-requirements.md에서
  확정 필요
- OI-03: Residual 경고 로그의 로그 레벨 및 로그 ID는
  07-cfs-integration-requirements.md에서 확정 필요
- OI-04: NUMERIC_FAILURE 판정을 위한 condition number 임계값을
  알고리즘 설계 단계에서 확정 필요
- OI status update: OI-02 is resolved by 07-cfs-integration-requirements.md
  CFS-TMR-01 with a 66 ms nominal Output_Cycle_Timer period. OI-03 is
  partially resolved by CFS-LOG-02 with WARNING log level; stable event/log ID
  remains open under OI-CFS-02.
