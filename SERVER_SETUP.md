# Flask Server Setup Guide

## Overview
This guide walks you through setting up and running the Flask API server for your AI-Powered Network Intrusion Detection System (NIDS).

## Prerequisites
- Python 3.8+ installed
- Trained models (`model.pkl` and `scaler.pkl`) in the `models/` directory
- Feature columns file (`feature_columns.txt`) in `data/processed/`

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (cross-origin support)
- scikit-learn (ML library)
- numpy (numerical computing)
- All other required packages

### 2. Verify Model Files
Ensure these files exist:
- `models/model.pkl` (Random Forest model)
- `models/scaler.pkl` (Feature scaler)
- `data/processed/feature_columns.txt` (76 feature names)

## Running the Server

### Start the Flask Server
```bash
python server.py
```

You should see output like:
```
============================================================
AI-Powered NIDS Flask Server
============================================================
✓ Model loaded successfully
✓ Scaler loaded successfully
✓ Loaded 76 feature columns

🚀 Starting Flask server on http://localhost:5000
📡 API Endpoint: POST http://localhost:5000/analyze
💚 Health Check: GET http://localhost:5000/health
============================================================
```

## Using the API

### 1. Health Check
Test if the server is running:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true,
  "features_loaded": true
}
```

### 2. Analyze a URL
Send a POST request to analyze a URL:

**Using curl:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://example.com\"}"
```

**Expected response:**
```json
{
  "verdict": "Benign",
  "confidence": 95.34,
  "mock_flow_data": {
    "url": "https://example.com",
    "hostname": "example.com",
    "ip_address": "93.184.216.34",
    "risk_score": 0.0,
    "key_features": {
      "Dst Port": 443,
      "Protocol": 6,
      "Flow Duration": 5234567.89,
      "Tot Fwd Pkts": 10,
      "Tot Bwd Pkts": 15,
      "Flow Byts/s": 1234.56,
      "Flow Pkts/s": 4.78
    }
  }
}
```

## Frontend Integration

### Open the HTML File
1. Keep the Flask server running in a terminal
2. Open `threat-scanner.html` in your web browser
3. Enter a URL and click "Analyze"

The frontend will now communicate with your Flask server instead of using simulated data.

### Testing Different URLs

**Normal URLs (likely Benign):**
- `https://google.com`
- `https://github.com`
- `https://stackoverflow.com`

**Suspicious URLs (likely Malicious):**
- URLs with "phish", "hack", "malware" keywords
- Very long URLs (>100 characters)
- URLs with IP addresses instead of domain names
- URLs with excessive subdomains

## How It Works

### Hybrid Approach
Since the ML model expects network flow features but users provide URLs, the server uses a hybrid approach:

1. **URL Analysis**: Extracts hostname and resolves IP address
2. **Risk Scoring**: Analyzes URL characteristics (length, keywords, patterns)
3. **Mock Flow Generation**: Creates realistic network flow features based on risk score
4. **Feature Mapping**: Maps generated values to the 76 features the model expects
5. **Scaling**: Applies the trained scaler to normalize features
6. **Prediction**: Uses the Random Forest model to classify as Benign/Malicious
7. **Response**: Returns verdict, confidence score, and mock flow data

### URL Risk Indicators
The system checks for:
- Suspicious keywords (phish, hack, malware, etc.)
- URL length (longer = more suspicious)
- IP addresses in URL
- Excessive subdomains
- Suspicious TLDs (.tk, .ml, .xyz, etc.)
- @ symbols (phishing technique)
- Excessive dashes or underscores

### Mock Flow Features
- **High-risk URLs**: Generate suspicious network patterns (high packet rates, unusual flags)
- **Low-risk URLs**: Generate normal baseline traffic patterns

## Troubleshooting

### Port Already in Use
If port 5000 is occupied, change it in `server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

Also update the frontend fetch URL in `threat-scanner.html`:
```javascript
const response = await fetch('http://localhost:5001/analyze', {
```

### CORS Errors
If you see CORS errors in browser console:
- Ensure `flask-cors` is installed: `pip install flask-cors`
- Verify CORS is enabled in `server.py`: `CORS(app)`

### Model Loading Errors
If models fail to load:
- Check file paths are correct
- Ensure model files are not corrupted
- Verify Python version compatibility (models trained on same Python version)

### Connection Refused
If frontend can't connect:
- Ensure Flask server is running
- Check firewall settings
- Verify URL in fetch matches server address

## Production Deployment

For production use, consider:
1. Use a production WSGI server (gunicorn, uWSGI)
2. Add authentication/API keys
3. Implement rate limiting
4. Add logging and monitoring
5. Use HTTPS
6. Configure proper CORS origins (instead of allowing all)

Example with gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze a URL for threats |
| `/health` | GET | Check server health status |

## Support
For issues or questions, refer to:
- Main README: `README.md`
- Project Summary: `PROJECT_SUMMARY.md`
