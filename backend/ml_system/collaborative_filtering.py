"""
Collaborative Filtering Engine
Proposal Alignment: Objective 1 - Research & implement collaborative filtering
Uses user-item interaction matrix + cosine similarity for neighborhood-based prediction
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from database import CareerInteraction, db
from sqlalchemy import func

class CollaborativeFilteringEngine:
    def __init__(self):
        self.user_item_matrix = None
        self.user_ids = []
        self.career_roles = []
        
    def _build_interaction_matrix(self, user_id):
        """Build sparse user-item matrix from database interactions"""
        # Get all distinct career roles interacted with
        roles = db.session.query(func.distinct(CareerInteraction.career_role)).all()
        self.career_roles = [r[0] for r in roles]
        
        # Get all users with interactions
        users = db.session.query(func.distinct(CareerInteraction.user_id)).all()
        self.user_ids = [u[0] for u in users]
        
        if not self.user_ids or not self.career_roles:
            return np.array([])
        
        # Create matrix: rows=users, cols=careers, values=weighted interaction scores
        matrix = np.zeros((len(self.user_ids), len(self.career_roles)))
        user_idx_map = {uid: i for i, uid in enumerate(self.user_ids)}
        role_idx_map = {role: i for i, role in enumerate(self.career_roles)}
        
        interactions = CareerInteraction.query.all()
        for inter in interactions:
            if inter.user_id in user_idx_map and inter.career_role in role_idx_map:
                r, c = user_idx_map[inter.user_id], role_idx_map[inter.career_role]
                # Weight interactions: view=1, favorite=2, rate=rating*2
                if inter.interaction_type == 'view':
                    matrix[r][c] = max(matrix[r][c], 1.0)
                elif inter.interaction_type == 'favorite':
                    matrix[r][c] = max(matrix[r][c], 2.0)
                elif inter.interaction_type == 'rate' and inter.rating:
                    matrix[r][c] = max(matrix[r][c], inter.rating * 2.0)
                    
        self.user_item_matrix = matrix
        return matrix

    def predict_rating(self, target_user_id, career_role, min_neighbors=3):
        """Predict rating for target_user on career_role using user-based CF"""
        matrix = self._build_interaction_matrix(target_user_id)
        if matrix.size == 0:
            return None
            
        user_idx_map = {uid: i for i, uid in enumerate(self.user_ids)}
        role_idx_map = {role: i for i, role in enumerate(self.career_roles)}
        
        if target_user_id not in user_idx_map or career_role not in role_idx_map:
            return None
            
        target_idx = user_idx_map[target_user_id]
        career_idx = role_idx_map[career_role]
        
        # If target user already interacted, return existing score
        if matrix[target_idx][career_idx] > 0:
            return matrix[target_idx][career_idx] / 2.0  # Normalize back to 1-5 scale
            
        # Calculate user similarities
        target_vec = matrix[target_idx].reshape(1, -1)
        similarities = cosine_similarity(target_vec, matrix)[0]
        similarities[target_idx] = 0  # Exclude self
        
        # Get top-K similar users who interacted with this career
        neighbor_indices = np.argsort(similarities)[::-1][:min_neighbors*2]
        
        numerator = 0.0
        denominator = 0.0
        for n_idx in neighbor_indices:
            if matrix[n_idx][career_idx] > 0 and similarities[n_idx] > 0.1:
                numerator += similarities[n_idx] * matrix[n_idx][career_idx]
                denominator += abs(similarities[n_idx])
                
        if denominator == 0:
            return None
            
        predicted_score = numerator / denominator
        return min(5.0, max(1.0, predicted_score / 2.0))  # Clamp to 1-5 scale

    def get_cold_start_status(self, user_id):
        """Check if user has enough interactions for CF"""
        count = CareerInteraction.query.filter_by(user_id=user_id).count()
        return count < 3  # Cold start if < 3 interactions