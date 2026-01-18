"""
Quick test script to verify the Flask server is working correctly
Run this AFTER starting the Flask server (python server.py)
"""

import requests
import json

# Server URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_analyze_benign():
    """Test analyzing a benign URL"""
    print("\n" + "="*60)
    print("TEST 2: Analyze Benign URL")
    print("="*60)
    
    try:
        url = "https://google.com"
        print(f"Analyzing: {url}")
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"\nVerdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"\nMock Flow Data:")
        print(f"  Hostname: {result['mock_flow_data']['hostname']}")
        print(f"  IP Address: {result['mock_flow_data']['ip_address']}")
        print(f"  Risk Score: {result['mock_flow_data']['risk_score']}")
        print(f"\nKey Features:")
        for key, value in result['mock_flow_data']['key_features'].items():
            print(f"  {key}: {value}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_analyze_suspicious():
    """Test analyzing a suspicious URL"""
    print("\n" + "="*60)
    print("TEST 3: Analyze Suspicious URL")
    print("="*60)
    
    try:
        url = "http://phishing-site-malware-hack.example.com/verify-account-login-now"
        print(f"Analyzing: {url}")
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"\nVerdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"\nMock Flow Data:")
        print(f"  Hostname: {result['mock_flow_data']['hostname']}")
        print(f"  IP Address: {result['mock_flow_data']['ip_address']}")
        print(f"  Risk Score: {result['mock_flow_data']['risk_score']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "🧪 Flask Server Test Suite".center(60, "="))
    print("Make sure the Flask server is running (python server.py)")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Benign URL Analysis", test_analyze_benign()))
    results.append(("Suspicious URL Analysis", test_analyze_suspicious()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Could not connect to Flask server")
        print("Please ensure the server is running: python server.py")
