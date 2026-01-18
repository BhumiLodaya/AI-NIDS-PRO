"""
Flask API Server for AI-Powered Network Intrusion Detection System (NIDS)
Provides a hybrid approach: URL input → Mock network flow features → ML prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import joblib
import numpy as np
import socket
import re
import sklearn
from urllib.parse import urlparse
import csv
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to store loaded models
model = None
scaler = None
feature_names = []


def load_models():
    """Load the trained model, scaler, and feature columns"""
    global model, scaler, feature_names
    
    try:
        print(f"Current scikit-learn version: {sklearn.__version__}")
        
        # Try joblib first (recommended for scikit-learn models)
        try:
            model = joblib.load('models/model.pkl')
            print("✓ Model loaded successfully (joblib)")
        except Exception as e1:
            # Fallback to pickle
            try:
                with open('models/model.pkl', 'rb') as f:
                    model = pickle.load(f)
                print("✓ Model loaded successfully (pickle)")
            except Exception as e2:
                raise Exception(f"Failed to load model with both methods. Joblib: {e1}, Pickle: {e2}")
        
        # Try joblib first for scaler
        try:
            scaler = joblib.load('models/scaler.pkl')
            print("✓ Scaler loaded successfully (joblib)")
        except Exception as e1:
            # Fallback to pickle
            try:
                with open('models/scaler.pkl', 'rb') as f:
                    scaler = pickle.load(f)
                print("✓ Scaler loaded successfully (pickle)")
            except Exception as e2:
                raise Exception(f"Failed to load scaler with both methods. Joblib: {e1}, Pickle: {e2}")
        
        # Load feature column names
        with open('data/processed/feature_columns.txt', 'r') as f:
            feature_names = [line.strip() for line in f if line.strip()]
        print(f"✓ Loaded {len(feature_names)} feature columns")
        
        return True
    except Exception as e:
        print(f"\n✗ Error loading models: {e}")
        print(f"\n⚠️  VERSION MISMATCH DETECTED!")
        print(f"   Your models were likely trained with a different scikit-learn version.")
        print(f"   Current version: {sklearn.__version__}")
        print(f"\n💡 Solution: Upgrade scikit-learn to match the training version:")
        print(f"   Run: python -m pip install --upgrade scikit-learn>=1.7.0")
        print(f"   Or: .venv\\Scripts\\python.exe -m pip install --upgrade scikit-learn>=1.7.0")
        return False


def resolve_hostname(url):
    """
    Extract hostname from URL and resolve to IP address
    Returns: (hostname, ip_address) or (hostname, None) if resolution fails
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path.split('/')[0]
        
        # Remove port if present
        hostname = hostname.split(':')[0]
        
        # Try to resolve IP
        try:
            ip_address = socket.gethostbyname(hostname)
            return hostname, ip_address
        except socket.gaierror:
            return hostname, None
    except Exception as e:
        return url, None


def detect_attack_type(url):
    """
    Detect potential attack type from URL patterns
    Returns: (attack_type, risk_score)
    """
    url_lower = url.lower()
    
    # Attack pattern detection
    if any(keyword in url_lower for keyword in ['dos', 'ddos', 'flood', 'syn', 'udp']):
        return 'DDoS', 0.85
    
    elif any(keyword in url_lower for keyword in ['ssh', 'admin', 'login', 'brute', 'ftp']):
        return 'Brute Force', 0.80
    
    elif any(keyword in url_lower for keyword in ['bot', 'botnet', 'zombie', 'command']):
        return 'Bot', 0.75
    
    elif any(keyword in url_lower for keyword in ['infiltration', 'backdoor', 'rootkit', 'exploit']):
        return 'Infiltration', 0.90
    
    elif any(keyword in url_lower for keyword in ['scan', 'probe', 'reconnaissance', 'portscan']):
        return 'PortScan', 0.70
    
    elif any(keyword in url_lower for keyword in ['phish', 'malware', 'virus', 'trojan']):
        return 'Web Attack', 0.85
    
    else:
        # Check for generic suspicious indicators
        risk_score = 0.0
        
        if len(url) > 100:
            risk_score += 0.2
        
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.search(ip_pattern, url):
            risk_score += 0.25
        
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path.split('/')[0]
        if hostname.count('.') > 3:
            risk_score += 0.2
        
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz']
        if any(url_lower.endswith(tld) for tld in suspicious_tlds):
            risk_score += 0.3
        
        if '@' in url:
            risk_score += 0.25
        
        if url.count('-') > 4 or url.count('_') > 4:
            risk_score += 0.1
        
        if risk_score > 0.4:
            return 'Suspicious', min(risk_score, 1.0)
        else:
            return 'Benign', min(risk_score, 1.0)


