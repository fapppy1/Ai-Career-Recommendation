"""
Hybrid Recommender System - FIXED INDUSTRY FILTERING
"""

from .recommender import ContentBasedRecommender
from .collaborative_filtering import CollaborativeFilteringEngine
from .dataset import CAREER_DATASET

class HybridRecommender:
    def __init__(self):
        self.content_engine = ContentBasedRecommender(CAREER_DATASET)
        self.cf_engine = CollaborativeFilteringEngine()
        self.COLD_START_THRESHOLD = 3
        
    def get_recommendations(self, user_skills, user_id, industry='Technology', 
                          experience_level='Intermediate', top_n=6):
        """Generate hybrid recommendations with PROPER industry filtering"""
        
        # 1. Get content-based recommendations (industry filter applied here)
        content_recs = self.content_engine.get_recommendations(
            user_skills, industry, experience_level, top_n=top_n*2
        )
        
        # 2. Check cold start
        is_cold_start = self.cf_engine.get_cold_start_status(user_id)
        
        # 3. Fuse scores
        hybrid_recs = []
        for rec in content_recs:
            content_score = rec['match_score']
            cf_score = 0.0
            algorithm = 'content_only'
            
            if not is_cold_start and user_id > 0:
                predicted_cf = self.cf_engine.predict_rating(user_id, rec['role'])
                if predicted_cf:
                    cf_normalized = 40 + (predicted_cf - 1) * (55/4)
                    cf_score = cf_normalized
                    algorithm = 'hybrid_cf'
            
            if algorithm == 'hybrid_cf':
                final_score = 0.7 * content_score + 0.3 * cf_score
            else:
                final_score = content_score
                
            rec.update({
                'hybrid_score': round(min(95, max(40, final_score)), 1),
                'content_score': content_score,
                'cf_score': round(cf_score, 1) if cf_score > 0 else None,
                'algorithm': algorithm,
                'cold_start': is_cold_start,
                'industry': rec.get('industry', 'Technology')  # Ensure industry is included
            })
            hybrid_recs.append(rec)
            
        # Sort by hybrid score
        hybrid_recs.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        # Add ranks and return top N
        for i, rec in enumerate(hybrid_recs[:top_n], 1):
            rec['rank'] = i
            
        return hybrid_recs[:top_n]