"""
Hybrid Recommendation Engine - Real ML Implementation
Proposal Alignment: Objective 1 - Advanced recommendation algorithms
Uses: TF-IDF vectorization + Cosine Similarity + User-based CF
"""
import logging
import re
from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


class ContentBasedEngine:
    """
    Content-based filtering using TF-IDF + Cosine Similarity.
    """

    def __init__(self, careers: List[Dict]):
        self.careers = careers
        self.skill_aliases = {
            "comunication": "communication",
            "microsoft word": "microsoft office",
            "ms word": "microsoft office",
            "word": "microsoft office",
            "excel": "microsoft office",
            "health and safety": "health safety",
            "health & safety": "health safety",
            "first aid": "patient care",
            "teamwork": "team work",
            "customer care": "customer service",
            "admin": "administration",
            "record keeping": "documentation",
            "patient support": "patient care",
        }
        self.vectorizer = TfidfVectorizer(
            token_pattern=r"(?u)\b[\w\+\#\.]+\b",
            stop_words="english",
            lowercase=True,
            max_features=1000,
        )
        self.career_matrix = None
        self.career_ids = []
        self._build_index()
        logger.info(f"Content engine initialized with {len(careers)} careers")

    def _normalize_skill(self, skill: str) -> str:
        cleaned = re.sub(r"\s+", " ", (skill or "").strip().lower())
        return self.skill_aliases.get(cleaned, cleaned)

    def _normalize_skill_list(self, skills: List[str]) -> List[str]:
        return [normalized for normalized in (self._normalize_skill(skill) for skill in skills) if normalized]

    def _format_skill_label(self, skill: str) -> str:
        return skill.replace("/", " / ").title()

    def _build_index(self):
        """Build TF-IDF index for all careers."""
        career_texts = []
        self.career_ids = []

        for career in self.careers:
            normalized_required = self._normalize_skill_list(career.get("required_skills", []))
            text_parts = [
                career.get("role", ""),
                career.get("description", ""),
                " ".join(normalized_required),
                " ".join(career.get("industry_tags", [])),
                career.get("experience_level", ""),
                career.get("salary_range", ""),
            ]
            career_texts.append(" ".join(filter(None, text_parts)))
            self.career_ids.append(career.get("id"))

        if career_texts:
            self.career_matrix = self.vectorizer.fit_transform(career_texts)
            logger.debug(f"TF-IDF matrix shape: {self.career_matrix.shape}")

    def get_recommendations(
        self,
        user_skills: List[str],
        industry: str = None,
        experience_level: str = None,
        top_n: int = 6,
    ) -> List[Dict]:
        if self.career_matrix is None or self.career_matrix.shape[0] == 0:
            logger.warning("Career matrix not built - returning empty recommendations")
            return []

        normalized_user_skills = self._normalize_skill_list(user_skills)
        user_text = " ".join(normalized_user_skills)

        try:
            user_vector = self.vectorizer.transform([user_text])
        except Exception as e:
            logger.error(f"Vectorization error: {e}")
            return []

        similarities = cosine_similarity(user_vector, self.career_matrix)[0]
        top_indices = np.argsort(similarities)[::-1][: top_n * 3]

        recommendations = []
        for idx in top_indices:
            if len(recommendations) >= top_n:
                break

            career = self.careers[idx]
            if industry and career.get("industry") != industry:
                continue

            career_experience = career.get("experience_level")
            if experience_level and career_experience and career_experience != experience_level:
                continue

            match_score = round(float(similarities[idx]) * 100, 1)
            normalized_required = self._normalize_skill_list(career.get("required_skills", []))
            matched = [
                original
                for original, normalized in zip(user_skills, normalized_user_skills)
                if normalized in normalized_required
            ]
            missing = [
                skill
                for skill, normalized in zip(career.get("required_skills", []), normalized_required)
                if normalized not in normalized_user_skills
            ][:5]
            confidence = round(match_score / 100, 2)

            recommendations.append(
                {
                    "id": career.get("id"),
                    "role": career.get("role"),
                    "industry": career.get("industry"),
                    "description": career.get("description"),
                    "required_skills": career.get("required_skills", []),
                    "salary_range": career.get("salary_range"),
                    "growth_outlook": career.get("growth_outlook"),
                    "match_score": match_score,
                    "confidence": confidence,
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "algorithm": "content_based_tfidf",
                    "cold_start": False,
                    "explainability": {
                        "matched_count": len(matched),
                        "required_count": len(career.get("required_skills", [])),
                        "similarity_score": match_score,
                        "confidence": confidence,
                        "top_matching_keywords": matched[:3] if matched else [],
                    },
                }
            )

        logger.info(f"Generated {len(recommendations)} content-based recommendations")
        return recommendations

    def analyze_skills(self, user_skills: List[str]) -> Dict:
        analysis = {}
        normalized_user_skills = self._normalize_skill_list(user_skills)

        for career in self.careers[:20]:
            required = self._normalize_skill_list(career.get("required_skills", []))
            if not required:
                continue

            matched = [
                original
                for original, normalized in zip(user_skills, normalized_user_skills)
                if normalized in required
            ]
            missing = [
                skill
                for skill, normalized in zip(career.get("required_skills", []), required)
                if normalized not in normalized_user_skills
            ]
            coverage = round(len(matched) / len(required) * 100, 1) if required else 0

            analysis[career["role"]] = {
                "coverage_pct": coverage,
                "matched_skills": matched,
                "missing_skills": missing[:5],
                "suggested_additions": missing[:3] if coverage < 80 else [],
                "confidence": round(coverage / 100, 2),
            }

        all_required = set()
        for career in self.careers:
            all_required.update(self._normalize_skill_list(career.get("required_skills", [])))

        user_set = set(normalized_user_skills)
        overall_coverage = round(len(user_set & all_required) / len(all_required) * 100, 1) if all_required else 0

        analysis["overall"] = {
            "skills_provided": len(user_skills),
            "relevant_to_careers": len(user_set & all_required),
            "coverage_pct": overall_coverage,
            "top_missing": [self._format_skill_label(skill) for skill in list(all_required - user_set)[:5]],
            "confidence": round(overall_coverage / 100, 2),
        }

        return analysis


