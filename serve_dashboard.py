#!/usr/bin/env python3
"""
Simple HTTP server to view the dashboard locally.
This avoids CORS issues when loading data files.
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def serve_dashboard():
    """Start HTTP server and open dashboard in browser."""

    # Check if dashboard exists
    if not (DIRECTORY / "dashboard.html").exists():
        print("Error: dashboard.html not found!")
        return

    # Check if data exists
    data_file = DIRECTORY / "outputs" / "proposals_with_implementation.json"
    if not data_file.exists():
        print("Warning: proposals_with_implementation.json not found")
        print("Dashboard may have limited functionality")

    Handler = MyHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/dashboard.html"
        print(f"\n{'='*80}")
        print(f"🚀 Dashboard Server Running")
        print(f"{'='*80}")
        print(f"\n📊 Dashboard URL: {url}")
        print(f"\n   Open this URL in your browser to view the dashboard.")
        print(f"   The dashboard will auto-open in your default browser.")
        print(f"\n   Press Ctrl+C to stop the server")
        print(f"\n{'='*80}\n")

        # Open browser
        webbrowser.open(url)

        # Serve forever
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
            print("Dashboard closed")

if __name__ == "__main__":
    serve_dashboard()
