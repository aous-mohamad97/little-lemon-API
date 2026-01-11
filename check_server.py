import urllib.request
import time
import sys

url = 'http://127.0.0.1:8000/api/'
max_attempts = 5
delay = 2

print("Checking if server is running...")
for i in range(max_attempts):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        print(f"[SUCCESS] Server is running!")
        print(f"Status Code: {response.getcode()}")
        print(f"URL: {url}")
        print("\nServer is ready to use!")
        sys.exit(0)
    except urllib.error.URLError as e:
        if i < max_attempts - 1:
            print(f"Attempt {i+1}/{max_attempts}: Server not ready yet, waiting {delay} seconds...")
            time.sleep(delay)
        else:
            print(f"[INFO] Server may still be starting. Please check manually.")
            print(f"Try accessing: {url}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
