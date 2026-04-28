#!/usr/bin/env python3
"""
Telegram Bot — Bidirectional Claude Code bridge.
Polls Telegram for incoming messages and responds via Claude Code CLI.

Requires env vars: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
Run: python3 bot.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.parse
from pathlib import Path

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = str(os.environ.get("TELEGRAM_CHAT_ID", ""))
PROJECT_DIR = Path(__file__).parent.parent.parent
CLAUDE_BIN = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")

SYSTEM_PREFIX = (
    "You are a helpful assistant responding via Telegram. "
    "You have full permission to use all available MCP tools (memory, etc.) directly without asking for authorization. "
    "Just use the tools and respond naturally. Keep responses concise.\n\n"
    "User message: "
)


def tg(method: str, params: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode() if params else None
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read())


def send_segments(text: str) -> None:
    if len(text) > 4096:
        text = text[:4093] + "..."
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs) <= 1:
        tg("sendMessage", {"chat_id": CHAT_ID, "text": text})
        return
    for i, para in enumerate(paragraphs):
        tg("sendMessage", {"chat_id": CHAT_ID, "text": para})
        if i < len(paragraphs) - 1:
            time.sleep(0.6)


def typing_loop(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            tg("sendChatAction", {"chat_id": CHAT_ID, "action": "typing"})
        except Exception:
            pass
        stop_event.wait(4)


def run_claude(message: str) -> str:
    full_prompt = SYSTEM_PREFIX + message
    cmd = [
        CLAUDE_BIN,
        "-p", full_prompt,
        "--output-format", "text",
        "--permission-mode", "auto",
    ]

    env = {**os.environ}
    env.pop("CLAUDECODE", None)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_DIR),
            env=env,
        )
        return result.stdout.strip() or "（无回复）"
    except subprocess.TimeoutExpired:
        return "超时了，请重试。"
    except Exception as e:
        return f"错误：{e}"


def handle_message(text: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] Received: {text[:60]}")

    stop_typing = threading.Event()
    t = threading.Thread(target=typing_loop, args=(stop_typing,), daemon=True)
    t.start()

    response = run_claude(text)

    stop_typing.set()
    t.join(timeout=1)

    send_segments(response)
    print(f"[{ts}] Replied: {response[:60]}")


def main() -> None:
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        sys.exit(1)

    print("Telegram bot started")
    print(f"  Listening for messages from chat_id: {CHAT_ID}")
    print(f"  Claude: {CLAUDE_BIN}")
    print()

    offset = 0

    while True:
        try:
            result = tg("getUpdates", {
                "offset": offset,
                "timeout": 30,
                "allowed_updates": "message",
            })

            for update in result.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})

                if str(msg.get("chat", {}).get("id", "")) != CHAT_ID:
                    continue

                text = msg.get("text", "").strip()
                if not text:
                    continue

                threading.Thread(
                    target=handle_message, args=(text,), daemon=True
                ).start()

        except KeyboardInterrupt:
            print("\nBot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
