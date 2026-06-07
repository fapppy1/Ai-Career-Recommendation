"""
SQLAlchemy Database Models
Aligned with Proposal: PostgreSQL Database (SQLite fallback for development)
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), default='Technology')
    skills = db.Column(db.Text, default='[]')  # JSON string
    experience_level = db.Column(db.String(20), default='Intermediate')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert user to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'industry': self.industry,
            'skills': json.loads(self.skills) if self.skills else [],
            'experience_level': self.experience_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Favorite(db.Model):
    __tablename__ = 'user_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    match_score = db.Column(db.Float)
    skills_needed = db.Column(db.Text, default='[]')
    description = db.Column(db.Text)
    salary_range = db.Column(db.String(50))
    growth_outlook = db.Column(db.String(20))
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role', name='uq_user_role'),
    )
    
    def to_dict(self):
        return {
            'role': self.role,
            'match_score': self.match_score,
            'skills_needed': json.loads(self.skills_needed) if self.skills_needed else [],
            'description': self.description,
            'salary_range': self.salary_range,
            'growth_outlook': self.growth_outlook,
            'saved_at': self.saved_at.isoformat()
        }

class MLFeedback(db.Model):
    __tablename__ = 'ml_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    feedback_score = db.Column(db.Integer, db.CheckConstraint('feedback_score BETWEEN 1 AND 5'))
    skills_provided = db.Column(db.Text, default='[]')
    industry = db.Column(db.String(50))
    feedback_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserBehavior(db.Model):
    """
    Tracks user actions for analytics and evaluation
    Proposal Alignment: Objective 6 - evaluation through testing
    """
    __tablename__ = 'user_behavior'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), index=True)  # e.g., 'register', 'login', 'recommendation_request'
    action_data = db.Column(db.Text)  # JSON string with action details
    session_id = db.Column(db.String(100), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'action_data': json.loads(self.action_data) if self.action_data else {},
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat()
        }

class CareerInteraction(db.Model):
    """
    Tracks user-career interactions for collaborative filtering
    Proposal Alignment: Objective 1 - recommendation algorithm research
    """
    __tablename__ = 'career_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    career_role = db.Column(db.String(100), nullable=False, index=True)
    interaction_type = db.Column(db.String(20))  # 'viewed', 'favorited', 'rated'
    rating = db.Column(db.Float)  # Explicit rating 1-5 if provided
    skills_matched = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'career_role', 'interaction_type'),
    )