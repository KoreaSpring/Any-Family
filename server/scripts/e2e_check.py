"""端到端检查：对已启动的本地服务做 HTTP 验证（首页/接口/SSE）。

用法： uv run python scripts/e2e_check.py
"""

from __future__ import annotations

import json
import urllib.request

BASE = "http://127.0.0.1:8080"


def get(path: str) -> tuple[int, str]:
    with urllib.request.urlopen(BASE + path, timeout=5) as r:
        return r.status, r.read().decode("utf-8", "replace")


def post(path: str, body: dict) -> int:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status


def main() -> None:
    # 1) 首页 HTML
    code, html = get("/")
    assert code == 200 and "Any-Family" in html, "首页未正确托管"
    print(f"[OK ] GET /          -> {code}, 含标题, {len(html)} 字节")

    # 2) 关键接口
    for p in ("/pet", "/overview", "/devices", "/timeline", "/interpretations", "/health-alerts"):
        code, _ = get(p)
        assert code == 200, f"{p} -> {code}"
        print(f"[OK ] GET {p:<18}-> {code}")

    # 3) 手动指令
    for p, body in (("/speak", {"text": "Lucky 乖"}), ("/play", {"mode": "ball"}), ("/feed", {"portion": "small"})):
        code = post(p, body)
        assert code == 200, f"{p} -> {code}"
        print(f"[OK ] POST {p:<17}-> {code}")

    # 4) SSE 能连上并收到数据
    with urllib.request.urlopen(BASE + "/events", timeout=5) as r:
        first = r.readline().decode()
        assert "event: hello" in first or "data:" in first, "SSE 无数据"
        print(f"[OK ] GET /events (SSE)  -> {r.status}, 首帧: {first.strip()[:40]}")

    print("\n端到端全部通过：Web 控制台 + 接口 + 实时流都正常。")


if __name__ == "__main__":
    main()
