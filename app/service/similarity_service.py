import numpy as np

class SimilarityService:
    @staticmethod
    def cosine(a,b):
        return np.dot(a,b)/(
            np.linalg.norm(a) *
            np.linalg.norm(b)
        )