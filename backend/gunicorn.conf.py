"""
Gunicorn configuration for production deployment.
Optimized for streaming/SSE support on Google Cloud Platform.
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2))
worker_class = "uvicorn.workers.UvicornWorker"  # Required for async FastAPI
worker_connections = 1000

# Timeout settings - increased for long-running streaming
timeout = 3600  # 1 hour timeout for long streaming operations
keepalive = 75  # TCP keepalive
graceful_timeout = 120

# Disable buffering for streaming
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance
sendfile = False  # Disable sendfile to prevent buffering issues

# Request settings
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "mazda-backend"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# StatsD (optional monitoring)
statsd_host = None
statsd_prefix = None

# Prevent worker timeout during streaming
timeout_graceful_shutdown = 5

def when_ready(server):
    """Called just after the master process is initialized."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"Forking worker {worker}")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
