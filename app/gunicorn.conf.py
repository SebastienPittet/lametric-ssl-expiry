# to print the config
#print_config = True  

wsgi_app = "app:app"

bind = "0.0.0.0:5000" # or unix:PATH

# The number of worker processes for handling requests.
workers = 1

# The number of worker threads for handling requests
threads = 2

# The max number of requests a worker will process before restarting
max_requests = 2
