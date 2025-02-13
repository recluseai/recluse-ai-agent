import redis

# Set up a basic Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

# Ping Redis to check the connection
if r.ping():
    print("Redis is connected!")
else:
    print("Failed to connect to Redis.")