class CollaborativeFilteringEngine:
    """
    User-based collaborative filtering using K-Nearest Neighbors.
    """

    def __init__(self, interactions: List[Dict], n_neighbors: int = 5):
        self.interactions = interactions
        self.n_neighbors = n_neighbors
        self.user_item_matrix = None
        self.user_ids = []
        self.item_ids = []
        self.user_index_map = {}
        self.item_index_map = {}
        self.knn_model = None
        self._build_matrix()
        logger.info(f"CF engine initialized with {len(interactions)} interactions")

    def _build_matrix(self):
        if not self.interactions:
            logger.debug("No interactions for CF matrix")
            return

        self.user_ids = list(set(i["user_id"] for i in self.interactions))
        self.item_ids = list(set(i["career_role"] for i in self.interactions))

        if len(self.user_ids) < 2 or len(self.item_ids) < 2:
            logger.debug("Insufficient users/items for CF")
            return

        self.user_index_map = {uid: i for i, uid in enumerate(self.user_ids)}
        self.item_index_map = {item: i for i, item in enumerate(self.item_ids)}
        self.user_item_matrix = np.zeros((len(self.user_ids), len(self.item_ids)))

        for interaction in self.interactions:
            if interaction.get("rating"):
                try:
                    user_idx = self.user_index_map[interaction["user_id"]]
                    item_idx = self.item_index_map[interaction["career_role"]]
                    self.user_item_matrix[user_idx, item_idx] = interaction["rating"]
                except (KeyError, IndexError):
                    continue

        if self.user_item_matrix.shape[0] >= 2:
            self.knn_model = NearestNeighbors(
                n_neighbors=min(self.n_neighbors, len(self.user_ids)),
                metric="cosine",
            )
            self.knn_model.fit(self.user_item_matrix)

    def get_recommendations(self, user_id: int, content_recs: List[Dict], top_n: int = 6) -> List[Dict]:
        if self.user_item_matrix is None or len(self.user_ids) < 2 or self.knn_model is None:
            for rec in content_recs:
                rec["algorithm"] = "content_fallback"
                rec["cold_start"] = True
            return content_recs

        try:
            if user_id not in self.user_index_map:
                for rec in content_recs:
                    rec["algorithm"] = "content_fallback"
                    rec["cold_start"] = True
                return content_recs

            user_idx = self.user_index_map[user_id]
            user_vector = self.user_item_matrix[user_idx].reshape(1, -1)
            distances, indices = self.knn_model.kneighbors(user_vector)

            predictions = {}
            for i, item in enumerate(self.item_ids):
                if self.user_item_matrix[user_idx, i] == 0:
                    numerator = sum(
                        self.user_item_matrix[idx, i] * (1 - dist)
                        for idx, dist in zip(indices[0], distances[0])
                        if self.user_item_matrix[idx, i] > 0
                    )
                    denominator = sum(
                        1 - dist
                        for idx, dist in zip(indices[0], distances[0])
                        if self.user_item_matrix[idx, i] > 0
                    )
                    if denominator > 0:
                        predictions[item] = numerator / denominator

            if predictions:
                cf_scores = list(predictions.values())
                if max(cf_scores) > 0:
                    scaler = MinMaxScaler(feature_range=(0, 100))
                    normalized = scaler.fit_transform(np.array(cf_scores).reshape(-1, 1)).flatten()
                    for item, score in zip(predictions.keys(), normalized):
                        predictions[item] = round(score, 1)

            cf_recs = []
            for role, cf_score in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
                matching = next((r for r in content_recs if r["role"] == role), None)
                if matching:
                    blended = round(0.7 * matching["match_score"] + 0.3 * cf_score, 1)
                    matching["match_score"] = blended
                    matching["algorithm"] = "hybrid_tfidf_cf"
                    matching["cold_start"] = False
                    matching["cf_score"] = cf_score
                    matching["confidence"] = round(blended / 100, 2)
                    cf_recs.append(matching)

            for rec in content_recs:
                if rec not in cf_recs and len(cf_recs) < top_n:
                    rec["algorithm"] = "hybrid_tfidf_cf"
                    rec["cold_start"] = False
                    rec["confidence"] = round(rec["match_score"] / 100, 2)
                    cf_recs.append(rec)

            return cf_recs[:top_n]
        except Exception as e:
            logger.error(f"CF error: {e}")
            for rec in content_recs:
                rec["algorithm"] = "content_fallback"
                rec["cold_start"] = True
            return content_recs[:top_n]


