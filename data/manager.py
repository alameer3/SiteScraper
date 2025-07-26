"""
Data Management System
Organized data handling, caching, reporting, and export capabilities.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib

class DataManager:
    """Centralized data management for the website analyzer."""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        
        # Create directory structure
        self.directories = {
            'cache': os.path.join(base_path, 'cache'),
            'exports': os.path.join(base_path, 'exports'),
            'reports': os.path.join(base_path, 'reports'),
            'templates': os.path.join(base_path, 'templates'),
            'backups': os.path.join(base_path, 'backups')
        }
        
        self._create_directories()
        self._init_cache_db()
    
    def _create_directories(self):
        """Create all necessary directories."""
        for directory in self.directories.values():
            os.makedirs(directory, exist_ok=True)
    
    def _init_cache_db(self):
        """Initialize cache database."""
        cache_db_path = os.path.join(self.directories['cache'], 'cache.db')
        
        with sqlite3.connect(cache_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS url_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_hash TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_url_hash ON url_cache(url_hash)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at ON url_cache(expires_at)
            ''')
    
    def cache_data(self, url: str, data: Dict, expires_hours: int = 24) -> bool:
        """Cache extraction data for a URL."""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            data_json = json.dumps(data, ensure_ascii=False)
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            cache_db_path = os.path.join(self.directories['cache'], 'cache.db')
            
            with sqlite3.connect(cache_db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO url_cache 
                    (url_hash, url, data, expires_at) 
                    VALUES (?, ?, ?, ?)
                ''', (url_hash, url, data_json, expires_at))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Cache storage failed: {e}")
            return False
    
    def get_cached_data(self, url: str) -> Optional[Dict]:
        """Retrieve cached data for a URL."""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cache_db_path = os.path.join(self.directories['cache'], 'cache.db')
            
            with sqlite3.connect(cache_db_path) as conn:
                cursor = conn.execute('''
                    SELECT data, expires_at FROM url_cache 
                    WHERE url_hash = ? AND expires_at > CURRENT_TIMESTAMP
                ''', (url_hash,))
                
                result = cursor.fetchone()
                
                if result:
                    # Update access statistics
                    conn.execute('''
                        UPDATE url_cache 
                        SET access_count = access_count + 1, 
                            last_accessed = CURRENT_TIMESTAMP
                        WHERE url_hash = ?
                    ''', (url_hash,))
                    
                    return json.loads(result[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache retrieval failed: {e}")
            return None
    
    def clean_expired_cache(self) -> int:
        """Clean expired cache entries."""
        try:
            cache_db_path = os.path.join(self.directories['cache'], 'cache.db')
            
            with sqlite3.connect(cache_db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM url_cache WHERE expires_at <= CURRENT_TIMESTAMP
                ''')
                
                return cursor.rowcount
                
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")
            return 0
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache usage statistics."""
        try:
            cache_db_path = os.path.join(self.directories['cache'], 'cache.db')
            
            with sqlite3.connect(cache_db_path) as conn:
                # Get total entries
                total_entries = conn.execute('SELECT COUNT(*) FROM url_cache').fetchone()[0]
                
                # Get expired entries
                expired_entries = conn.execute('''
                    SELECT COUNT(*) FROM url_cache WHERE expires_at <= CURRENT_TIMESTAMP
                ''').fetchone()[0]
                
                # Get most accessed URLs
                top_urls = conn.execute('''
                    SELECT url, access_count FROM url_cache 
                    ORDER BY access_count DESC LIMIT 10
                ''').fetchall()
                
                return {
                    'total_entries': total_entries,
                    'expired_entries': expired_entries,
                    'active_entries': total_entries - expired_entries,
                    'top_accessed_urls': [{'url': url, 'count': count} for url, count in top_urls]
                }
                
        except Exception as e:
            self.logger.error(f"Cache statistics failed: {e}")
            return {}
    
    def save_report(self, report_name: str, report_data: Dict, report_type: str = 'analysis') -> str:
        """Save analysis report."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{report_name}_{timestamp}.json"
            filepath = os.path.join(self.directories['reports'], filename)
            
            # Add metadata
            report_with_meta = {
                'metadata': {
                    'report_name': report_name,
                    'report_type': report_type,
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'data': report_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_with_meta, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Report saving failed: {e}")
            return ""
    
    def load_report(self, filename: str) -> Optional[Dict]:
        """Load saved report."""
        try:
            filepath = os.path.join(self.directories['reports'], filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Report loading failed: {e}")
            return None
    
    def list_reports(self, report_type: Optional[str] = None) -> List[Dict]:
        """List all saved reports."""
        try:
            reports = []
            reports_dir = self.directories['reports']
            
            for filename in os.listdir(reports_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(reports_dir, filename)
                    stat = os.stat(filepath)
                    
                    # Parse filename for metadata
                    parts = filename.replace('.json', '').split('_')
                    if len(parts) >= 3:
                        file_report_type = parts[0]
                        
                        if report_type is None or file_report_type == report_type:
                            reports.append({
                                'filename': filename,
                                'report_type': file_report_type,
                                'size': stat.st_size,
                                'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'path': filepath
                            })
            
            return sorted(reports, key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Report listing failed: {e}")
            return []
    
    def create_backup(self, name: str) -> str:
        """Create backup of current data."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{name}_{timestamp}"
            backup_path = os.path.join(self.directories['backups'], backup_name)
            
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup cache database
            cache_source = os.path.join(self.directories['cache'], 'cache.db')
            if os.path.exists(cache_source):
                cache_backup = os.path.join(backup_path, 'cache.db')
                with open(cache_source, 'rb') as src, open(cache_backup, 'wb') as dst:
                    dst.write(src.read())
            
            # Backup reports
            reports_backup = os.path.join(backup_path, 'reports')
            os.makedirs(reports_backup, exist_ok=True)
            
            for filename in os.listdir(self.directories['reports']):
                source_file = os.path.join(self.directories['reports'], filename)
                backup_file = os.path.join(reports_backup, filename)
                with open(source_file, 'rb') as src, open(backup_file, 'wb') as dst:
                    dst.write(src.read())
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return ""
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information and statistics."""
        storage_info = {}
        
        try:
            for name, path in self.directories.items():
                if os.path.exists(path):
                    total_size = 0
                    file_count = 0
                    
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                    
                    storage_info[name] = {
                        'path': path,
                        'total_size_bytes': total_size,
                        'total_size_mb': round(total_size / (1024 * 1024), 2),
                        'file_count': file_count
                    }
                else:
                    storage_info[name] = {
                        'path': path,
                        'exists': False
                    }
            
            return storage_info
            
        except Exception as e:
            self.logger.error(f"Storage info retrieval failed: {e}")
            return {}
    
    def organize_data(self) -> Dict[str, Any]:
        """Organize and optimize data storage."""
        results = {
            'cache_cleaned': 0,
            'reports_organized': 0,
            'space_freed_mb': 0,
            'errors': []
        }
        
        try:
            # Clean expired cache
            results['cache_cleaned'] = self.clean_expired_cache()
            
            # Organize reports by date
            reports_by_date = {}
            for report in self.list_reports():
                date = report['created'][:10]  # YYYY-MM-DD
                if date not in reports_by_date:
                    reports_by_date[date] = []
                reports_by_date[date].append(report)
            
            # Create date-based folders
            for date, reports in reports_by_date.items():
                date_folder = os.path.join(self.directories['reports'], date)
                os.makedirs(date_folder, exist_ok=True)
                
                for report in reports:
                    source_path = report['path']
                    target_path = os.path.join(date_folder, report['filename'])
                    
                    if source_path != target_path and os.path.exists(source_path):
                        os.rename(source_path, target_path)
                        results['reports_organized'] += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"Data organization failed: {e}")
            results['errors'].append(str(e))
            return results