def generate_mock_flow_features(url, hostname, ip_address, attack_type, risk_score):
    """
    Generate realistic network flow features based on attack profiles
    Maps to the exact feature names from feature_columns.txt
    
    Uses attack-specific profiles for realistic feature generation
    """
    features = {}
    url_lower = url.lower()
    
    # Define Attack Profiles with characteristic network patterns
    ATTACK_PROFILES = {
        'DDoS': {
            'duration_mult': 0.2,  # Short, rapid connections
            'fwd_pkts': np.random.randint(500, 2000),  # Very high packet count
            'bwd_pkts': np.random.randint(100, 500),
            'pkt_size': 64,  # Small packets for floods
            'flags': 0.9,  # High flag activity (SYN floods)
            'port': 80
        },
        'Brute Force': {
            'duration_mult': 0.5,
            'fwd_pkts': np.random.randint(50, 200),  # Multiple login attempts
            'bwd_pkts': np.random.randint(50, 200),
            'pkt_size': 200,
            'flags': 0.4,
            'port': 22  # SSH port
        },
        'Bot': {
            'duration_mult': 2.0,  # Longer connections
            'fwd_pkts': np.random.randint(100, 500),
            'bwd_pkts': np.random.randint(100, 500),
            'pkt_size': 400,
            'flags': 0.5,
            'port': 8080
        },
        'Infiltration': {
            'duration_mult': 5.0,  # Very long, stealthy
            'fwd_pkts': np.random.randint(20, 100),
            'bwd_pkts': np.random.randint(20, 100),
            'pkt_size': 300,
            'flags': 0.2,  # Low flags to avoid detection
            'port': 443
        },
        'PortScan': {
            'duration_mult': 0.1,  # Very fast
            'fwd_pkts': np.random.randint(1, 5),  # Few packets per port
            'bwd_pkts': np.random.randint(0, 2),
            'pkt_size': 40,  # Minimal packets
            'flags': 0.7,
            'port': np.random.randint(1, 65535)
        },
        'Web Attack': {
            'duration_mult': 1.0,
            'fwd_pkts': np.random.randint(30, 150),
            'bwd_pkts': np.random.randint(30, 150),
            'pkt_size': 500,  # Larger payload
            'flags': 0.3,
            'port': 443
        },
        'Benign': {
            'duration_mult': 1.5,
            'fwd_pkts': np.random.randint(10, 50),
            'bwd_pkts': np.random.randint(10, 50),
            'pkt_size': 250,
            'flags': 0.1,
            'port': 443 if 'https' in url_lower else 80
        }
    }
    
    # Select appropriate profile
    profile = ATTACK_PROFILES.get(attack_type, ATTACK_PROFILES['Benign'])
    
    # Determine if this should simulate malicious flow
    is_suspicious = attack_type not in ['Benign', 'Suspicious'] or risk_score > 0.4
    
    # Use profile parameters
    duration_multiplier = profile['duration_mult']
    flag_activity = profile['flags']
    
    # Port and Protocol
    features['Dst Port'] = profile['port']
    features['Protocol'] = 6  # TCP
    
    # Flow duration and packet counts
    base_duration = 5000000 * duration_multiplier  # microseconds
    features['Flow Duration'] = base_duration
    features['Tot Fwd Pkts'] = profile['fwd_pkts']
    features['Tot Bwd Pkts'] = profile['bwd_pkts']
    
    # Packet lengths from profile
    base_fwd_len = profile['pkt_size'] * np.random.uniform(0.9, 1.1)
    base_bwd_len = profile['pkt_size'] * np.random.uniform(0.8, 1.0)
    
    features['TotLen Fwd Pkts'] = base_fwd_len * features['Tot Fwd Pkts']
    features['TotLen Bwd Pkts'] = base_bwd_len * features['Tot Bwd Pkts']
    features['Fwd Pkt Len Max'] = base_fwd_len * 1.5
    features['Fwd Pkt Len Min'] = base_fwd_len * 0.5
    features['Fwd Pkt Len Mean'] = base_fwd_len
    features['Fwd Pkt Len Std'] = base_fwd_len * 0.3
    
    features['Bwd Pkt Len Max'] = base_bwd_len * 1.5
    features['Bwd Pkt Len Min'] = base_bwd_len * 0.5
    features['Bwd Pkt Len Mean'] = base_bwd_len
    features['Bwd Pkt Len Std'] = base_bwd_len * 0.3
    
    # Flow rates
    if base_duration > 0:
        total_bytes = features['TotLen Fwd Pkts'] + features['TotLen Bwd Pkts']
        total_pkts = features['Tot Fwd Pkts'] + features['Tot Bwd Pkts']
        features['Flow Byts/s'] = (total_bytes / base_duration) * 1000000
        features['Flow Pkts/s'] = (total_pkts / base_duration) * 1000000
    else:
        features['Flow Byts/s'] = 0
        features['Flow Pkts/s'] = 0
    
    # Inter-arrival times (IAT)
    base_iat = base_duration / max(total_pkts - 1, 1)
    features['Flow IAT Mean'] = base_iat
    features['Flow IAT Std'] = base_iat * 0.5
    features['Flow IAT Max'] = base_iat * 2
    features['Flow IAT Min'] = base_iat * 0.1
    
    features['Fwd IAT Tot'] = base_duration * 0.4
    features['Fwd IAT Mean'] = features['Fwd IAT Tot'] / max(features['Tot Fwd Pkts'] - 1, 1)
    features['Fwd IAT Std'] = features['Fwd IAT Mean'] * 0.5
    features['Fwd IAT Max'] = features['Fwd IAT Mean'] * 2
    features['Fwd IAT Min'] = features['Fwd IAT Mean'] * 0.1
    
    features['Bwd IAT Tot'] = base_duration * 0.6
    features['Bwd IAT Mean'] = features['Bwd IAT Tot'] / max(features['Tot Bwd Pkts'] - 1, 1)
    features['Bwd IAT Std'] = features['Bwd IAT Mean'] * 0.5
    features['Bwd IAT Max'] = features['Bwd IAT Mean'] * 2
    features['Bwd IAT Min'] = features['Bwd IAT Mean'] * 0.1
    
    # Flags (suspicious traffic has more unusual flag activity)
    features['Fwd PSH Flags'] = int(flag_activity * 3)
    features['Bwd PSH Flags'] = int(flag_activity * 2)
    features['Fwd URG Flags'] = int(flag_activity * 1)
    features['Bwd URG Flags'] = int(flag_activity * 1)
    
    features['FIN Flag Cnt'] = 1
    features['SYN Flag Cnt'] = 1
    features['RST Flag Cnt'] = int(flag_activity * 2)
    features['PSH Flag Cnt'] = int(flag_activity * 5)
    features['ACK Flag Cnt'] = int(total_pkts * 0.8)
    features['URG Flag Cnt'] = int(flag_activity * 2)
    features['CWE Flag Count'] = 0
    features['ECE Flag Cnt'] = 0
    
    # Header lengths
    features['Fwd Header Len'] = 40 * features['Tot Fwd Pkts']
    features['Bwd Header Len'] = 40 * features['Tot Bwd Pkts']
    
    # Packet rates
    if base_duration > 0:
        features['Fwd Pkts/s'] = (features['Tot Fwd Pkts'] / base_duration) * 1000000
        features['Bwd Pkts/s'] = (features['Tot Bwd Pkts'] / base_duration) * 1000000
    else:
        features['Fwd Pkts/s'] = 0
        features['Bwd Pkts/s'] = 0
    
    # Packet length statistics
    all_pkt_lens = ([base_fwd_len] * int(features['Tot Fwd Pkts']) + 
                    [base_bwd_len] * int(features['Tot Bwd Pkts']))
    features['Pkt Len Min'] = min(all_pkt_lens) if all_pkt_lens else 0
    features['Pkt Len Max'] = max(all_pkt_lens) if all_pkt_lens else 0
    features['Pkt Len Mean'] = np.mean(all_pkt_lens) if all_pkt_lens else 0
    features['Pkt Len Std'] = np.std(all_pkt_lens) if all_pkt_lens else 0
    features['Pkt Len Var'] = np.var(all_pkt_lens) if all_pkt_lens else 0
    
    # Ratios and averages
    features['Down/Up Ratio'] = (features['Tot Bwd Pkts'] / max(features['Tot Fwd Pkts'], 1))
    features['Pkt Size Avg'] = features['Pkt Len Mean']
    features['Fwd Seg Size Avg'] = features['Fwd Pkt Len Mean']
    features['Bwd Seg Size Avg'] = features['Bwd Pkt Len Mean']
    
    # Bulk rates (usually 0 for normal HTTP traffic)
    features['Fwd Byts/b Avg'] = 0
    features['Fwd Pkts/b Avg'] = 0
    features['Fwd Blk Rate Avg'] = 0
    features['Bwd Byts/b Avg'] = 0
    features['Bwd Pkts/b Avg'] = 0
    features['Bwd Blk Rate Avg'] = 0
    
    # Subflow features
    features['Subflow Fwd Pkts'] = features['Tot Fwd Pkts']
    features['Subflow Fwd Byts'] = features['TotLen Fwd Pkts']
    features['Subflow Bwd Pkts'] = features['Tot Bwd Pkts']
    features['Subflow Bwd Byts'] = features['TotLen Bwd Pkts']
    
    # Window sizes
    features['Init Fwd Win Byts'] = 65535 if not is_suspicious else np.random.randint(8000, 32000)
    features['Init Bwd Win Byts'] = 65535 if not is_suspicious else np.random.randint(8000, 32000)
    
    # Active data packets
    features['Fwd Act Data Pkts'] = int(features['Tot Fwd Pkts'] * 0.7)
    features['Fwd Seg Size Min'] = features['Fwd Pkt Len Min']
    
    # Active and Idle times
    base_active = 1000000  # 1 second in microseconds
    features['Active Mean'] = base_active * (0.5 if is_suspicious else 1.0)
    features['Active Std'] = features['Active Mean'] * 0.3
    features['Active Max'] = features['Active Mean'] * 1.5
    features['Active Min'] = features['Active Mean'] * 0.5
    
    base_idle = 500000  # 0.5 seconds
    features['Idle Mean'] = base_idle * (2.0 if is_suspicious else 1.0)
    features['Idle Std'] = features['Idle Mean'] * 0.4
    features['Idle Max'] = features['Idle Mean'] * 2
    features['Idle Min'] = features['Idle Mean'] * 0.2
    
    return features


