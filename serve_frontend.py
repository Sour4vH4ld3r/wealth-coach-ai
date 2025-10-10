#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend testing app.
"""
import http.server
import socketserver
import os

PORT = 3001
DIRECTORY = "frontend/public"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║  💰 Wealth Coach AI - Frontend Testing Interface               ║
║                                                                 ║
║  Server running at: http://localhost:{PORT}                      ║
║  API running at:    http://localhost:8000                       ║
║                                                                 ║
║  Press Ctrl+C to stop the server                               ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝
        """)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            httpd.shutdown()
