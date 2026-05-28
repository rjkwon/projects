#!/usr/bin/env python3
"""
Simple local Web Server to edit links in data/fun.json.
Runs on http://localhost:8080 by default.
"""

import http.server
import json
import os
import sys
import webbrowser
from pathlib import Path

PORT = 8080
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FILE = PROJECT_ROOT / "data" / "fun.json"
ADMIN_HTML_FILE = PROJECT_ROOT / "static" / "admin.html"

class LinksEditorHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/admin.html":
            # Serve the editor UI
            if not ADMIN_HTML_FILE.exists():
                self.send_error(404, "admin.html not found. Make sure static/admin.html exists.")
                return
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(ADMIN_HTML_FILE, "rb") as f:
                self.wfile.write(f.read())
                
        elif self.path == "/api/links":
            # Serve data/fun.json
            if not DATA_FILE.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"[]")
                return
                
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            with open(DATA_FILE, "rb") as f:
                self.wfile.write(f.read())
                
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/links":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                # Validate JSON structure
                links_data = json.loads(post_data.decode("utf-8"))
                if not isinstance(links_data, list):
                    raise ValueError("Data must be a list of link objects")
                
                # Ensure data directory exists
                DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to fun.json
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(links_data, f, indent=2, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Links saved successfully"}).encode("utf-8"))
                print(f"Successfully saved {len(links_data)} links to {DATA_FILE}")
                
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    # Suppress verbose log messages in console if desired, but printing server start is helpful
    def log_message(self, format, *args):
        # Only log request lines to stdout for debugging
        sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))

def main():
    print(f"Starting Links Editor Local Server...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Data file: {DATA_FILE}")
    print(f"Admin HTML: {ADMIN_HTML_FILE}")
    
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, LinksEditorHandler)
    
    url = f"http://localhost:{PORT}/"
    print(f"\n==========================================")
    print(f"Server is running at: {url}")
    print(f"Press Ctrl+C to stop.")
    print(f"==========================================\n")
    
    # Auto-open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass
        
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server. Goodbye!")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
