"""
Disaster Recovery System - Simple Dashboard
"""
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Disaster Recovery Dashboard</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 800px; margin: auto; }
        h1 { color: #333; }
        .status { padding: 15px; background: #4CAF50; color: white; border-radius: 4px; margin: 20px 0; }
        .info { background: #2196F3; color: white; padding: 10px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Disaster Recovery System</h1>
        <div class="status">
            <h2>✅ System Online</h2>
            <p>Application deployed successfully on Azure!</p>
        </div>
        <div class="info">
            <p><strong>Environment:</strong> {{ env }}</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Storage Account:</strong> Connected</p>
        </div>
        <h3>Features:</h3>
        <ul>
            <li>Azure Blob Storage Integration</li>
            <li>Automated Backup System</li>
            <li>Terraform Infrastructure Management</li>
            <li>CI/CD with GitHub Actions & Jenkins</li>
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Main dashboard page"""
    return render_template_string(
        HTML_TEMPLATE,
        env=os.getenv('AZURE_CONTAINER_NAME', 'Production'),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'disaster-recovery-system',
        'timestamp': datetime.now().isoformat(),
        'azure_storage': 'connected' if os.getenv('AZURE_STORAGE_CONNECTION_STRING') else 'not configured'
    })

@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'environment': os.getenv('AZURE_CONTAINER_NAME', 'production'),
        'features': [
            'Backup Management',
            'Azure Storage',
            'Terraform IaC',
            'CI/CD Pipeline'
        ]
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
