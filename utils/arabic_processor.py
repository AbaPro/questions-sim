import re
from typing import List

class ArabicProcessor:
    """Process Arabic text for similarity comparison"""
    
    # Common Arabic stop words that don't add meaning
    STOP_WORDS = {
        'في', 'من', 'إلى', 'على', 'عن', 'مع', 'هل', 'ما', 'ماذا', 'كيف',
        'لماذا', 'متى', 'أين', 'هذا', 'هذه', 'ذلك', 'تلك', 'التي', 'الذي',
        'و', 'أو', 'ثم', 'لكن', 'أن', 'إن', 'لا', 'نعم', 'قد', 'كان',
        'يكون', 'كل', 'بعض', 'أي', 'هناك', 'هنا', 'عند', 'لدى', 'ال'
    }
    
    @staticmethod
    def normalize_arabic(text: str) -> str:
        """Normalize Arabic text by removing diacritics and normalizing characters"""
        if not text:
            return ""
        
        # Remove Arabic diacritics
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        
        # Normalize Alef variants
        text = re.sub(r'[إأآا]', 'ا', text)
        
        # Normalize Teh Marbuta
        text = re.sub(r'ة', 'ه', text)
        
        # Normalize Yeh variants
        text = re.sub(r'ى', 'ي', text)
        
        return text
    
    @staticmethod
    def remove_stop_words(text: str) -> str:
        """Remove common Arabic stop words"""
        words = text.split()
        filtered_words = [word for word in words if word not in ArabicProcessor.STOP_WORDS]
        return ' '.join(filtered_words)
    
    @staticmethod
    def preprocess(text: str) -> str:
        """Full preprocessing pipeline for Arabic text"""
        if not text:
            return ""
        
        # Convert to lowercase and strip
        text = text.strip().lower()
        
        # Normalize Arabic characters
        text = ArabicProcessor.normalize_arabic(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove stop words
        text = ArabicProcessor.remove_stop_words(text)
        
        return text