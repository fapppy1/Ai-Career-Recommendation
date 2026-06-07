"""
Evaluation Metrics for Dissertation Chapter 4
Proposal Alignment: Objective 6 - Quantitative evaluation
"""
from datetime import datetime, timedelta, timezone
import logging
import os
import re
from typing import List, Optional

from database.models import MLFeedback, UserBehavior

logger = logging.getLogger(__name__)


def calculate_precision_at_k(recommendations: List[dict], ground_truth_roles: List[str], k: int = 5) -> float:
    """
    Calculate Precision@K: Of the top-K recommendations, how many are relevant?

    Formula: Precision@K = |Relevant ∩ Recommended| / K
    """
    if not recommendations or not ground_truth_roles:
        return 0.0

    recommended_roles = [r["role"] for r in recommendations[:k]]
    relevant_count = sum(1 for role in recommended_roles if role in ground_truth_roles)

    return round(relevant_count / k, 3) if k > 0 else 0.0


def calculate_recall_at_k(recommendations: List[dict], ground_truth_roles: List[str], k: int = 5) -> float:
    """
    Calculate Recall@K: Of all relevant items, how many were recommended?

    Formula: Recall@K = |Relevant ∩ Recommended| / |Relevant|
    """
    if not recommendations or not ground_truth_roles:
        return 0.0

    recommended_roles = [r["role"] for r in recommendations[:k]]
    relevant_count = sum(1 for role in recommended_roles if role in ground_truth_roles)

    return round(relevant_count / len(ground_truth_roles), 3) if ground_truth_roles else 0.0


def calculate_f1_score(precision: float, recall: float) -> float:
    """Calculate F1-Score (harmonic mean of precision and recall)."""
    if precision + recall == 0:
        return 0.0
    return round(2 * (precision * recall) / (precision + recall), 3)


def get_recommendation_accuracy(user_id: Optional[int] = None, days: int = 30) -> dict:
    """Calculate recommendation quality metrics from recorded user feedback."""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        query = MLFeedback.query.filter(MLFeedback.timestamp >= cutoff)
        if user_id:
            query = query.filter_by(user_id=user_id)

        feedback = query.all()

        if not feedback:
            return {
                "period_days": days,
                "total_feedback": 0,
                "message": "Insufficient feedback data for evaluation"
            }

        ratings = [f.feedback_score for f in feedback]
        avg_rating = sum(ratings) / len(ratings)
        precision_at_5 = round(sum(1 for r in ratings if r >= 4) / len(ratings), 3)
        recall_at_5 = round(sum(1 for r in ratings if r >= 3) / len(ratings), 3)

        return {
            "period_days": days,
            "total_feedback": len(feedback),
            "average_rating": round(avg_rating, 2),
            "precision_at_4_plus": precision_at_5,
            "high_ratings_pct": round(sum(1 for r in ratings if r >= 4) / len(ratings) * 100, 1),
            "rating_distribution": {
                "5_star": sum(1 for r in ratings if r == 5),
                "4_star": sum(1 for r in ratings if r == 4),
                "3_star": sum(1 for r in ratings if r == 3),
                "2_star": sum(1 for r in ratings if r == 2),
                "1_star": sum(1 for r in ratings if r == 1),
            },
            "calculated_metrics": {
                "precision_at_5": precision_at_5,
                "recall_at_5": recall_at_5,
                "f1_score": calculate_f1_score(precision_at_5, recall_at_5),
            },
        }
    except Exception as e:
        logger.error(f"Accuracy metrics error: {e}")
        return {"error": str(e)}


def get_system_performance(days: int = 30) -> dict:
    """Calculate system performance metrics from the application log."""
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "app.log")
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    pattern = re.compile(
        r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\|\s(?P<status>\d{3})\s\|\s(?P<latency>[\d.]+)ms"
    )
    latencies = []
    status_codes = []

    try:
        if not os.path.exists(log_path):
            return {
                "period_days": days,
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "success_rate_pct": 0,
                "requests_per_day": 0,
                "sample_size": 0,
                "note": "Application log file not found",
            }

        with open(log_path, "r", encoding="utf-8", errors="ignore") as log_file:
            for line in log_file:
                match = pattern.search(line)
                if not match:
                    continue

                timestamp = datetime.strptime(match.group("ts"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                if timestamp < cutoff:
                    continue

                latencies.append(float(match.group("latency")))
                status_codes.append(int(match.group("status")))

        if not latencies:
            return {
                "period_days": days,
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "success_rate_pct": 0,
                "requests_per_day": 0,
                "sample_size": 0,
                "note": "No recent request logs available",
            }

        ordered = sorted(latencies)
        p95_index = max(0, min(len(ordered) - 1, int(len(ordered) * 0.95) - 1))
        successful = sum(1 for status in status_codes if 200 <= status < 400)

        return {
            "period_days": days,
            "avg_response_time_ms": round(sum(latencies) / len(latencies), 2),
            "p95_response_time_ms": round(ordered[p95_index], 2),
            "success_rate_pct": round((successful / len(status_codes)) * 100, 2),
            "requests_per_day": round(len(latencies) / max(days, 1), 2),
            "sample_size": len(latencies),
            "note": "Metrics calculated from logged requests",
        }
    except Exception as e:
        logger.error(f"System performance metrics error: {e}")
        return {"error": str(e)}


def get_security_feature_usage(user_id: Optional[int] = None, days: int = 30) -> dict:
    """Analyze cybersecurity feature engagement."""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        query = UserBehavior.query.filter(
            UserBehavior.timestamp >= cutoff,
            UserBehavior.action_type == "url_safety_check",
        )
        if user_id:
            query = query.filter_by(user_id=user_id)

        url_checks = query.all()

        phishing_detected = sum(
            1 for uc in url_checks if uc.action_data and "is_phishing" in str(uc.action_data)
        )

        return {
            "period_days": days,
            "total_url_checks": len(url_checks),
            "unique_users": len(set(uc.user_id for uc in url_checks)),
            "phishing_detected": phishing_detected,
            "avg_checks_per_user": round(
                len(url_checks) / max(1, len(set(uc.user_id for uc in url_checks))), 1
            ),
            "proposal_alignment": "Objective 5: Phishing detection API usage",
        }
    except Exception as e:
        logger.error(f"Security metrics error: {e}")
        return {"error": str(e)}
