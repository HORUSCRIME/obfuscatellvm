#!/usr/bin/env python3
"""Simple test for web UI functionality."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from webui.app import app
    
    # Test Flask app creation
    print("[OK] Flask app created successfully")
    
    # Test routes
    with app.test_client() as client:
        # Test main page
        response = client.get('/')
        assert response.status_code == 200
        print("[OK] Main page loads")
        
        # Test profiles API
        response = client.get('/api/profiles')
        assert response.status_code == 200
        print("[OK] Profiles API works")
        
        # Test CFG diff API
        response = client.get('/api/cfg-diff')
        assert response.status_code == 200
        data = response.get_json()
        assert 'original' in data
        assert 'obfuscated' in data
        print("[OK] CFG diff API works")
        
        print("\nWeb UI test completed successfully!")
        print("To run the web UI: python webui/app.py")
        print("Then visit: http://localhost:5000")

except ImportError as e:
    print(f"Flask not available: {e}")
    print("Install with: pip install flask")
except Exception as e:
    print(f"Web UI test failed: {e}")
    sys.exit(1)