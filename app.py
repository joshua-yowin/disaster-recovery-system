"""
Automated Backup System - Complete Dashboard with Backup Functionality
"""
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import os
from datetime import datetime
import traceback


app = Flask(__name__)
CORS(app)


# Import backup system
try:
    from backup_system import BackupSystem
    BACKUP_AVAILABLE = True
except Exception as e:
    print(f"Warning: Backup system not available: {e}")
    BACKUP_AVAILABLE = False


# Enhanced HTML template with backup controls
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Automated Backup System</title>
    <style>
        body { font-family: Arial; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { background: white; padding: 30px; border-radius: 12px; max-width: 1000px; margin: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        h1 { color: #333; margin-top: 0; }
        h2 { color: #555; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .status { padding: 20px; background: #4CAF50; color: white; border-radius: 8px; margin: 20px 0; }
        .info { background: #2196F3; color: white; padding: 15px; margin: 10px 0; border-radius: 6px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }
        .stat-card h3 { margin: 0 0 10px 0; color: #666; font-size: 14px; }
        .stat-card .value { font-size: 28px; font-weight: bold; color: #333; }
        .backup-list { background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; max-height: 400px; overflow-y: auto; }
        .backup-item { background: white; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #4CAF50; }
        .backup-item .name { font-weight: bold; color: #333; }
        .backup-item .meta { color: #666; font-size: 13px; margin-top: 5px; }
        button { background: #667eea; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 5px; }
        button:hover { background: #5568d3; }
        button.danger { background: #f44336; }
        button.danger:hover { background: #da190b; }
        .loading { display: none; color: #667eea; font-style: italic; }
        .error { background: #f44336; color: white; padding: 15px; border-radius: 6px; margin: 10px 0; }
    </style>
    <script>
        function refreshStats() {
            document.getElementById('loading').style.display = 'block';
            fetch('/api/backup/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-backups').textContent = data.total_backups;
                    document.getElementById('total-size').textContent = data.total_size_mb + ' MB';
                    document.getElementById('loading').style.display = 'none';
                    loadBackups();
                })
                .catch(err => {
                    console.error(err);
                    document.getElementById('loading').style.display = 'none';
                });
        }
        
        function loadBackups() {
            fetch('/api/backup/list')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('backup-list');
                    if (data.backups && data.backups.length > 0) {
                        container.innerHTML = data.backups.map(b => `
                            <div class="backup-item">
                                <div class="name">📦 ${b.name}</div>
                                <div class="meta">
                                    Size: ${b.size_mb} MB | 
                                    Created: ${new Date(b.created).toLocaleString()}
                                </div>
                            </div>
                        `).join('');
                    } else {
                        container.innerHTML = '<p style="color: #999;">No backups found</p>';
                    }
                })
                .catch(err => console.error(err));
        }
        
        window.onload = function() {
            refreshStats();
            // Auto-refresh every 30 seconds
            setInterval(refreshStats, 30000);
        };
    </script>
</head>
<body>
    <div class="container">
        <h1>🚀 Automated Backup System</h1>
        
        <div class="status">
            <h2>✅ System Online</h2>
            <p>Complete automated backup and recovery system deployed on Azure</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
        </div>
        
        <h2>📊 Backup Statistics</h2>
        <div class="stats">
            <div class="stat-card">
                <h3>Total Backups</h3>
                <div class="value" id="total-backups">-</div>
            </div>
            <div class="stat-card">
                <h3>Storage Used</h3>
                <div class="value" id="total-size">-</div>
            </div>
            <div class="stat-card">
                <h3>Status</h3>
                <div class="value" style="font-size: 20px;">{{ status }}</div>
            </div>
        </div>
        
        <div class="info">
            <p><strong>Environment:</strong> {{ env }}</p>
            <p><strong>Storage Container:</strong> {{ container }}</p>
            <p><strong>Backup System:</strong> {{ backup_status }}</p>
        </div>
        
        <h2>📦 Recent Backups</h2>
        <div id="loading" class="loading">Loading backups...</div>
        <div id="backup-list" class="backup-list">
            <p style="color: #999;">Loading...</p>
        </div>
        
        <h2>🔧 Quick Actions</h2>
        <button onclick="refreshStats()">🔄 Refresh Stats</button>
        <button onclick="window.location.href='/api/backup/stats'">📊 View JSON Stats</button>
        <button onclick="window.location.href='/health'">❤️ Health Check</button>
        
        <h3 style="margin-top: 40px;">🎯 Features:</h3>
        <ul>
            <li>✅ Azure Blob Storage Integration</li>
            <li>✅ Automated Backup System</li>
            <li>✅ Real-time Statistics</li>
            <li>✅ Backup & Restore API</li>
            <li>✅ Terraform Infrastructure Management</li>
            <li>✅ CI/CD with GitHub Actions & Jenkins</li>
        </ul>
    </div>
</body>
</html>
"""


@app.route('/')
def home():
    """Main dashboard page"""
    backup_status = "✅ Operational" if BACKUP_AVAILABLE else "⚠️ Not Available"
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        env=os.getenv('AZURE_CONTAINER_NAME', 'Production'),
        container=os.getenv('AZURE_CONTAINER_NAME', 'backups'),
        status="Operational",
        backup_status=backup_status
    )


@app.route('/health')
def health():
    """Health check endpoint"""
    health_data = {
        'status': 'healthy',
        'service': 'automated-backup-system',
        'timestamp': datetime.now().isoformat(),
        'azure_storage': 'connected' if os.getenv('AZURE_STORAGE_CONNECTION_STRING') else 'not configured',
        'backup_system': 'operational' if BACKUP_AVAILABLE else 'unavailable'
    }
    return jsonify(health_data)


@app.route('/api/status')
def status():
    """API status endpoint"""
    return jsonify({
        'status': 'online',
        'version': '2.0.0',
        'environment': os.getenv('AZURE_CONTAINER_NAME', 'production'),
        'features': [
            'Backup Management',
            'Restore Functionality',
            'Azure Storage',
            'Terraform IaC',
            'CI/CD Pipeline',
            'Real-time Monitoring'
        ],
        'backup_system_available': BACKUP_AVAILABLE
    })


# Backup API Endpoints
@app.route('/api/backup/list')
def list_backups():
    """List all available backups"""
    if not BACKUP_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Backup system not available'}), 503
    
    try:
        backup = BackupSystem()
        backups = backup.list_backups()
        return jsonify({
            'status': 'success',
            'count': len(backups),
            'backups': backups
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/backup/stats')
def backup_stats():
    """Get backup system statistics"""
    if not BACKUP_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Backup system not available'}), 503
    
    try:
        backup = BackupSystem()
        stats = backup.get_storage_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/backup/test', methods=['POST'])
def test_backup():
    """Create a test backup"""
    if not BACKUP_AVAILABLE:
        return jsonify({'status': 'error', 'message': 'Backup system not available'}), 503
    
    try:
        # Create a test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(f"Test backup created at {datetime.now().isoformat()}\n")
            f.write("This is a test backup to verify the system is working.\n")
            test_file = f.name
        
        # Backup the test file
        backup = BackupSystem()
        result = backup.backup_file(test_file, f"test_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        # Clean up
        os.unlink(test_file)
        
        return jsonify({
            'status': 'success',
            'message': 'Test backup created successfully',
            'backup_info': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
