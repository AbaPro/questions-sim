import pandas as pd
from typing import List, Tuple

class DataLoader:
    """Load questions from Excel file"""
    
    @staticmethod
    def load_excel(file_path: str) -> Tuple[List[str], List[str]]:
        """
        Load questions from Excel file with columns: id, question
        Returns: (ids, questions)
        """
        try:
            df = pd.read_excel(file_path)
            
            # Validate columns
            if 'id' not in df.columns or 'question' not in df.columns:
                raise ValueError("Excel file must have 'id' and 'question' columns")
            
            # Remove empty questions
            df = df.dropna(subset=['question'])
            
            ids = df['id'].astype(str).tolist()
            questions = df['question'].astype(str).tolist()
            
            return ids, questions
        
        except Exception as e:
            raise Exception(f"Error loading Excel file: {str(e)}")