#!/usr/bin/env python3
"""
Start both frontend and backend services with a reverse proxy for Cloud Run.
Serves everything on port 8000 as required by Cloud Run.
"""

import os
import sys
import subprocess
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import httpx
import asyncio
from urllib.parse import urlparse

# Configuration
BACKEND_PORT = 4000
FRONTEND_PORT = 3000
PROXY_PORT = int(os.getenv("PORT", "8000"))  # Cloud Run sets PORT env var

class ReverseProxyHandler(BaseHTTPRequestHandler):
    """Simple reverse proxy to route requests to frontend or backend."""
    
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def do_OPTIONS(self):
        self.proxy_request()
    
    def proxy_request(self):
        """Route requests based on path."""
        # API requests go to backend
        if self.path.startswith('/api/') or \
           self.path.startswith('/run') or \
           self.path.startswith('/healthz') or \
           self.path.startswith('/version'):
            target_url = f"http://localhost:{BACKEND_PORT}{self.path}"
        # Everything else goes to frontend
        else:
            target_url = f"http://localhost:{FRONTEND_PORT}{self.path}"
        
        try:
            # Read request body if present
            content_length = self.headers.get('Content-Length')
            body = None
            if content_length:
                body = self.rfile.read(int(content_length))
            
            # Forward request
            with httpx.Client(timeout=30) as client:
                # Copy headers
                headers = {}
                for key, value in self.headers.items():
                    if key.lower() not in ['host', 'connection']:
                        headers[key] = value
                
                # Make request
                response = client.request(
                    method=self.command,
                    url=target_url,
                    headers=headers,
                    content=body if body else None
                )
                
                # Send response
                self.send_response(response.status_code)
                
                # Copy response headers
                for key, value in response.headers.items():
                    if key.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(key, value)
                self.end_headers()
                
                # Send response body
                if response.content:
                    self.wfile.write(response.content)
                    
        except Exception as e:
            print(f"Proxy error: {e}")
            self.send_error(502, f"Bad Gateway: {str(e)}")
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        return

def start_backend():
    """Start the FastAPI backend."""
    print(f"Starting backend on port {BACKEND_PORT}...")
    env = os.environ.copy()
    env["PORT"] = str(BACKEND_PORT)
    subprocess.run([sys.executable, "run.py"], env=env)

def start_frontend():
    """Start the Next.js frontend."""
    print(f"Starting frontend on port {FRONTEND_PORT}...")
    os.chdir("frontend")
    subprocess.run(["npm", "start"])

def wait_for_service(port, name, timeout=60):
    """Wait for a service to be ready."""
    print(f"Waiting for {name} on port {port}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with httpx.Client() as client:
                response = client.get(f"http://localhost:{port}/")
                if response.status_code < 500:
                    print(f"{name} is ready!")
                    return True
        except:
            pass
        time.sleep(1)
    print(f"Timeout waiting for {name}")
    return False

def main():
    """Main entry point."""
    print("Starting Microlearning Content Generator...")
    
    # Start backend in thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Wait for services to be ready
    if not wait_for_service(BACKEND_PORT, "backend"):
        sys.exit(1)
    if not wait_for_service(FRONTEND_PORT, "frontend"):
        sys.exit(1)
    
    # Start reverse proxy
    print(f"Starting reverse proxy on port {PROXY_PORT}...")
    print(f"Application ready at http://localhost:{PROXY_PORT}")
    
    httpd = HTTPServer(('', PROXY_PORT), ReverseProxyHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()

if __name__ == "__main__":
    main()
