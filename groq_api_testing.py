try:
    import ujson as json  # type: ignore
except Exception:
    import json  # type: ignore

try:
    import requests  # type: ignore
except Exception:
    import urequests as requests  # type: ignore

try:
    import network  # type: ignore
except Exception:
    network = None

try:
    import usocket as socket  # type: ignore
except Exception:
    import socket  # type: ignore

try:
    import utime as time  # type: ignore
except Exception:
    import time  # type: ignore

try:
    import os  # type: ignore
except Exception:
    os = None

URL = "https://api.groq.com/openai/v1/responses"
HOST = "api.groq.com"
PORT = 443
MODEL = "openai/gpt-oss-20b"


def load_api_key():
    if os is None:
        return ""

    try:
        key = os.getenv("GROQ_API_KEY")
    except Exception:
        key = None

    if not key:
        try:
            key = getattr(os, "environ", {}).get("GROQ_API_KEY", "")
        except Exception:
            key = ""

    return str(key or "").strip()


def sleep_ms(ms):
    try:
        time.sleep_ms(ms)
    except Exception:
        time.sleep(ms / 1000)


def wait_for_wifi(timeout_ms=12000):
    if network is None:
        print("network module not available, skipping Wi-Fi check")
        return True

    try:
        wlan = network.WLAN(network.STA_IF)
        print("wifi active:", wlan.active())
        print("wifi connected:", wlan.isconnected())
        if hasattr(wlan, "ifconfig"):
            try:
                print("ifconfig:", wlan.ifconfig())
            except Exception:
                pass

        waited = 0
        while not wlan.isconnected() and waited < timeout_ms:
            sleep_ms(500)
            waited += 500

        print("wifi connected after wait:", wlan.isconnected())
        if hasattr(wlan, "ifconfig"):
            try:
                print("ifconfig:", wlan.ifconfig())
            except Exception:
                pass
        return wlan.isconnected()
    except Exception as err:
        print("wifi check failed:", err)
        return False


def resolve_host(retries=3):
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            addr = socket.getaddrinfo(HOST, PORT)[0][-1]
            print("dns ok:", addr)
            return addr
        except Exception as err:
            last_err = err
            print("dns failed attempt {}: {}".format(attempt, err))
            sleep_ms(1200)
    return last_err


def extract_output_text(body):
    output_text = body.get("output_text", "")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    parts = []
    for item in body.get("output", []):
        if not isinstance(item, dict):
            continue
        for block in item.get("content", []):
            if not isinstance(block, dict):
                continue
            if block.get("type") in ("output_text", "text"):
                parts.append(block.get("text", ""))
    return "".join(parts).strip()


def run_query(user_input):
    api_key = load_api_key()
    if api_key == "":
        print("set GROQ_API_KEY in the environment before running this script")
        return

    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "input": user_input,
    }

    response = None
    try:
        try:
            response = requests.post(
                URL,
                data=json.dumps(payload),
                headers=headers,
                timeout=30,
            )
        except TypeError:
            response = requests.post(
                URL,
                data=json.dumps(payload),
                headers=headers,
            )

        print("status:", getattr(response, "status_code", 0))

        try:
            body = response.json()
        except Exception:
            print("raw response:")
            print(getattr(response, "text", ""))
            return

        text = extract_output_text(body)
        if text:
            print(text)
        else:
            print(body)
    except Exception as err:
        print("request failed:", err)
    finally:
        try:
            if response is not None:
                response.close()
        except Exception:
            pass


def main():
    while True:
        if not wait_for_wifi():
            print("Wi-Fi is not connected")
            sleep_ms(2000)
            continue

        try:
            user_input = input("input: ")
        except (EOFError, KeyboardInterrupt):
            print("\nstopped")
            return

        user_input = str(user_input or "").strip()
        if not user_input:
            continue

        resolved = resolve_host()
        if not isinstance(resolved, tuple):
            print("request failed:", resolved)
            print("hint: -202 usually means DNS lookup failed before the HTTPS request started")
            continue

        run_query(user_input)
        print("")


main()
