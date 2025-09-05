import weaviate
import subprocess
from contextlib import contextmanager
import os
import time

@contextmanager
def suppress_subprocess_output():
    """
    Context manager that suppresses the standard output and error 
    of any subprocess.Popen calls within this context.
    """
    # Store the original Popen
    original_popen = subprocess.Popen

    def patched_popen(*args, **kwargs):
        # Redirect the stdout and stderr to subprocess.DEVNULL
        kwargs['stdout'] = subprocess.DEVNULL
        kwargs['stderr'] = subprocess.DEVNULL
        return original_popen(*args, **kwargs)

    try:
        # Apply the patch by replacing subprocess.Popen with patched_popen
        subprocess.Popen = patched_popen
        # Yield control back to the context
        yield
    finally:
        # Ensure that the original Popen method is restored
        subprocess.Popen = original_popen

def wait_for_weaviate(url="http://localhost:8080", timeout=60):
    """Wait for Weaviate to be ready"""
    import requests
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/v1/.well-known/ready", timeout=5)
            if response.status_code == 200:
                print("Weaviate is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        print("Waiting for Weaviate to start...")
        time.sleep(2)
    return False

# Try to connect to local Weaviate instance (Docker)
try:
    # Wait for Weaviate to be ready
    if wait_for_weaviate():
        client = weaviate.connect_to_local(
            host="localhost",
            port=8080,
            grpc_port=50051
        )
        print("Connected to Weaviate via Docker")
    else:
        raise Exception("Weaviate is not ready after waiting")
except Exception as e:
    print(f"Failed to connect to local Weaviate: {e}")
    print("Please ensure Weaviate is running via Docker. Run: docker-compose up -d")
    raise


