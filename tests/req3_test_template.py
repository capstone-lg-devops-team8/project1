import os
import re
import sys
import json
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
REPORT_PATH = REPORT_DIR / "req3_report_template.md"

APP_JS = PROJECT_ROOT / "app" / "static" / "app.js"
STYLE_CSS = PROJECT_ROOT / "app" / "static" / "style.css"

CI_YML = (
    PROJECT_ROOT
    / ".github"
    / "workflows"
    / "ci.yml"
)

results = []


def check(
    tc_id,
    scenario,
    expected,
    actual,
    state
):
    results.append(
        (
            tc_id,
            scenario,
            expected,
            actual,
            state
        )
    )

    print(
        f"[{state}] {tc_id} {scenario}"
    )


def read_text(path):
    try:
        return path.read_text(
            encoding="utf-8"
        )
    except Exception:
        return ""


def function_body(js, name):

    pattern = (
        rf"function\s+{re.escape(name)}"
        rf"\s*\([^)]*\)\s*\{{"
    )

    m = re.search(pattern, js)

    if not m:
        return ""

    start = m.end()
    depth = 1
    i = start

    while i < len(js):

        if js[i] == "{":
            depth += 1

        elif js[i] == "}":
            depth -= 1

            if depth == 0:
                return js[start:i]

        i += 1

    return ""


def check_badge(
    body,
    css,
    value,
    css_class,
    scenario,
    expected,
    tc_id
):

    body_lower = body.lower()
    css_lower = css.lower()

    mapping_ok = (
        value.lower() in body_lower
        and css_class.lower() in body_lower
    )

    css_ok = (
        f".{css_class.lower()}"
        in css_lower
    )

    passed = (
        mapping_ok
        and css_ok
    )

    actual = (
        f"mapping={'OK' if mapping_ok else 'FAIL'}, "
        f"css={'OK' if css_ok else 'FAIL'}"
    )

    check(
        tc_id,
        scenario,
        expected,
        actual,
        "PASS" if passed else "FAIL"
    )


def http_get(url, timeout=30):

    try:

        with urllib.request.urlopen(
            url,
            timeout=timeout
        ) as resp:

            body = resp.read().decode(
                "utf-8",
                errors="replace"
            )

            try:
                body = json.loads(body)
            except Exception:
                pass

            return resp.status, body

    except Exception as e:
        return None, str(e)


