

# gunicorn_config.py

# Use the 'gthread' worker type for better concurrency support
worker_class = 'gthread'

# The number of worker processes
workers = 1

# The address and port to bind to
bind = '0.0.0.0:8443'  # Change to your desired host and port

# SSL configuration
certfile= "ca.crt"  # Path to your SSL private key
keyfile = "ca.key"  # Path to your SSL certificate

# Set the user and group under which the worker processes will run
# user = 'your_user'
# group = 'your_group'

# Enable debugging
debug = False

# Set the maximum number of requests a worker will process before restarting
max_requests = 1000

# Set the maximum number of requests a worker will process before gracefully exiting
max_requests_jitter = 50

# Set the timeout for worker processes to gracefully exit
timeout = 30

# Set the maximum number of concurrent connections that a worker will handle
worker_connections = 1000

# Logging configuration
accesslog = 'access.log'
errorlog = 'error.log'
loglevel = 'info'
