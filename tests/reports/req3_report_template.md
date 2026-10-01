# requirement_3 검증 Report

| 항목 | 내용 |
|------|------|
| 프로젝트 | webOS Subscription Management Dashboard |
| 검증 대상 | requirement_3.md |
| 검증 일시 | 2026-10-01 17:13:16 |
| 작성자 | Test Engineer |

**총 13건 중 PASS 12 / FAIL 0 / BLOCKED 1**

| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |
|:-----:|----------------|-----------|-----------|:----:|
| TE3-01 | Active 상태 확인 | 초록 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-02 | Paused 상태 확인 | 파랑 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-03 | Expired 상태 확인 | 빨강 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-04 | Online 상태 확인 | 초록 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-05 | Offline 상태 확인 | 회색 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-06 | Error 상태 확인 | 빨강 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-07 | Power On 상태 확인 | 노랑 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-08 | Health Normal 상태 확인 | 초록 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-09 | Health Warning 상태 확인 | 빨강 badge | mapping=OK, css=OK | ✅ PASS |
| TE3-10 | main push 시 CI 자동 실행 설정 | GitHub Actions 자동 실행 | ci.yml 설정 확인 | ✅ PASS |
| TE3-11 | CI health 체크 | /health 체크 통과 | health 검사 설정 확인 | ✅ PASS |
| TE3-12 | CI API 테스트 | 3개 API 엔드포인트 검사 | API 검사 설정 확인 | ✅ PASS |
| TE3-13 | Render 배포 확인 | 배포 URL 접속 가능 | RENDER_URL 미지정 | ⏸ BLOCKED |
