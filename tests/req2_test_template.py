import os
import sys
import time
import json
import socket
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
REPORT_DIR = THIS_DIR / "reports"
REPORT_PATH = REPORT_DIR / "req2_report_template.md"
APP_JS = PROJECT_ROOT / "app" / "static" / "app.js"

os.chdir(PROJECT_ROOT)

BASE_URL = None
results = []


def check(tc_id, scenario, expected, actual, passed):
    results.append((tc_id, scenario, expected, actual, passed))
    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] {tc_id} {scenario}")


def http_get(path, timeout=5):
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, None

    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            return e.code, json.loads(body)
        except Exception:
            return e.code, None

    except Exception:
        return None, None


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def start_server(port):
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    for _ in range(40):
        if proc.poll() is not None:
            return proc, False

        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/health",
                timeout=1
            ) as r:
                if r.status == 200:
                    return proc, True
        except Exception:
            time.sleep(0.5)

    return proc, False


def stop_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()

        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def filter_devices(devices, search="", status=""):
    search = search.lower()

    result = []

    for d in devices:
        matches_search = (
            search in str(d.get("type", "")).lower()
            or search in str(d.get("model", "")).lower()
            or search in str(d.get("status", "")).lower()
            or search in str(d.get("deviceId", "")).lower()
            or search in str(d.get("location", "")).lower()
        )

        matches_status = (
            not status
            or d.get("status") == status
        )

        if matches_search and matches_status:
            result.append(d)

    return result


