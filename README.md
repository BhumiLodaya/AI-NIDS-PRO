# 🛡️ AI-NIDS PRO  
### Professional Hybrid Threat Analysis System

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)

**AI-NIDS PRO** is an enterprise-grade **AI-powered Network Intrusion Detection System (NIDS)** designed to bridge the gap between **high-level user activity (URLs)** and **low-level network behavior (flows)**.

The system leverages a **Random Forest classifier** trained on the **CSE-CIC-IDS2018 dataset**, achieving **99.8% detection accuracy**, and focuses on **behavioral threat analysis** to identify even **zero-day attacks**.

---

## 🚀 Overview

Traditional signature-based security systems often fail against **unknown or evolving threats**. AI-NIDS PRO overcomes this limitation by analyzing **behavioral network flow patterns** rather than relying solely on known signatures.

By examining **78 network flow features**—including packet timing, volume, protocol behavior, and flow duration—the system can detect malicious intent **even when the URL or IP address has never been seen before**.



---

## ✨ Key Features

- **🎨 Modern Security UI** High-fidelity React dashboard with glassmorphism, neon accents, and real-time scanline animations for a professional SOC look.

- **🔗 Hybrid Analysis Logic** Translates application-layer URLs into simulated transport-layer network flows for deep inspection.

- **🎓 Educational Intelligence Layer** Interactive tooltips explain complex NIDS metrics (e.g., *Dst Port*, *Flow Duration*, *Protocol Flags*) for junior analysts.

- **🧠 Context-Aware Risk Assessment** Intelligent scoring logic suppresses false positives—**benign traffic is always marked Low Risk**, regardless of confidence score.

- **🧬 Multi-Class Threat Detection** Identifies DDoS, Brute Force, Botnets, Infiltration, Port Scans, and Web Attacks.

- **📁 Forensic Audit Logging** Automatically logs all detections into `threat_logs.csv` with timestamps, IPs, labels, and confidence scores.

---

## 📊 Attack Taxonomy

| Class | Description | Network Signature |
| :--- | :--- | :--- |
| **DDoS** | Distributed Denial of Service | High packet volume, short duration, flooding patterns |
| **Brute Force** | Credential Cracking | Repetitive small packets targeting ports 22, 80, 443 |
| **Bot** | Botnet Activity | Persistent heartbeat connections, C2 ports |
| **Infiltration** | Backdoor / Exploits | Stealthy flows, low packet count, long duration |
| **PortScan** | Network Reconnaissance | Sequential or random port probing |
| **Web Attack** | Phishing / Malware | URL heuristics + anomalous download flows |
| **Benign** | Normal Traffic | Standard handshakes and data transfers |

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+**
- **Flask** (REST API)
- **Flask-CORS**
- **Socket Programming**

### Machine Learning
- **Random Forest Classifier**
- **Scikit-learn**
- **Pandas, NumPy**
- **Joblib**

### Frontend
- **React 18.x**
- **Tailwind CSS**
- **Lucide Icons**

### Dataset
- **CSE-CIC-IDS2018** (Canadian Institute for Cybersecurity)

---

## 📁 Project Structure

```text
AI_Threat_Analysis_NIDS/
├── server.py                 # Flask API & Hybrid ML Logic
├── threat_scanner_v4.html    # React + Tailwind Dashboard
├── requirements.txt          # Project dependencies
├── threat_logs.csv           # Auto-generated audit logs
├── models/
│   ├── model.pkl             # Trained Random Forest model
│   ├── scaler.pkl            # StandardScaler
│   └── feature_columns.txt   # 78 required features
├── src/
│   ├── data_preprocessing.py # Feature engineering
│   └── model_training.py     # Training pipeline
└── README.md                 # Project documentation

```

## ⚙️ How It Works — Hybrid Pipeline



1. **Ingestion (Layer 7)**: User submits a URL. The system extracts the hostname and resolves it to an IP address.
2. **Simulation (The Bridge)**: A **78-dimensional network flow vector** is generated to simulate packet-sniffer metadata.
3. **ML Inference (The Brain)**: The flow vector is normalized using `StandardScaler` and passed to the Random Forest model.
4. **Risk Evaluation**: 
   - **Benign predictions** → Low Risk
   - **Attacks** → Risk weighted by model confidence
5. **Exposition (The UI)**: Results are visualized with **Security Educator tooltips**, explaining packet-level behavior.

---

## 📦 Installation & Setup

### Prerequisites
* Python 3.8+
* pip or conda

# Clone the repository
git clone https://github.com/yourusername/AI_Threat_Analysis_NIDS.git
cd AI_Threat_Analysis_NIDS

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# Mac / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python server.py

# Launch dashboard
# Open threat_scanner_v4.html in your browser

## 📡 API Documentation
### POST /analyze
{
  "request": {
    "url": "http://target.com/dos-attack"
  },
  "response": {
    "verdict": "MALICIOUS",
    "label": "DDoS",
    "confidence": "0.9245",
    "risk_level": "High",
    "ip": "104.21.65.122",
    "flow_metrics": {
      "duration": "5,000,000 µs",
      "packets": "1,842",
      "protocol": "TCP (6)"
    }
  }
}

## ⚠️ Troubleshooting
** Backend Connection Failed: Ensure server.py is running. Look for ✅ Model loaded in terminal. Ensure port 5000 is not in use. **

** CORS Errors: Verify flask-cors is installed and initialized in the app. **

** Model Accuracy Issues: Confirm model.pkl and scaler.pkl exist in the models/ directory. **

## 🎯 Future Roadmap
[ ] Live Packet Sniffing (Scapy integration)

[ ] Real-time Threat Visualization

[ ] SIEM Integration (Splunk / ELK)

[ ] Dockerized Deployment

[ ] Cloud-Based Scaling

## 🤝 Acknowledgments
CSE-CIC-IDS2018 Dataset – Canadian Institute for Cybersecurity

Scikit-learn & Flask Communities

Cybersecurity Research Community

## 🛡️ AI-NIDS PRO | Built for the next generation of Cybersecurity Professionals


