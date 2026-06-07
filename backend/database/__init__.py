"""
Database Initialization Module
Exports all SQLAlchemy models for use in the application
Proposal Alignment: Facilities - PostgreSQL Database (SQLite fallback)
"""

from .models import (
    db,
    User,
    Favorite,
    MLFeedback,
    UserBehavior,
    CareerInteraction
)

__all__ = [
    'db',
    'User', 
    'Favorite',
    'MLFeedback',
    'UserBehavior',
    'CareerInteraction'
]