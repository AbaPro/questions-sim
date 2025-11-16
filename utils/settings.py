import json
import os
from typing import Set

class Settings:
    """Global settings manager for the application"""
    
    DEFAULT_STOP_WORDS = {
        'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هل', 'ما', 'ماذا', 'كيف',
        'لماذا', 'متى', 'أين', 'هذا', 'هذه', 'ذلك', 'تلك', 'التي', 'الذي',
        'و', 'أو', 'ثم', 'لكن', 'أن', 'إن', 'لا', 'نعم', 'قد', 'كان',
        'يكون', 'كل', 'بعض', 'أي', 'هناك', 'هنا', 'عند', 'لدى', 'ال'
    }
    
    SETTINGS_FILE = 'app_settings.json'
    
    _instance = None
    _stop_words = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        """Load settings from file or use defaults"""
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._stop_words = set(data.get('stop_words', self.DEFAULT_STOP_WORDS))
            except Exception as e:
                print(f"Error loading settings: {e}")
                self._stop_words = self.DEFAULT_STOP_WORDS.copy()
        else:
            self._stop_words = self.DEFAULT_STOP_WORDS.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            data = {
                'stop_words': list(self._stop_words)
            }
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    @property
    def stop_words(self) -> Set[str]:
        """Get current stop words"""
        return self._stop_words
    
    def add_stop_word(self, word: str):
        """Add a stop word"""
        self._stop_words.add(word.strip())
    
    def remove_stop_word(self, word: str):
        """Remove a stop word"""
        self._stop_words.discard(word.strip())
    
    def reset_to_defaults(self):
        """Reset stop words to defaults"""
        self._stop_words = self.DEFAULT_STOP_WORDS.copy()
    
    def update_stop_words(self, words: Set[str]):
        """Update all stop words at once"""
        self._stop_words = words