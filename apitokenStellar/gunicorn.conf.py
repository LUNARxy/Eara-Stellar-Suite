import logging
import logging.handlers

# --- Logging Configuration ---
# You can customize the log file path, size, and backup count here.
log_file = "./error.log"
access_log_file = "./access.log"
max_bytes = 1024 * 1024 * 1024  # 10 MB
backup_count = 5

def post_worker_init(worker):
    """
    Hook to configure logging specifically for each worker process.
    This ensures that each worker logs to the same file correctly.
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Set overall logging level

    # Remove any existing handlers to prevent duplicate logging
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure file handler for error logs
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        mode='a',
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    # Define a formatter for error logs, including timestamp
    error_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(process)d [%(name)s] %(filename)s:%(lineno)d %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    # If you want to capture stdout/stderr to the error log, you might need
    # to redirect them. Gunicorn's --capture-output handles this for its own logs,
    # but for application-specific prints, you'd usually configure your app's
    # logging to go through the root logger.

    worker.log.info(f"Worker {worker.pid} started with logging configured to {log_file}")


# --- Gunicorn Configuration ---

# Bind address and port
# Use 0.0.0.0 to listen on all available network interfaces
# Or 127.0.0.1 for local connections only
bind = "127.0.0.1:8002" # Replace 8000 with your desired port

# Number of worker processes
# A common recommendation is (2 * number_of_cores) + 1
workers = 8 # Adjust based on your server's CPU cores

# Worker class (for FastAPI/ASGI applications)
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout for graceful worker shutdown (seconds)
timeout = 30

# Maximum number of requests a worker will process before restarting
# This helps prevent memory leaks
max_requests = 1000
max_requests_jitter = 50 # Add some jitter to prevent all workers restarting at once

# Log files (Gunicorn will create these)
# Error log: Gunicorn's own errors and application's stderr/stdout if captured
# Access log: HTTP request details
errorlog = log_file # Points to the file configured by RotatingFileHandler
# accesslog = access_log_file
accesslog = "-"


# --- MODIFICACIÓN AQUÍ para el access_log_format ---
# Formato de log de acceso:
# %(h)s: host remoto
# %(l)s: ident (si está disponible, normalmente '-')
# %(u)s: usuario autenticado (si está disponible, normalmente '-')
# %(t)s: fecha y hora de la solicitud
# %(r)s: línea de solicitud (método, ruta, versión HTTP)
# %(s)s: código de estado de la respuesta
# %(b)s: tamaño del cuerpo de la respuesta en bytes
# %(f)s: Referer (URL de origen)
# %(a)s: User-Agent
# %(L)s: Tiempo de la solicitud en segundos (flotante)
# %(D)s: Tiempo de la solicitud en microsegundos (entero)
# %(p)s: ID del proceso del worker
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'


# Log levels
loglevel = "info" # Options: debug, info, warning, error, critical

# Capture stdout/stderr to the error log
# This is crucial for seeing application prints in your error.log
capture_output = True

# Inherit standard I/O (often used with --capture-output)
enable_stdio_inheritance = True

# Process name (optional, helps identify Gunicorn processes)
proc_name = "apitoken"

# Application module and variable name
# Replace 'main:app' with the actual path to your FastAPI app
# For example, if your app is in 'src/api.py' and the FastAPI instance is 'app', use 'src.api:app'
wsgi_app = "main:app"