def log_threat_detection(url, ip_address, predicted_label, confidence, risk_level):
    """
    Log every detection result to threat_logs.csv for security monitoring
    """
    try:
        log_file = 'threat_logs.csv'
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Timestamp', 'URL', 'Resolved_IP', 'Predicted_Label', 
                         'Confidence_%', 'Risk_Level']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write log entry
            writer.writerow({
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'URL': url,
                'Resolved_IP': ip_address if ip_address else 'N/A',
                'Predicted_Label': predicted_label,
                'Confidence_%': confidence,
                'Risk_Level': risk_level
            })
        
        print(f"📝 Logged: {predicted_label} | {url} | {confidence}% confidence")
        
    except Exception as e:
        print(f"⚠️  Logging error: {e}")


def calculate_risk_level(predicted_label, confidence):
    """
    Calculate risk level based on predicted label and confidence score
    - Benign traffic: Always 'Low' risk
    - Malicious traffic: Risk based on confidence (High if >70%, Medium if <=70%)
    Returns: 'Low', 'Medium', or 'High'
    """
    # Benign traffic is always low risk, regardless of confidence
    if predicted_label.lower() == 'benign':
        return 'Low'
    
    # For malicious traffic, use confidence to determine risk level
    if confidence > 70:
        return 'High'
    else:
        return 'Medium'


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Main API endpoint for URL analysis
    Accepts: { "url": "https://example.com" }
    Returns: { "verdict": "Benign/Malicious", "confidence": 0.95, "mock_flow_data": {...} }
    """
    try:
        # Get URL from request
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        
        # Step 1: Resolve hostname
        hostname, ip_address = resolve_hostname(url)
        
        # Step 2: Detect attack type from URL patterns
        attack_type, risk_score = detect_attack_type(url)
        
        # Step 3: Generate mock network flow features using attack profiles
        mock_features = generate_mock_flow_features(url, hostname, ip_address, attack_type, risk_score)
        
        # Step 4: Create feature vector in correct order
        feature_vector = []
        for feature_name in feature_names:
            if feature_name in mock_features:
                feature_vector.append(mock_features[feature_name])
            else:
                # Default value for missing features
                feature_vector.append(0)
        
        # Convert to numpy array and reshape
        X = np.array(feature_vector).reshape(1, -1)
        
        # Step 5: Scale the features with error handling
        try:
            X_scaled = scaler.transform(X)
        except ValueError as e:
            error_msg = f"Feature scaling failed - Shape mismatch: Expected {scaler.n_features_in_} features, got {X.shape[1]}"
            print(f"❌ {error_msg}")
            print(f"   Expected features: {scaler.n_features_in_}")
            print(f"   Received features: {X.shape[1]}")
            return jsonify({'error': error_msg}), 500
        
        # Step 6: Get prediction with error handling
        try:
            prediction = model.predict(X_scaled)[0]
            probabilities = model.predict_proba(X_scaled)[0]
        except Exception as e:
            error_msg = f"Model prediction failed: {str(e)}"
            print(f"❌ {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        # Get confidence (probability of predicted class)
        confidence = float(max(probabilities))
        
        # Determine detailed verdict with actual class labels
        # Convert prediction to string to get actual attack class name
        predicted_label = str(prediction)
        
        # Map numeric predictions to known attack types if model uses numeric encoding
        # If your model returns class names directly, use them; otherwise use attack_type
        if predicted_label.isdigit():
            # Numeric prediction - use detected attack type from URL analysis
            if int(predicted_label) == 0:
                predicted_label = 'Benign'
            else:
                # Use the attack type detected from URL patterns
                predicted_label = attack_type if attack_type != 'Benign' else 'Malicious'
        
        verdict = predicted_label
        
        # Calculate risk level and confidence percentage
        confidence_pct = round(confidence * 100, 2)
        risk_level = calculate_risk_level(predicted_label, confidence_pct)
        
        # Log the detection for security monitoring
        log_threat_detection(url, ip_address, predicted_label, confidence_pct, risk_level)
        
        # Prepare enhanced response
        response = {
            'verdict': verdict,
            'predicted_label': predicted_label,
            'confidence': confidence_pct,
            'risk_level': risk_level,
            'attack_type_detected': attack_type,
            'mock_flow_data': {
                'url': url,
                'hostname': hostname,
                'ip_address': ip_address,
                'risk_score': round(risk_score, 3),
                'key_features': {
                    'Dst Port': mock_features.get('Dst Port'),
                    'Protocol': mock_features.get('Protocol'),
                    'Flow Duration': round(mock_features.get('Flow Duration', 0), 2),
                    'Tot Fwd Pkts': mock_features.get('Tot Fwd Pkts'),
                    'Tot Bwd Pkts': mock_features.get('Tot Bwd Pkts'),
                    'Flow Byts/s': round(mock_features.get('Flow Byts/s', 0), 2),
                    'Flow Pkts/s': round(mock_features.get('Flow Pkts/s', 0), 2),
                }
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'features_loaded': len(feature_names) > 0
    }
    return jsonify(status), 200


if __name__ == '__main__':
    print("=" * 60)
    print("AI-Powered NIDS Flask Server")
    print("=" * 60)
    
    # Load models on startup
    if load_models():
        print("\n🚀 Starting Flask server on http://localhost:5000")
        print("📡 API Endpoint: POST http://localhost:5000/analyze")
        print("💚 Health Check: GET http://localhost:5000/health")
        print("=" * 60)
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
    else:
        print("\n❌ Failed to load models. Server not started.")
        print("Please ensure model.pkl, scaler.pkl, and feature_columns.txt exist.")
