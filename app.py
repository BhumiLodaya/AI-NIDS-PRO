"""
AI Threat Scanner Web Application
Flask backend for URL threat analysis using machine learning
"""

from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Load the trained model
MODEL_PATH = 'models/model.pkl'
SCALER_PATH = 'models/scaler.pkl'

model = None
scaler = None

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    print("✅ Model and scaler loaded successfully!")
except Exception as e:
    print(f"⚠️ Warning: Could not load model: {e}")


def extract_url_features(url):
    """
    Extract security-relevant features from a URL
    This is a placeholder - you can extend this based on your model's requirements
    """
    parsed = urlparse(url)
    
    features = {
        'url_length': len(url),
        'domain_length': len(parsed.netloc),
        'path_length': len(parsed.path),
        'has_ip': 1 if re.match(r'\d+\.\d+\.\d+\.\d+', parsed.netloc) else 0,
        'has_at_symbol': 1 if '@' in url else 0,
        'has_double_slash': 1 if '//' in parsed.path else 0,
        'num_dots': url.count('.'),
        'num_hyphens': url.count('-'),
        'num_underscores': url.count('_'),
        'num_slashes': url.count('/'),
        'num_question_marks': url.count('?'),
        'num_equals': url.count('='),
        'num_ampersands': url.count('&'),
        'has_https': 1 if parsed.scheme == 'https' else 0,
        'suspicious_tld': 1 if parsed.netloc.endswith(('.tk', '.ml', '.ga', '.cf', '.gq')) else 0,
    }
    
    return features


def analyze_url_threat(url):
    """
    Analyze URL for potential security threats
    Returns threat level, confidence, and details
    """
    try:
        # Basic validation
        if not url or len(url) < 10:
            return {
                'status': 'error',
                'message': 'Please enter a valid URL'
            }
        
        # Extract features
        features = extract_url_features(url)
        
        # Heuristic analysis (since our model is trained on network traffic, not URLs)
        threat_score = 0
        threat_indicators = []
        
        # Check for suspicious patterns
        if features['has_ip']:
            threat_score += 30
            threat_indicators.append('Uses IP address instead of domain name')
        
        if features['url_length'] > 100:
            threat_score += 20
            threat_indicators.append('Unusually long URL')
        
        if features['has_at_symbol']:
            threat_score += 25
            threat_indicators.append('Contains @ symbol (possible obfuscation)')
        
        if features['num_dots'] > 5:
            threat_score += 15
            threat_indicators.append('Excessive subdomains')
        
        if features['suspicious_tld']:
            threat_score += 35
            threat_indicators.append('Uses suspicious TLD')
        
        if not features['has_https']:
            threat_score += 10
            threat_indicators.append('Not using HTTPS')
        
        if features['num_hyphens'] > 3:
            threat_score += 15
            threat_indicators.append('Multiple hyphens in domain')
        
        # Determine threat level
        if threat_score >= 60:
            threat_level = 'HIGH'
            threat_class = 'Attack'
            color = '#ef4444'
        elif threat_score >= 30:
            threat_level = 'MEDIUM'
            threat_class = 'Suspicious'
            color = '#f59e0b'
        else:
            threat_level = 'LOW'
            threat_class = 'Normal'
            color = '#10b981'
        
        confidence = min(threat_score + 20, 95)
        
        return {
            'status': 'success',
            'url': url,
            'threat_level': threat_level,
            'threat_class': threat_class,
            'confidence': confidence,
            'threat_score': threat_score,
            'indicators': threat_indicators,
            'color': color,
            'features': features,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Analysis failed: {str(e)}'
        }


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint for URL analysis"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'status': 'error',
                'message': 'No URL provided'
            }), 400
        
        # Perform analysis
        result = analyze_url_threat(url)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️  AI THREAT SCANNER - Web Application")
    print("="*60)
    print("\n🚀 Starting Flask server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
