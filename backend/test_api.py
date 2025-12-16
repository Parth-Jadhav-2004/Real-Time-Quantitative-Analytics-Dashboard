import requests
import time

time.sleep(3)  # Wait for server to be ready

try:
    # Test basic endpoint
    response = requests.get("http://127.0.0.1:8001/")
    print(f"Health check: {response.json()}")
    
    # Test symbols endpoint
    response = requests.get("http://127.0.0.1:8001/api/symbols")
    print(f"Symbols: {response.json()}")
    
    print("\n✅ API is working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
