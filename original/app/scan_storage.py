import json
import os
from datetime import datetime

class ScanStorage:
    def __init__(self, storage_file='scan_results.json'):
        self.storage_file = storage_file
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """Ensure the storage file exists with proper structure"""
        if not os.path.exists(self.storage_file):
            self._save_results({
                'last_scan': None,
                'scan_history': []
            })

    def _save_results(self, data):
        """Save data to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=4)

    def _load_results(self):
        """Load data from storage file"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'last_scan': None, 'scan_history': []}

    def save_scan(self, devices):
        """Save the results of a new scan"""
        data = self._load_results()
        scan_result = {
            'timestamp': datetime.now().isoformat(),
            'devices': devices
        }
        
        # Update last scan
        data['last_scan'] = scan_result
        
        # Add to history (keep last 10 scans)
        data['scan_history'].insert(0, scan_result)
        data['scan_history'] = data['scan_history'][:10]
        
        self._save_results(data)
        return scan_result

    def get_last_scan(self):
        """Get the results of the last scan"""
        data = self._load_results()
        return data.get('last_scan')

    def get_scan_history(self, limit=10):
        """Get the scan history"""
        data = self._load_results()
        return data.get('scan_history', [])[:limit] 