from typing import List
import numpy as np

class NLPService:
    def __init__(self):
        # Using a lightweight model for sentence embeddings
        # Lazy load to avoid import issues
        self.model = None
        self._model_name = 'all-MiniLM-L6-v2'
    
    def _load_model(self):
        """Lazy load the sentence transformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self._model_name)
            except Exception as e:
                print(f"Warning: Could not load sentence transformer model: {e}")
                print("Using fallback similarity calculation")
                self.model = False  # Mark as failed to load
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            numpy array of embeddings
        """
        self._load_model()
        
        if self.model and self.model is not False:
            return self.model.encode(texts)
        else:
            # Fallback: simple bag-of-words representation
            return self._simple_embeddings(texts)
    
    def _simple_embeddings(self, texts: List[str]) -> np.ndarray:
        """Simple fallback embedding using word presence."""
        # Create a simple vocabulary from all texts
        all_words = set()
        for text in texts:
            all_words.update(text.lower().split())
        
        vocab = sorted(list(all_words))
        vocab_index = {word: i for i, word in enumerate(vocab)}
        
        # Create embeddings
        embeddings = []
        for text in texts:
            words = text.lower().split()
            vec = np.zeros(len(vocab))
            for word in words:
                if word in vocab_index:
                    vec[vocab_index[word]] = 1
            embeddings.append(vec)
        
        return np.array(embeddings)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        embeddings = self.get_embeddings([text1, text2])
        
        # Compute cosine similarity
        norm1 = np.linalg.norm(embeddings[0])
        norm2 = np.linalg.norm(embeddings[1])
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(embeddings[0], embeddings[1]) / (norm1 * norm2)
        
        return float(max(0.0, min(1.0, similarity)))  # Clamp between 0 and 1
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key terms from text (simple implementation).
        
        Args:
            text: Input text
            top_n: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction based on word frequency
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:top_n]]

# Singleton instance
nlp_service = NLPService()
