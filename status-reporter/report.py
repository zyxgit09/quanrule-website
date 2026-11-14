# SPDX-FileCopyrightText: 2026 QuanRule Contributors
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-
"""
全规则服务器 · 状态上报（零第三方依赖，只用 Python 标准库）

工作方式：
  1) 在本地读取真实在线人数（127.0.0.1:25565，稳定可靠）
  2) 直接 POST 到自己域名的反向代理 https://www.zyxfwq.online/sb/rest/v1/...
     该域名（SNI 不含被封关键词）在本机网络可达，由 Netlify 函数再转发到 Supabase。
  每 60 秒一次，pythonw 静默后台运行，开机自启。
"""
import socket, struct, json, time, urllib.request, urllib.error, re, os

MC_HOST = "127.0.0.1"
MC_PORT = 25565
INTERVAL = 60

# 自动从 ../config.js 读取中转地址与密钥，避免重复维护
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "..", "config.js")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    url = re.search(r'SUPABASE_URL\s*=\s*"([^"]+)"', text).group(1)
    key = re.search(r'SUPABASE_ANON_KEY\s*=\s*"([^"]+)"', text).group(1)
    return url, key


# ---------------- Minecraft SLP 协议（标准库实现） ----------------
def pack_varint(value):
    if value < 0:
        value += 1 << 32
    out = b""
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out += bytes([b | 0x80])
        else:
            out += bytes([b])
            break
    return out


def pack_string(s):
    data = s.encode("utf-8")
    return pack_varint(len(data)) + data


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise IOError("连接被关闭")
        buf += chunk
    return buf


def recv_varint(sock):
    num = 0
    shift = 0
    while True:
        b = recv_exact(sock, 1)[0]
        num |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
        if shift >= 35:
            raise IOError("Varint 太长")
    return num


def ping_server():
    sock = socket.create_connection((MC_HOST, MC_PORT), timeout=8)
    try:
        handshake = (b"\x00" + pack_varint(-1) + pack_string(MC_HOST)
                     + struct.pack(">H", MC_PORT) + pack_varint(1))
        sock.sendall(pack_varint(len(handshake)) + handshake)
        req = b"\x00"
        sock.sendall(pack_varint(len(req)) + req)
        recv_varint(sock)
        recv_varint(sock)
        str_len = recv_varint(sock)
        payload = recv_exact(sock, str_len).decode("utf-8")
        return json.loads(payload)
    finally:
        sock.close()


def read_status():
    try:
        s = ping_server()
        p = s.get("players", {})
        sample = p.get("sample") or []
        return {
            "id": 1,
            "online": True,
            "player_count": int(p.get("online", 0)),
            "max_players": int(p.get("max", 0)),
            "player_names": ",".join(x.get("name", "") for x in sample),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        }
    except Exception as e:
        return {
            "id": 1,
            "online": False,
            "player_count": 0,
            "max_players": 0,
            "player_names": "",
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
            "error": str(e),
        }


def upsert(base_url, key, row):
    url = base_url.rstrip("/") + "/rest/v1/server_status"
    data = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("apikey", key)
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=merge-duplicates")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status


def main():
    while True:
        try:
            base_url, key = load_config()
            row = read_status()
            code = upsert(base_url, key, row)
            print("[%s] 上报成功 HTTP %s 人数 %s/%s" % (
                time.strftime("%H:%M:%S"), code,
                row["player_count"], row["max_players"]))
        except Exception as e:
            print("[%s] 本次上报失败：%s" % (time.strftime("%H:%M:%S"), e))
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
