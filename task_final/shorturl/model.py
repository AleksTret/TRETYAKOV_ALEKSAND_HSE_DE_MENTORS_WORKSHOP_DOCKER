import sqlite3
import hashlib
import secrets
import os
from datetime import datetime

class URLShortener:
    def __init__(self, db_path: str = "/app/data/urls.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_id TEXT UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                click_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_short_id ON urls(short_id)')
        conn.commit()
        conn.close()
    
    def generate_short_id(self, url: str) -> str:
        """Генерация уникального короткого ID"""
        while True:
            # Создаем 6-символьный хеш
            salt = secrets.token_hex(4)
            hash_input = url + salt + str(datetime.now().timestamp())
            short_id = hashlib.md5(hash_input.encode()).hexdigest()[:6]
            
            # Проверяем уникальность
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT short_id FROM urls WHERE short_id = ?", (short_id,))
            if not cursor.fetchone():
                conn.close()
                return short_id
            conn.close()
    
    def save_url(self, original_url: str, short_id: str):
        """Сохранение URL в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO urls (short_id, original_url) VALUES (?, ?)",
            (short_id, original_url)
        )
        conn.commit()
        conn.close()
    
    def get_url(self, short_id: str):
        """Получение оригинального URL по короткому ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT original_url, click_count FROM urls WHERE short_id = ?",
            (short_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result
    
    def increment_click_count(self, short_id: str, current_count: int):
        """Увеличение счетчика кликов"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE urls SET click_count = ? WHERE short_id = ?",
            (current_count + 1, short_id)
        )
        conn.commit()
        conn.close()
    
    def get_stats(self, short_id: str):
        """Получение статистики по короткой ссылке"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT short_id, original_url, created_at, click_count FROM urls WHERE short_id = ?",
            (short_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result