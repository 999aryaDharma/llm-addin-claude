import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from app.config import settings
from loguru import logger


class CacheManager:
    """Manage context caching untuk Word dan Excel"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.cache_path)
        self.ttl = settings.CACHE_TTL
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cache table untuk summaries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP
                )
            """)
            
            # Context layers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_layers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    layer_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(document_id, layer_type)
                )
            """)
            
            # Document summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT UNIQUE NOT NULL,
                    summary_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON cache(key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_context_doc ON context_layers(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_summary_doc ON summaries(document_id)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cache database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing cache database: {e}")
            raise
    
    def _generate_key(self, *args) -> str:
        """Generate cache key from arguments"""
        key_string = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT value, expires_at, metadata 
                FROM cache 
                WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            
            if row:
                value, expires_at, metadata = row
                
                # Check expiration
                if expires_at:
                    expires = datetime.fromisoformat(expires_at)
                    if datetime.now() > expires:
                        self.delete(key)
                        conn.close()
                        return None
                
                # Update access stats
                cursor.execute("""
                    UPDATE cache 
                    SET access_count = access_count + 1,
                        last_accessed = CURRENT_TIMESTAMP
                    WHERE key = ?
                """, (key,))
                conn.commit()
                
                conn.close()
                
                # Parse JSON value
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate expiration
            ttl = ttl or self.ttl
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # Serialize value
            if not isinstance(value, str):
                value = json.dumps(value)
            
            # Serialize metadata
            metadata_str = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO cache 
                (key, value, metadata, expires_at, last_accessed)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, metadata_str, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Cached key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear all expired cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM cache 
                WHERE expires_at < CURRENT_TIMESTAMP
            """)
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            logger.info(f"Cleared {deleted} expired cache entries")
            return deleted
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0
    
    # Context Layer Methods
    
    def save_context_layer(
        self,
        document_id: str,
        layer_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Save context layer for a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_str = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO context_layers
                (document_id, layer_type, content, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (document_id, layer_type, content, metadata_str))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {layer_type} layer for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving context layer: {e}")
            return False
    
    def get_context_layer(
        self,
        document_id: str,
        layer_type: str
    ) -> Optional[Dict]:
        """Get context layer for a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content, metadata, updated_at
                FROM context_layers
                WHERE document_id = ? AND layer_type = ?
            """, (document_id, layer_type))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                content, metadata_str, updated_at = row
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                return {
                    "content": content,
                    "metadata": metadata,
                    "updated_at": updated_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting context layer: {e}")
            return None
    
    def get_all_layers(self, document_id: str) -> Dict[str, Dict]:
        """Get all context layers for a document"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT layer_type, content, metadata, updated_at
                FROM context_layers
                WHERE document_id = ?
            """, (document_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            layers = {}
            for layer_type, content, metadata_str, updated_at in rows:
                metadata = json.loads(metadata_str) if metadata_str else {}
                layers[layer_type] = {
                    "content": content,
                    "metadata": metadata,
                    "updated_at": updated_at
                }
            
            return layers
            
        except Exception as e:
            logger.error(f"Error getting all layers: {e}")
            return {}
    
    # Summary Methods
    
    def save_summary(
        self,
        document_id: str,
        summary_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Save document summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            metadata_str = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO summaries
                (document_id, summary_type, content, metadata, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (document_id, summary_type, content, metadata_str))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {summary_type} summary for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return False
    
    def get_summary(
        self,
        document_id: str,
        summary_type: str = "full"
    ) -> Optional[Dict]:
        """Get document summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT content, metadata, updated_at
                FROM summaries
                WHERE document_id = ? AND summary_type = ?
            """, (document_id, summary_type))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                content, metadata_str, updated_at = row
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                return {
                    "content": content,
                    "metadata": metadata,
                    "updated_at": updated_at
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM cache")
            cache_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM context_layers")
            layer_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM summaries")
            summary_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM cache 
                WHERE expires_at < CURRENT_TIMESTAMP
            """)
            expired_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "cache_entries": cache_count,
                "context_layers": layer_count,
                "summaries": summary_count,
                "expired_entries": expired_count
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}


# Global instance
cache_manager = CacheManager()