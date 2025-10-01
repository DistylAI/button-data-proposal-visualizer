#!/usr/bin/env python3
"""
Simple HTTP server to view the dashboard locally.
This avoids CORS issues when loading data files.
"""

import http.server
import socketserver
import webbrowser
import argparse
import socket
from pathlib import Path

DEFAULT_PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, format, *args):
        """Suppress logging for cleaner output (optional)."""
        pass  # Comment this line out if you want to see request logs

def find_available_port(start_port=DEFAULT_PORT, max_attempts=10):
    """
    Find an available port starting from start_port.

    Args:
        start_port: Port to start searching from
        max_attempts: Maximum number of ports to try

    Returns:
        Available port number, or None if none found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def serve_dashboard(port=None, no_browser=False):
    """
    Start HTTP server and open dashboard in browser.

    Args:
        port: Port to use (None = auto-find starting from DEFAULT_PORT)
        no_browser: If True, don't auto-open browser
    """

    # Check if dashboard exists
    if not (DIRECTORY / "dashboard.html").exists():
        print("❌ Error: dashboard.html not found!")
        print(f"   Expected location: {DIRECTORY / 'dashboard.html'}")
        return 1

    # Check if data exists
    data_file = DIRECTORY / "outputs" / "proposals_with_implementation.json"
    if not data_file.exists():
        print("⚠️  Warning: proposals_with_implementation.json not found")
        print("   Dashboard may have limited functionality")
        print()

    # Find available port
    if port is None:
        port = find_available_port(DEFAULT_PORT)
        if port is None:
            print(f"❌ Error: Could not find available port in range {DEFAULT_PORT}-{DEFAULT_PORT + 9}")
            print(f"   Try specifying a different port: python serve_dashboard.py --port 8080")
            return 1
        elif port != DEFAULT_PORT:
            print(f"ℹ️  Port {DEFAULT_PORT} in use, using port {port} instead")
    else:
        # Check if specified port is available
        if not find_available_port(port, 1):
            print(f"❌ Error: Port {port} is already in use")
            print(f"   Solutions:")
            print(f"   1. Kill the process using port {port}:")
            print(f"      lsof -ti:{port} | xargs kill -9")
            print(f"   2. Use a different port:")
            print(f"      python serve_dashboard.py --port 8080")
            print(f"   3. Let the script auto-find an available port:")
            print(f"      python serve_dashboard.py")
            return 1

    Handler = MyHTTPRequestHandler

    # Allow port reuse to avoid "Address already in use" on restart
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}/dashboard.html"
            print(f"\n{'='*80}")
            print(f"🚀 Dashboard Server Running")
            print(f"{'='*80}")
            print(f"\n📊 Dashboard URL: {url}")
            print(f"\n   Press Ctrl+C to stop the server")
            print(f"\n{'='*80}\n")

            # Open browser
            if not no_browser:
                webbrowser.open(url)

            # Serve forever
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\n✓ Server stopped")
                return 0

    except OSError as e:
        print(f"❌ Error starting server: {e}")
        return 1

    return 0

def main():
    parser = argparse.ArgumentParser(
        description='Serve the AI system analysis dashboard locally',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python serve_dashboard.py              # Auto-find available port (starting from 8000)
  python serve_dashboard.py --port 8080  # Use specific port
  python serve_dashboard.py --no-browser # Don't auto-open browser
        """
    )
    parser.add_argument('--port', type=int, default=None,
                      help=f'Port to use (default: auto-find starting from {DEFAULT_PORT})')
    parser.add_argument('--no-browser', action='store_true',
                      help='Don\'t automatically open browser')

    args = parser.parse_args()

    exit_code = serve_dashboard(port=args.port, no_browser=args.no_browser)
    exit(exit_code)

if __name__ == "__main__":
    main()
