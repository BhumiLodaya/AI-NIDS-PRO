"""
Advanced Test Script for Upgraded Flask NIDS Server
Tests attack detection, logging, and risk level classification
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_result(response_data):
    """Pretty print the API response"""
    verdict = response_data.get('verdict', 'Unknown')
    predicted_label = response_data.get('predicted_label', 'N/A')
    confidence = response_data.get('confidence', 0)
    risk_level = response_data.get('risk_level', 'Unknown')
    attack_type = response_data.get('attack_type_detected', 'Unknown')
    
    # Color based on risk level
    if risk_level == 'High':
        color = RED
    elif risk_level == 'Medium':
        color = YELLOW
    else:
        color = GREEN
    
    print(f"\n{color}Verdict: {verdict}{RESET}")
    print(f"Predicted Label: {predicted_label}")
    print(f"Attack Type Detected: {attack_type}")
    print(f"Confidence: {confidence}%")
    print(f"{color}Risk Level: {risk_level}{RESET}")
    
    if 'mock_flow_data' in response_data:
        flow_data = response_data['mock_flow_data']
        print(f"\nURL: {flow_data.get('url')}")
        print(f"Hostname: {flow_data.get('hostname')}")
        print(f"IP Address: {flow_data.get('ip_address')}")
        print(f"Risk Score: {flow_data.get('risk_score')}")
        
        if 'key_features' in flow_data:
            print(f"\nKey Network Features:")
            for key, value in flow_data['key_features'].items():
                print(f"  • {key}: {value}")

def test_attack_profiles():
    """Test different attack type URLs"""
    print_header("🎯 TESTING ATTACK PROFILE DETECTION")
    
    test_cases = [
        ("Benign URL", "https://google.com"),
        ("DDoS Attack", "http://target.com/ddos-attack-flood-syn"),
        ("Brute Force", "http://server.com/ssh-admin-brute-force-login"),
        ("Bot Activity", "http://command.com/bot-botnet-zombie-control"),
        ("Infiltration", "http://target.com/backdoor-infiltration-exploit"),
        ("Port Scan", "http://target.com/portscan-reconnaissance-probe"),
        ("Web Attack", "http://victim.com/phishing-malware-trojan"),
    ]
    
    for test_name, url in test_cases:
        print(f"\n{MAGENTA}{'─'*70}{RESET}")
        print(f"{MAGENTA}Test: {test_name}{RESET}")
        print(f"URL: {url}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"url": url},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print_result(response.json())
            else:
                print(f"{RED}❌ Error: {response.status_code} - {response.text}{RESET}")
        
        except Exception as e:
            print(f"{RED}❌ Error: {e}{RESET}")
        
        time.sleep(0.5)  # Small delay between requests

def test_risk_levels():
    """Test different URLs to trigger various risk levels"""
    print_header("⚠️  TESTING RISK LEVEL CLASSIFICATION")
    
    test_urls = [
        "https://wikipedia.org",  # Low risk
        "http://suspicious-long-domain-name-with-many-dashes-and-subdomains.example.com",  # Medium
        "http://192.168.1.1/phishing-malware-ddos-attack.tk",  # High
    ]
    
    for url in test_urls:
        print(f"\n{MAGENTA}Testing URL: {url}{RESET}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze",
                json={"url": url},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                risk = data.get('risk_level', 'Unknown')
                conf = data.get('confidence', 0)
                print(f"Risk Level: {risk} (Confidence: {conf}%)")
        
        except Exception as e:
            print(f"{RED}❌ Error: {e}{RESET}")
        
        time.sleep(0.5)

def test_error_handling():
    """Test error handling for invalid inputs"""
    print_header("🛡️  TESTING ERROR HANDLING")
    
    test_cases = [
        ("Empty URL", ""),
        ("Invalid JSON", None),
        ("No URL field", {"invalid": "test"}),
    ]
    
    for test_name, test_data in test_cases:
        print(f"\n{MAGENTA}Test: {test_name}{RESET}")
        
        try:
            if test_data is None:
                response = requests.post(
                    f"{BASE_URL}/analyze",
                    data="invalid json",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            else:
                response = requests.post(
                    f"{BASE_URL}/analyze",
                    json=test_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        
        except Exception as e:
            print(f"{RED}❌ Error: {e}{RESET}")
        
        time.sleep(0.5)

def check_log_file():
    """Check if threat_logs.csv was created"""
    print_header("📝 CHECKING SECURITY LOGS")
    
    import os
    log_file = 'threat_logs.csv'
    
    if os.path.exists(log_file):
        print(f"{GREEN}✓ Log file '{log_file}' exists{RESET}")
        
        # Read and display last few entries
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"\nTotal entries: {len(lines) - 1}")  # -1 for header
            
            if len(lines) > 1:
                print(f"\nLast 5 entries:")
                print(f"{BLUE}{lines[0].strip()}{RESET}")  # Header
                for line in lines[-5:]:
                    print(line.strip())
    else:
        print(f"{RED}✗ Log file '{log_file}' not found{RESET}")

def main():
    print(f"\n{GREEN}{'='*70}")
    print("🧪 ADVANCED FLASK NIDS SERVER TEST SUITE")
    print(f"{'='*70}{RESET}\n")
    
    # Check server health first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"{GREEN}✓ Server is running and healthy{RESET}")
        else:
            print(f"{RED}✗ Server health check failed{RESET}")
            return
    except Exception as e:
        print(f"{RED}✗ Cannot connect to server: {e}{RESET}")
        print(f"\nPlease ensure the server is running:")
        print(f"  python server.py")
        return
    
    # Run tests
    test_attack_profiles()
    test_risk_levels()
    test_error_handling()
    check_log_file()
    
    print(f"\n{GREEN}{'='*70}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*70}{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