def run_tests():

    app_js = read_text(APP_JS)
    css = read_text(STYLE_CSS)

    badge_body = function_body(
        app_js,
        "badgeClass"
    )


    # ----------------------------------------------------
    # Badge 테스트
    # ----------------------------------------------------

    check_badge(
        badge_body,
        css,
        "active",
        "status-active",
        "Active 상태 확인",
        "초록 badge",
        "TE3-01"
    )

    check_badge(
        badge_body,
        css,
        "paused",
        "status-paused",
        "Paused 상태 확인",
        "파랑 badge",
        "TE3-02"
    )

    check_badge(
        badge_body,
        css,
        "expired",
        "status-expired",
        "Expired 상태 확인",
        "빨강 badge",
        "TE3-03"
    )

    check_badge(
        badge_body,
        css,
        "online",
        "status-active",
        "Online 상태 확인",
        "초록 badge",
        "TE3-04"
    )

    check_badge(
        badge_body,
        css,
        "offline",
        "status-offline",
        "Offline 상태 확인",
        "회색 badge",
        "TE3-05"
    )

    check_badge(
        badge_body,
        css,
        "error",
        "status-expired",
        "Error 상태 확인",
        "빨강 badge",
        "TE3-06"
    )

    check_badge(
        badge_body,
        css,
        "on",
        "status-on",
        "Power On 상태 확인",
        "노랑 badge",
        "TE3-07"
    )

    check_badge(
        badge_body,
        css,
        "normal",
        "status-active",
        "Health Normal 상태 확인",
        "초록 badge",
        "TE3-08"
    )

    check_badge(
        badge_body,
        css,
        "warning",
        "status-expired",
        "Health Warning 상태 확인",
        "빨강 badge",
        "TE3-09"
    )


    # ----------------------------------------------------
    # CI 테스트
    # ----------------------------------------------------

    ci = read_text(CI_YML)
    ci_lower = ci.lower()


    # TE3-10
    passed = (
        CI_YML.exists()
        and "push:" in ci_lower
        and "branches:" in ci_lower
        and "main" in ci_lower
    )

    check(
        "TE3-10",
        "main push 시 CI 자동 실행 설정",
        "GitHub Actions 자동 실행",
        "ci.yml 설정 확인"
        if passed
        else "설정 누락",
        "PASS" if passed else "FAIL"
    )


    # TE3-11
    passed = (
        "uvicorn app.main:app" in ci_lower
        and "/health" in ci_lower
        and "curl" in ci_lower
    )

    check(
        "TE3-11",
        "CI health 체크",
        "/health 체크 통과",
        "health 검사 설정 확인"
        if passed
        else "health 검사 누락",
        "PASS" if passed else "FAIL"
    )


    # TE3-12
    endpoints = [
        "/api/subscribers",
        "/api/subscribers/u001/devices",
        "/api/devices/d001/usage",
    ]

    passed = all(
        endpoint in ci_lower
        for endpoint in endpoints
    )

    check(
        "TE3-12",
        "CI API 테스트",
        "3개 API 엔드포인트 검사",
        "API 검사 설정 확인"
        if passed
        else "API 검사 일부 누락",
        "PASS" if passed else "FAIL"
    )


    # ----------------------------------------------------
    # Render 배포 확인
    # ----------------------------------------------------

    render_url = os.environ.get(
        "RENDER_URL",
        ""
    ).strip()


    if not render_url:

        check(
            "TE3-13",
            "Render 배포 확인",
            "배포 URL 접속 가능",
            "RENDER_URL 미지정",
            "BLOCKED"
        )

    else:

        root_url = render_url.rstrip("/")
        health_url = (
            render_url.rstrip("/")
            + "/health"
        )

        root_status, root_body = http_get(
            root_url
        )

        health_status, health_body = http_get(
            health_url
        )

        health_ok = (
            isinstance(health_body, dict)
            and health_body.get("status")
            == "ok"
        )

        passed = (
            root_status == 200
            and health_status == 200
            and health_ok
        )

        check(
            "TE3-13",
            "Render 배포 확인",
            "대시보드 및 /health 접속 가능",
            (
                f"root={root_status}, "
                f"health={health_status}"
            ),
            "PASS" if passed else "FAIL"
        )


def render_report():

    total = len(results)

    passed = sum(
        1
        for *_, state in results
        if state == "PASS"
    )

    failed = sum(
        1
        for *_, state in results
        if state == "FAIL"
    )

    blocked = sum(
        1
        for *_, state in results
        if state == "BLOCKED"
    )

    lines = []

    lines.append(
        "# requirement_3 검증 Report"
    )

    lines.append("")

    lines.append(
        "| 항목 | 내용 |"
    )

    lines.append(
        "|------|------|"
    )

    lines.append(
        "| 프로젝트 | webOS Subscription Management Dashboard |"
    )

    lines.append(
        "| 검증 대상 | requirement_3.md |"
    )

    lines.append(
        f"| 검증 일시 | "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |"
    )

    lines.append(
        "| 작성자 | Test Engineer |"
    )

    lines.append("")

    lines.append(
        f"**총 {total}건 중 "
        f"PASS {passed} / "
        f"FAIL {failed} / "
        f"BLOCKED {blocked}**"
    )

    lines.append("")

    lines.append(
        "| TC ID | 테스트 시나리오 | 기대 결과 | 실제 결과 | 판정 |"
    )

    lines.append(
        "|:-----:|----------------|-----------|-----------|:----:|"
    )

    for (
        tc_id,
        scenario,
        expected,
        actual,
        state
    ) in results:

        if state == "PASS":
            mark = "✅ PASS"

        elif state == "FAIL":
            mark = "❌ FAIL"

        else:
            mark = "⏸ BLOCKED"

        actual = str(actual).replace(
            "|",
            "/"
        )

        lines.append(
            f"| {tc_id} | "
            f"{scenario} | "
            f"{expected} | "
            f"{actual} | "
            f"{mark} |"
        )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    return (
        passed,
        failed,
        blocked,
        total
    )


def main():

    print("=" * 60)
    print(" requirement_3 검증")
    print("=" * 60)

    run_tests()

    (
        passed,
        failed,
        blocked,
        total
    ) = render_report()

    print("")
    print("=" * 60)

    print(
        f"결과: "
        f"PASS {passed} / "
        f"FAIL {failed} / "
        f"BLOCKED {blocked} "
        f"(총 {total})"
    )

    print(
        f"Report 저장: "
        f"{REPORT_PATH.relative_to(PROJECT_ROOT)}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()