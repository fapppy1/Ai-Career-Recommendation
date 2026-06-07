"""
Content-Based Career Recommender
Aligned with Proposal Objective 1: Research recommendation algorithms
Uses cosine similarity for skill-based matching with proper industry filtering
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .dataset import CAREER_DATASET

class ContentBasedRecommender:
    def __init__(self, career_dataset=None):
        self.careers = career_dataset or CAREER_DATASET
        self._build_skill_index()
    
    def _build_skill_index(self):
        """Build index of all unique skills across careers"""
        all_skills = set()
        for career in self.careers:
            all_skills.update(skill.lower().strip() for skill in career.get('required_skills', []))
        self.all_skills = sorted(list(all_skills))
        print(f"✅ Skill index built: {len(self.all_skills)} unique skills")
    
    def _vectorize_skills(self, skill_list):
        """Convert list of skills to binary feature vector"""
        skill_lower = [s.lower().strip() for s in skill_list]
        return np.array([1 if skill in skill_lower else 0 for skill in self.all_skills])
    
    def calculate_match_score(self, user_skills, career):
        """Calculate match score using cosine similarity"""
        user_vector = self._vectorize_skills(user_skills).reshape(1, -1)
        career_vector = self._vectorize_skills(career.get('required_skills', [])).reshape(1, -1)
        similarity = cosine_similarity(user_vector, career_vector)[0][0]
        scaled_score = 40 + (similarity * 55)
        return round(min(95, max(40, scaled_score)), 1)
    
    def get_recommendations(self, user_skills, industry='Technology', 
                          experience_level='Intermediate', top_n=6):
        """Generate personalized career recommendations with PROPER industry filtering"""
        if not user_skills:
            return []
        
        exp_adjustment = {
            'Beginner': -5,
            'Intermediate': 0,
            'Advanced': 3,
            'Expert': 5
        }.get(experience_level, 0)
        
        recommendations = []
        
        for career in self.careers:
            # ===== CRITICAL FIX: Proper industry filtering =====
            career_industry = career.get('industry', 'Technology')
            
            # If user selected specific industry (not 'Other' or 'All'), filter strictly
            if industry and industry.lower() not in ['other', 'all', '']:
                if career_industry.lower() != industry.lower():
                    continue  # Skip careers not in selected industry
            
            # Calculate base match score
            base_score = self.calculate_match_score(user_skills, career)
            
            # Adjust for experience level
            final_score = min(95, max(40, base_score + exp_adjustment))
            
            # Identify missing/matched skills
            user_skills_lower = [s.lower() for s in user_skills]
            career_skills = career.get('required_skills', [])
            missing_skills = [s for s in career_skills if s.lower() not in user_skills_lower]
            matched_skills = [s for s in career_skills if s.lower() in user_skills_lower]
            
            recommendations.append({
                "role": career['role'],
                "match_score": round(final_score, 1),
                "skills_needed": missing_skills[:5],
                "skills_matched": matched_skills,
                "description": career.get('description', ''),
                "salary_range": f"£{career['salary_min']:,} - £{career['salary_max']:,}",
                "growth_outlook": career.get('growth', 'Medium'),
                "required_skills": career_skills,
                "industry": career_industry,
                "source": "content_based",
                "algorithm": "cosine_similarity"
            })
        
        # Sort by match score and return top N
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Add rank
        for i, rec in enumerate(recommendations[:top_n], 1):
            rec['rank'] = i
        
        return recommendations[:top_n]
    
    def analyze_skills(self, user_skills):
        """Analyze user skills against career requirements"""
        if not user_skills:
            return {}
        
        categories = {
            "Programming": ["python", "javascript", "java", "c++", "sql"],
            "ML/AI": ["machine learning", "tensorflow", "pytorch", "deep learning", "nlp"],
            "Data": ["data analysis", "statistics", "pandas", "numpy", "visualization"],
            "Cloud/DevOps": ["aws", "azure", "docker", "kubernetes", "ci/cd"],
            "Security": ["network security", "risk assessment", "penetration testing", "siem"],
            "Healthcare": ["patient care", "medical records", "hipaa", "clinical research", "health informatics"],
            "Soft Skills": ["communication", "leadership", "problem solving", "agile"]
        }
        
        user_lower = [s.lower().strip() for s in user_skills]
        analysis = {}
        
        for category, keywords in categories.items():
            matched = [kw.title() for kw in keywords if kw in user_lower]
            if matched:
                analysis[category] = {
                    "matched_skills": matched,
                    "coverage_pct": round(len(matched) / len(keywords) * 100, 1),
                    "suggested_additions": [kw.title() for kw in keywords[:2] if kw not in user_lower]
                }
        
        # Overall coverage
        all_career_skills = set()
        for career in self.careers:
            all_career_skills.update(s.lower() for s in career.get('required_skills', []))
        
        covered = len([s for s in user_lower if s in all_career_skills])
        total = len(all_career_skills)
        
        analysis["overall"] = {
            "skills_provided": len(user_skills),
            "relevant_to_careers": covered,
            "coverage_percentage": round(covered / total * 100, 1) if total > 0 else 0,
            "top_missing": [s.title() for s in list(all_career_skills - set(user_lower))[:5]]
        }
        
        return analysis