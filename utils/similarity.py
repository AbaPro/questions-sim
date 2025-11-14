import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from .arabic_processor import ArabicProcessor

class SimilarityCalculator:
    """Calculate similarity between Arabic questions"""
    
    def __init__(self):
        self.processor = ArabicProcessor()
        self.vectorizer = TfidfVectorizer(
            analyzer='char',  # Use character n-grams for Arabic
            ngram_range=(2, 4),
            max_features=5000
        )
        self.questions = []
        self.processed_questions = []
        self.tfidf_matrix = None
        
    def fit(self, questions: List[str]):
        """Fit the model with questions"""
        self.questions = questions
        self.processed_questions = [self.processor.preprocess(q) for q in questions]
        
        if self.processed_questions:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_questions)
    
    def get_similar_questions(self, query_idx: int, top_n: int = 100) -> List[Tuple[int, float]]:
        """Get most similar questions to the query question"""
        if self.tfidf_matrix is None or query_idx >= len(self.questions):
            return []
        
        # Get similarity scores
        query_vector = self.tfidf_matrix[query_idx]
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top N similar questions (excluding the query itself)
        similar_indices = similarities.argsort()[::-1]
        
        results = []
        for idx in similar_indices:
            if idx != query_idx and similarities[idx] > 0:
                results.append((idx, similarities[idx]))
                if len(results) >= top_n:
                    break
        
        return results