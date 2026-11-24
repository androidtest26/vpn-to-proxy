import os, sys, time, requests

TG = os.environ["TG_BOT_TOKEN"]
CHAT = int(os.environ["TG_CHAT_ID"])  # shudhu ei chat theke command nibe
API = f"https://api.telegram.org/bot{TG}"


def send(text):
    requests.post(f"{API}/sendMessage", data={"chat_id": CHAT, "text": text})


def get_updates(offset, timeout=30):
    try:
        r = requests.get(f"{API}/getUpdates",
                         params={"offset": offset, "timeout": timeout},
                         timeout=timeout + 10)
        return r.json().get("result", [])
    except Exception:
        time.sleep(3)
        return []


def flush():
    """Purono message ignore korar jonno."""
    res = get_updates(-1, timeout=0)
    return res[-1]["update_id"] + 1 if res else 0


def wait_file(max_wait=600):
    offset = flush()
    send("Bot chalu hoyeche. Ekta .ovpn file pathan (10 minute somoy ache).")
    deadline = time.time() + max_wait
    while time.time() < deadline:
        for u in get_updates(offset):
            offset = u["update_id"] + 1
            m = u.get("message") or {}
            if m.get("chat", {}).get("id") != CHAT:
                continue
            doc = m.get("document")
            if not doc:
                continue
            if not doc.get("file_name", "").lower().endswith(".ovpn"):
                send("Shudhu .ovpn file dite hobe.")
                continue
            fp = requests.get(f"{API}/getFile",
                              params={"file_id": doc["file_id"]}).json()["result"]["file_path"]
            data = requests.get(f"https://api.telegram.org/file/bot{TG}/{fp}").content
            with open("/tmp/client.ovpn", "wb") as f:
                f.write(data)
            send("File peyechi. VPN connect korchi...")
            return
    send("10 minute e file ashe ni. Action bondho hocche.")
    sys.exit(1)


def wait_stop(seconds):
    offset = flush()
    deadline = time.time() + seconds
    while time.time() < deadline:
        for u in get_updates(offset):
            offset = u["update_id"] + 1
            m = u.get("message") or {}
            if m.get("chat", {}).get("id") == CHAT and m.get("text", "").strip() == "/stop":
                return


if __name__ == "__main__":
    if sys.argv[1] == "wait_file":
        wait_file()
    elif sys.argv[1] == "wait_stop":
        wait_stop(int(sys.argv[2]))