class HybridRecommender:
    """
    Main hybrid recommender: 70% content + 30% collaborative filtering.
    """

    def __init__(self, careers: List[Dict], interactions: List[Dict] = None):
        self.content_engine = ContentBasedEngine(careers)
        self.cf_engine = CollaborativeFilteringEngine(interactions or [], n_neighbors=5)
        self.content_weight = 0.7
        self.cf_weight = 0.3
        logger.info("Hybrid recommender initialized")

    def _experience_fallback_order(self, experience_level: str) -> List[str]:
        mapping = {
            "Beginner": ["Beginner", "Intermediate"],
            "Intermediate": ["Intermediate", "Beginner", "Advanced"],
            "Advanced": ["Advanced", "Intermediate", "Expert"],
            "Expert": ["Expert", "Advanced", "Intermediate"],
        }
        return mapping.get(experience_level, [experience_level] if experience_level else [])

    def get_recommendations(
        self,
        user_skills: List[str],
        user_id: int = 0,
        industry: str = None,
        experience_level: str = None,
        top_n: int = 6,
    ) -> List[Dict]:
        requested_industry = None if industry == "Other" else industry

        content_recs = []
        for candidate_level in self._experience_fallback_order(experience_level):
            content_recs = self.content_engine.get_recommendations(
                user_skills, requested_industry, candidate_level, top_n * 2
            )
            if content_recs:
                if candidate_level != experience_level:
                    for rec in content_recs:
                        rec["fallback_reason"] = (
                            f"No exact {experience_level.lower()} matches were found; "
                            f"showing the closest {candidate_level.lower()} roles."
                        )
                break

        if not content_recs:
            content_recs = self.content_engine.get_recommendations(
                user_skills, requested_industry, experience_level, top_n * 2
            )

        if not content_recs:
            logger.info(
                "No recommendations found for industry=%s, falling back to cross-industry matching",
                industry,
            )
            content_recs = self.content_engine.get_recommendations(
                user_skills, None, experience_level, top_n * 2
            )
            for rec in content_recs:
                rec["fallback_reason"] = f"No direct matches for {industry}; showing best overall matches"

        if not content_recs and experience_level:
            logger.info(
                "No recommendations found for experience_level=%s, retrying without experience filter",
                experience_level,
            )
            content_recs = self.content_engine.get_recommendations(
                user_skills, requested_industry, None, top_n * 2
            )

        if not content_recs:
            content_recs = self.content_engine.get_recommendations(
                user_skills, None, None, top_n * 2
            )

        if user_id > 0 and len(self.cf_engine.user_ids) >= 2:
            final_recs = self.cf_engine.get_recommendations(user_id, content_recs, top_n)
        else:
            final_recs = content_recs[:top_n]
            for rec in final_recs:
                rec["cold_start"] = True
                rec["algorithm"] = "content_based_tfidf"

        for rec in final_recs:
            if "confidence" not in rec:
                rec["confidence"] = round(rec.get("match_score", 0) / 100, 2)

        return final_recs

    def analyze_skills(self, user_skills: List[str]) -> Dict:
        return self.content_engine.analyze_skills(user_skills)

    def evaluate_recommendations(self, recommendations: List[Dict], ground_truth_roles: List[str], k: int = 5) -> Dict:
        if not recommendations or not ground_truth_roles:
            return {
                "precision_at_k": 0.0,
                "recall_at_k": 0.0,
                "f1_score": 0.0,
                "note": "Insufficient data for evaluation",
            }

        recommended_roles = [r["role"] for r in recommendations[:k]]
        relevant_count = sum(1 for role in recommended_roles if role in ground_truth_roles)
        precision = relevant_count / k if k > 0 else 0.0
        recall = relevant_count / len(ground_truth_roles) if ground_truth_roles else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision_at_k": round(precision, 3),
            "recall_at_k": round(recall, 3),
            "f1_score": round(f1, 3),
            "k": k,
            "total_recommendations": len(recommendations),
            "relevant_ground_truth": len(ground_truth_roles),
        }