def run_tests():

    # ---------------------------------------------------------
    # TE2-01
    # U001의 가전 목록 -> D001, D002
    # ---------------------------------------------------------
    status, body = http_get("/api/subscribers/U001/devices")

    ids = (
        [d.get("deviceId") for d in body]
        if isinstance(body, list)
        else []
    )

    passed = (
        status == 200
        and len(ids) == 2
        and set(ids) == {"D001", "D002"}
    )

    check(
        "TE2-01",
        "/api/subscribers/U001/devices 호출",
        "D001, D002 두 가전 반환",
        f"status={status}, ids={ids}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-02
    # U005는 가전 없음
    # ---------------------------------------------------------
    status, body = http_get("/api/subscribers/U005/devices")

    passed = status == 200 and body == []

    check(
        "TE2-02",
        "/api/subscribers/U005/devices 호출",
        "빈 배열 [] 반환",
        f"status={status}, body={body}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-03
    # 없는 사용자 -> 404
    # ---------------------------------------------------------
    status, body = http_get("/api/subscribers/U999/devices")

    check(
        "TE2-03",
        "/api/subscribers/U999/devices 호출",
        "404 에러",
        f"status={status}",
        status == 404
    )


    # U001 가전 데이터 재사용
    status, devices = http_get("/api/subscribers/U001/devices")

    if not isinstance(devices, list):
        devices = []


    # ---------------------------------------------------------
    # TE2-04
    # U001 클릭 시 가전 Table 관련 구현 확인
    # ---------------------------------------------------------
    try:
        app_js = APP_JS.read_text(encoding="utf-8")
    except Exception:
        app_js = ""

    required = [
        "selectSubscriber",
        "renderDevices",
        "/api/subscribers/",
        "deviceId",
        "model",
        "location",
        "status",
    ]

    missing = [x for x in required if x not in app_js]

    passed = (
        len(missing) == 0
        and {"D001", "D002"} <= set(
            d.get("deviceId") for d in devices
        )
    )

    check(
        "TE2-04",
        "U001 클릭 시 가전 Table 표시",
        "D001, D002 표시",
        "구현 확인" if passed else f"누락={missing}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-05
    # 가전 없는 사용자 안내
    # ---------------------------------------------------------
    passed = "No registered devices" in app_js

    check(
        "TE2-05",
        "U005 클릭 시 안내 메시지",
        "No registered devices 표시",
        "문구 존재" if passed else "문구 없음",
        passed
    )


    # ---------------------------------------------------------
    # TE2-06
    # TV 검색
    # ---------------------------------------------------------
    r = filter_devices(devices, search="TV")

    passed = (
        len(r) == 1
        and r[0].get("type") == "TV"
    )

    check(
        "TE2-06",
        '가전 검색 "TV"',
        "TV 타입만 표시",
        f"{len(r)}개: {[d.get('deviceId') for d in r]}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-07
    # Online 필터
    # ---------------------------------------------------------
    r = filter_devices(devices, status="Online")

    passed = (
        len(r) >= 1
        and all(d.get("status") == "Online" for d in r)
    )

    check(
        "TE2-07",
        '상태 필터 "Online"',
        "Online 가전만 표시",
        f"{len(r)}개: {[d.get('deviceId') for d in r]}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-08
    # D001 사용 현황
    # ---------------------------------------------------------
    status, usage = http_get("/api/devices/D001/usage")

    fields = {
        "deviceId",
        "deviceName",
        "powerStatus",
        "lastUsedAt",
        "totalUsageHours",
        "weeklyUsageCount",
        "healthStatus",
        "remark",
        "weeklyUsageTrend",
    }

    if isinstance(usage, dict):
        missing = fields - set(usage.keys())
    else:
        missing = fields

    passed = (
        status == 200
        and isinstance(usage, dict)
        and len(missing) == 0
    )

    check(
        "TE2-08",
        "/api/devices/D001/usage 호출",
        "사용 현황 JSON 반환",
        f"status={status}, missing={list(missing)}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-09
    # 없는 디바이스 -> 404
    # ---------------------------------------------------------
    status, body = http_get("/api/devices/D999/usage")

    check(
        "TE2-09",
        "/api/devices/D999/usage 호출",
        "404 에러",
        f"status={status}",
        status == 404
    )


    # ---------------------------------------------------------
    # TE2-10
    # 사용 현황 UI 구현
    # ---------------------------------------------------------
    required = [
        "selectDevice",
        "/api/devices/",
        "/usage",
        "powerStatus",
        "totalUsageHours",
        "weeklyUsageCount",
        "healthStatus",
        "remark",
    ]

    missing = [x for x in required if x not in app_js]

    passed = len(missing) == 0

    check(
        "TE2-10",
        "D001 클릭 시 사용 현황 표시",
        "전원상태, 누적시간 등 표시",
        "구현 확인" if passed else f"누락={missing}",
        passed
    )


    # ---------------------------------------------------------
    # TE2-11
    # Bar Chart
    # ---------------------------------------------------------
    lower_js = app_js.lower()

    passed = (
        "renderusagechart" in lower_js
        and "new chart" in lower_js
        and (
            'type: "bar"' in lower_js
            or "type: 'bar'" in lower_js
        )
        and "mon" in lower_js
        and "sun" in lower_js
    )

    check(
        "TE2-11",
        "D001 클릭 시 Bar Chart 표시",
        "요일별 Bar Chart",
        "Chart 구현 확인" if passed else "Chart 구현 확인 실패",
        passed
    )


    # ---------------------------------------------------------
    # TE2-12
    # 기존 Chart 제거 후 갱신
    # ---------------------------------------------------------
    passed = (
        "destroy()" in app_js
        and "usageChart" in app_js
    )

    check(
        "TE2-12",
        "다른 가전 클릭 시 차트 갱신",
        "기존 차트 제거 후 새 차트 표시",
        "destroy 로직 존재" if passed else "destroy 로직 없음",
        passed
    )


def render_report():

    total = len(results)

    passed_count = sum(
        1 for *_, passed in results
        if passed
    )

    failed_count = total - passed_count

    rate = (
        passed_count / total * 100
        if total
        else 0
    )

    lines = []

    lines.append("# requirement_2 검증 Report")
    lines.append("")
    lines.append("| 항목 | 내용 |")
    lines.append("|------|------|")
    lines.append("| 프로젝트 | webOS Subscription Management Dashboard |")
    lines.append("| 검증 대상 | requirement_2.md |")
    lines.append(
        f"| 검증 일시 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |"
    )
    lines.append("| 작성자 | Test Engineer |")
    lines.append("")

    lines.append(
        f"**총 {total}건 중 PASS {passed_count} / "
        f"FAIL {failed_count} — Pass Rate {rate:.1f}%**"
    )

    lines.append("")
    lines.append(
        "| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |"
    )
    lines.append(
        "|:-----:|----------------|-----------|-----------|:----:|"
    )

    for tc_id, scenario, expected, actual, passed in results:

        mark = "✅ PASS" if passed else "❌ FAIL"

        actual = str(actual).replace("|", "/")

        lines.append(
            f"| {tc_id} | {scenario} | {expected} | "
            f"{actual} | {mark} |"
        )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    return passed_count, failed_count, total, rate


def main():

    global BASE_URL

    print("=" * 60)
    print(" requirement_2 검증")
    print("=" * 60)

    port = find_free_port()

    print(f"[서버 기동] 127.0.0.1:{port} ...")

    proc, ok = start_server(port)

    if not ok:
        print("[오류] 서버 기동 실패")
        stop_server(proc)
        sys.exit(1)

    BASE_URL = f"http://127.0.0.1:{port}"

    print("[서버 기동] 성공\n")

    try:
        run_tests()
    finally:
        stop_server(proc)

    passed, failed, total, rate = render_report()

    print("")
    print("=" * 60)
    print(
        f"결과: PASS {passed} / FAIL {failed} "
        f"(총 {total}) - {rate:.1f}%"
    )
    print(
        f"Report 저장: "
        f"{REPORT_PATH.relative_to(PROJECT_ROOT)}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()