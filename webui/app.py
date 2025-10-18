#!/usr/bin/env python3
"""ObfuscateLLVM Web UI - Interactive visualization and configuration."""

from flask import Flask, render_template, request, jsonify, send_file
import json
import tempfile
import subprocess
from pathlib import Path
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Main dashboard."""
    return render_template('index.html')

@app.route('/api/profiles')
def get_profiles():
    """Get available obfuscation profiles."""
    profiles = {}
    profiles_dir = Path(__file__).parent.parent / "profiles"
    
    for profile_file in profiles_dir.glob("*.json"):
        with open(profile_file) as f:
            profile_data = json.load(f)
            profiles[profile_file.stem] = profile_data
    
    return jsonify(profiles)

@app.route('/api/obfuscate', methods=['POST'])
def obfuscate():
    """Run obfuscation with given parameters."""
    data = request.json
    
    # Validate input
    if 'source_code' not in data:
        return jsonify({'error': 'No source code provided'}), 400
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Write source to temp file
            source_file = tmp_path / "input.c"
            with open(source_file, 'w') as f:
                f.write(data['source_code'])
            
            # Build command
            output_file = tmp_path / "output"
            report_file = tmp_path / "report.json"
            
            cmd = [
                "python", str(Path(__file__).parent.parent / "src/cli/obfuscatellvm.py"),
                "--input", str(source_file),
                "--output", str(output_file),
                "--report", str(report_file)
            ]
            
            # Add optional parameters
            if data.get('profile'):
                cmd.extend(["--profile", data['profile']])
            if data.get('cycles'):
                cmd.extend(["--cycles", str(data['cycles'])])
            if data.get('seed'):
                cmd.extend(["--seed", str(data['seed'])])
            if data.get('polymorphic'):
                cmd.append("--polymorphic")
            
            # Run obfuscation
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            response = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            # Add report data if available
            if report_file.exists():
                with open(report_file) as f:
                    response['report'] = json.load(f)
            
            return jsonify(response)
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Obfuscation timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cfg-diff')
def cfg_diff():
    """Generate CFG diff visualization."""
    # Mock CFG data for demonstration
    cfg_data = {
        'original': {
            'nodes': [
                {'id': 'entry', 'label': 'Entry', 'x': 100, 'y': 50},
                {'id': 'bb1', 'label': 'Basic Block 1', 'x': 100, 'y': 150},
                {'id': 'bb2', 'label': 'Basic Block 2', 'x': 200, 'y': 250},
                {'id': 'exit', 'label': 'Exit', 'x': 150, 'y': 350}
            ],
            'edges': [
                {'from': 'entry', 'to': 'bb1'},
                {'from': 'bb1', 'to': 'bb2'},
                {'from': 'bb2', 'to': 'exit'}
            ]
        },
        'obfuscated': {
            'nodes': [
                {'id': 'entry', 'label': 'Entry', 'x': 100, 'y': 50},
                {'id': 'dispatch', 'label': 'Dispatcher', 'x': 100, 'y': 150},
                {'id': 'bb1_flat', 'label': 'Flattened BB1', 'x': 50, 'y': 250},
                {'id': 'bb2_flat', 'label': 'Flattened BB2', 'x': 150, 'y': 250},
                {'id': 'junk1', 'label': 'Junk Block', 'x': 250, 'y': 200},
                {'id': 'exit', 'label': 'Exit', 'x': 100, 'y': 350}
            ],
            'edges': [
                {'from': 'entry', 'to': 'dispatch'},
                {'from': 'dispatch', 'to': 'bb1_flat'},
                {'from': 'dispatch', 'to': 'bb2_flat'},
                {'from': 'bb1_flat', 'to': 'dispatch'},
                {'from': 'bb2_flat', 'to': 'dispatch'},
                {'from': 'dispatch', 'to': 'junk1'},
                {'from': 'junk1', 'to': 'dispatch'},
                {'from': 'dispatch', 'to': 'exit'}
            ]
        }
    }
    
    return jsonify(cfg_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)