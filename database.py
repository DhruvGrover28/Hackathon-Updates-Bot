import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import hashlib


class Database:
    """Database handler for storing hackathon information and managing deduplication."""
    
    def __init__(self, db_path: str = "hackathons.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create hackathons table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS hackathons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        date_info TEXT,
                        description TEXT,
                        hash TEXT UNIQUE NOT NULL,
                        posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_posted BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Create scraping_log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scraping_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        hackathons_found INTEGER,
                        new_hackathons INTEGER,
                        errors TEXT
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def generate_hash(self, title: str, url: str) -> str:
        """Generate a unique hash for a hackathon to prevent duplicates."""
        content = f"{title.strip().lower()}|{url.strip()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_duplicate(self, title: str, url: str) -> bool:
        """Check if a hackathon already exists in the database."""
        hash_value = self.generate_hash(title, url)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM hackathons WHERE hash = ?", (hash_value,))
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Error checking duplicate: {e}")
            return False
    
    def add_hackathon(self, title: str, url: str, date_info: str = "", description: str = "") -> bool:
        """Add a new hackathon to the database if it's not a duplicate."""
        if self.is_duplicate(title, url):
            return False
        
        hash_value = self.generate_hash(title, url)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO hackathons (title, url, date_info, description, hash)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, url, date_info, description, hash_value))
                conn.commit()
                logging.info(f"Added new hackathon: {title}")
                return True
        except Exception as e:
            logging.error(f"Error adding hackathon: {e}")
            return False
    
    def get_unposted_hackathons(self) -> List[Dict]:
        """Get hackathons that haven't been posted to Telegram yet."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, date_info, description
                    FROM hackathons
                    WHERE is_posted = FALSE
                    ORDER BY id ASC
                ''')
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error getting unposted hackathons: {e}")
            return []
    
    def mark_as_posted(self, hackathon_id: int) -> bool:
        """Mark a hackathon as posted to Telegram."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE hackathons
                    SET is_posted = TRUE
                    WHERE id = ?
                ''', (hackathon_id,))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error marking hackathon as posted: {e}")
            return False
    
    def log_scraping_session(self, hackathons_found: int, new_hackathons: int, errors: str = "") -> None:
        """Log scraping session statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scraping_log (hackathons_found, new_hackathons, errors)
                    VALUES (?, ?, ?)
                ''', (hackathons_found, new_hackathons, errors))
                conn.commit()
        except Exception as e:
            logging.error(f"Error logging scraping session: {e}")
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total hackathons
                cursor.execute("SELECT COUNT(*) FROM hackathons")
                total = cursor.fetchone()[0]
                
                # Posted hackathons
                cursor.execute("SELECT COUNT(*) FROM hackathons WHERE is_posted = TRUE")
                posted = cursor.fetchone()[0]
                
                # Recent scraping sessions
                cursor.execute('''
                    SELECT scraped_at, hackathons_found, new_hackathons
                    FROM scraping_log
                    ORDER BY scraped_at DESC
                    LIMIT 5
                ''')
                recent_sessions = cursor.fetchall()
                
                return {
                    "total_hackathons": total,
                    "posted_hackathons": posted,
                    "pending_hackathons": total - posted,
                    "recent_sessions": recent_sessions
                }
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {}
