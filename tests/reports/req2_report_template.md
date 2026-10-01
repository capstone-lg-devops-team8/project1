# requirement_2 검증 Report

| 항목 | 내용 |
|------|------|
| 프로젝트 | webOS Subscription Management Dashboard |
| 검증 대상 | requirement_2.md |
| 검증 일시 | 2026-10-01 17:13:12 |
| 작성자 | Test Engineer |

**총 12건 중 PASS 12 / FAIL 0 — Pass Rate 100.0%**

| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |
|:-----:|----------------|-----------|-----------|:----:|
| TE2-01 | /api/subscribers/U001/devices 호출 | D001, D002 두 가전 반환 | status=200, ids=['D001', 'D002'] | ✅ PASS |
| TE2-02 | /api/subscribers/U005/devices 호출 | 빈 배열 [] 반환 | status=200, body=[] | ✅ PASS |
| TE2-03 | /api/subscribers/U999/devices 호출 | 404 에러 | status=404 | ✅ PASS |
| TE2-04 | U001 클릭 시 가전 Table 표시 | D001, D002 표시 | 구현 확인 | ✅ PASS |
| TE2-05 | U005 클릭 시 안내 메시지 | No registered devices 표시 | 문구 존재 | ✅ PASS |
| TE2-06 | 가전 검색 "TV" | TV 타입만 표시 | 1개: ['D001'] | ✅ PASS |
| TE2-07 | 상태 필터 "Online" | Online 가전만 표시 | 1개: ['D001'] | ✅ PASS |
| TE2-08 | /api/devices/D001/usage 호출 | 사용 현황 JSON 반환 | status=200, missing=[] | ✅ PASS |
| TE2-09 | /api/devices/D999/usage 호출 | 404 에러 | status=404 | ✅ PASS |
| TE2-10 | D001 클릭 시 사용 현황 표시 | 전원상태, 누적시간 등 표시 | 구현 확인 | ✅ PASS |
| TE2-11 | D001 클릭 시 Bar Chart 표시 | 요일별 Bar Chart | Chart 구현 확인 | ✅ PASS |
| TE2-12 | 다른 가전 클릭 시 차트 갱신 | 기존 차트 제거 후 새 차트 표시 | destroy 로직 존재 | ✅ PASS |
