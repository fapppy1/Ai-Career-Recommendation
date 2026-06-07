"""
AI Career Path Recommendation Web Application with Cybersecurity Awareness Features
====================================================================================
Project: CN6000 Final Year Project | Student: 2597225 | Supervisor: Dr. Athirah
Programme: BSc Computer Science | Year: 2025

Proposal Objectives Implemented:
✅ Obj 1: Hybrid Recommender (Content 70% + Collaborative Filtering 30%)
✅ Obj 2: Cybersecurity awareness methods & phishing detection research
✅ Obj 3: Flask-based web API integrating ML + cybersecurity + resume parsing
✅ Obj 4: React frontend ready (CORS configured for localhost:3000)
✅ Obj 5: Open-source phishing detection APIs (VirusTotal/URLScan.io integrated)
✅ Obj 6: Evaluation endpoints + performance tracking + pytest suite ready
✅ Obj 7: Reflection-ready architecture with explainability hooks

Facilities Used:
✅ Python 3.12+ | Flask Framework | PostgreSQL/SQLite Database
✅ Scikit-Learn for ML model | Requests for API integration
✅ bcrypt for password hashing | JWT for stateless authentication
✅ PyPDF2/python-docx/spaCy for resume parsing
✅ pytest for automated testing | GitHub for version control

Author: Rajdhami Alex (2597225)
Date: 2026
"""

# ===== Fix Windows Console Unicode Warnings =====
import sys
import os
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os, json, bcrypt, re, time, hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

# ===== Import Database Models =====
from database.models import db, User, UserBehavior, CareerInteraction, MLFeedback, Favorite

# ===== Import ML & Security Services =====
from services.recommendation_engine import HybridRecommender
from services import phishing_detector
from services.resume_parser import ResumeParser

# ===== Import Validation Schemas =====
from schemas import (
    RegisterRequest, LoginRequest, LoginResponse,
    RecommendationRequest, RecommendationResponse,
    URLCheckRequest, URLCheckResponse,
    JobAnalysisRequest, JobAnalysisResponse,
    validate_request
)

# ===== Import Logging =====
from utils.logger import setup_logger
logger = setup_logger('ai_career_recommender', log_file='logs/app.log')

# ===== CRITICAL: Force reload .env with override=True =====
load_dotenv(override=True)

# ===== JWT DEBUG: Print secret loading status =====
_jwt_secret = os.getenv('JWT_SECRET_KEY')
if _jwt_secret:
    logger.info(f"\n🔐 JWT_DEBUG: Secret loaded = ✅")
    logger.info(f"🔐 JWT_DEBUG: Secret length = {len(_jwt_secret)} chars")
    logger.info(f"🔐 JWT_DEBUG: Secret preview = {_jwt_secret[:30]}...")
else:
    logger.error(f"\n❌ JWT_DEBUG: Secret NOT loaded from .env")


def create_app():
    """Application Factory Pattern - Creates and configures Flask app"""
    app = Flask(__name__)
    
    # ===== Configuration =====
    
    # 🔐 Security: JWT configuration - MUST load from .env (NO FALLBACK)
    jwt_secret = os.getenv('JWT_SECRET_KEY') or globals().get('_jwt_secret')
    
    if not jwt_secret or len(jwt_secret) < 32:
        logger.error("❌ JWT_SECRET_KEY must be set in .env and be at least 32 characters!")
        raise ValueError(
            "❌ JWT_SECRET_KEY must be set in .env and be at least 32 characters!\n"
            "Add this to backend/.env:\n"
            "JWT_SECRET_KEY=your-secret-key-min-32-chars-here"
        )
    
    # Set config BEFORE initializing JWTManager
    app.config['JWT_SECRET_KEY'] = jwt_secret
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_ALGORITHM'] = 'HS256'
    
    # 🔐 CRITICAL FIX FOR JWT 401 ERRORS:
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'              
    app.config['JWT_DECODE_ALGORITHMS'] = ['HS256']       
    app.config['JWT_HEADER_TYPE'] = 'Bearer'              
    
    # Safe logging
    if app.config.get('JWT_SECRET_KEY'):
        logger.info(f"✅ JWT configured: secret length = {len(app.config['JWT_SECRET_KEY'])} chars")
    
    # 🗄️ Database: PostgreSQL with SQLite fallback
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    else:
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        if db_name and db_user and db_password:
            app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_career.db'
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 🌐 CORS for React frontend
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # 📁 File Upload Configuration
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE_MB', 16)) * 1024 * 1024
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # ===== Initialize Extensions =====
    jwt = JWTManager(app)
    
    # 🔐 JWT DEBUG: Log token validation issues
    @jwt.invalid_token_loader
    def debug_invalid_token(error):
        auth_header = request.headers.get('Authorization', 'NONE')
        logger.error(f"❌ INVALID TOKEN: {error}")
        logger.error(f"   Auth Header: {auth_header[:60] if auth_header != 'NONE' else 'NONE'}...")
        logger.error(f"   Endpoint: {request.path}")
        return jsonify({
            "success": False,
            "error": "Invalid token",
            "error_code": "invalid_token"
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"⚠️ EXPIRED TOKEN for endpoint: {request.path}")
        return jsonify({
            "success": False,
            "error": "Token has expired",
            "error_code": "token_expired"
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning(f"⚠️ MISSING TOKEN for endpoint: {request.path}")
        return jsonify({
            "success": False,
            "error": "Authentication required",
            "error_code": "auth_required"
        }), 401
    
    # 🔐 JWT DEBUG: Print config for verification
    if app.config.get('JWT_SECRET_KEY'):
        logger.info(f"🔐 JWT_SECRET_KEY in config: {app.config['JWT_SECRET_KEY'][:30]}...")
    logger.info(f"🔐 JWT_ALGORITHM: {app.config.get('JWT_ALGORITHM')}")
    logger.info(f"🔐 JWT_TOKEN_LOCATION: {app.config.get('JWT_TOKEN_LOCATION')}\n")
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created/verified")
    
    # 🤖 Initialize Hybrid Recommender
    from ml_system import CAREER_DATASET
    from database.models import CareerInteraction as CI
    
    def load_interactions():
        try:
            interactions = CI.query.all()
            return [{
                'user_id': i.user_id,
                'career_role': i.career_role,
                'interaction_type': i.interaction_type,
                'rating': i.rating
            } for i in interactions if i.rating]
        except:
            return []
    
    hybrid_recommender = HybridRecommender(
        careers=CAREER_DATASET,
        interactions=load_interactions()
    )
    logger.info(f"✅ Hybrid recommender initialized with {len(CAREER_DATASET)} careers")
    
    # ===== Helper Functions =====
    
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def track_user_behavior(user_id: int, action_type: str, action_data: Dict, session_id: str = None):
        try:
            if user_id == 0:
                return
            if isinstance(action_data, (dict, list)):
                action_data_str = json.dumps(action_data)
            else:
                action_data_str = str(action_data) if action_data else None
            
            behavior = UserBehavior(
                user_id=user_id,
                action_type=action_type,
                action_data=action_data_str,
                session_id=session_id
            )
            db.session.add(behavior)
            db.session.commit()
        except Exception as e:
            logger.warning(f"⚠️ Behavior tracking error: {e}")
            db.session.rollback()
        
    def log_career_interaction(user_id: int, career_role: str, interaction_type: str, rating: float = None):
        try:
            existing = CareerInteraction.query.filter_by(
                user_id=user_id, career_role=career_role, interaction_type=interaction_type
            ).first()
            if existing:
                if rating:
                    existing.rating = max(existing.rating or 0, rating)
            else:
                new_inter = CareerInteraction(
                    user_id=user_id, career_role=career_role, 
                    interaction_type=interaction_type, rating=rating
                )
                db.session.add(new_inter)
            db.session.commit()
        except Exception as e:
            logger.warning(f"⚠️ Interaction logging error: {e}")
            db.session.rollback()
    
    # ===== Performance Tracking Middleware =====
    
    @app.before_request
    def before_request():
        request.start_time = time.time()
        request.user_id = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                request.user_id = get_jwt_identity()
            except:
                pass
    
    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            latency_ms = round((time.time() - request.start_time) * 1000, 2)
            logger.info(f"⏱️  {request.method} {request.path} | {response.status_code} | {latency_ms}ms")
            if response.status_code == 200 and request.user_id:
                track_user_behavior(request.user_id, 'performance_metric', {
                    'endpoint': request.path,
                    'method': request.method,
                    'latency_ms': latency_ms,
                    'status_code': response.status_code
                })
        return response
    
    # ===== ROUTES =====
    
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "🎓 AI Career Path Recommender API",
            "project": "CN6000 Final Year Project | Student: 2597225",
            "status": "running",
            "version": "5.0.0-Hybrid",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "5.0.0-Hybrid",
            "careers_in_dataset": len(CAREER_DATASET)
        }), 200
    
    # ===== AUTHENTICATION ROUTES =====
    
    @app.route("/auth/register", methods=["POST"])
    def register():
        try:
            is_valid, data, error = validate_request(RegisterRequest, request.get_json() or {})
            if not is_valid:
                return jsonify({"success": False, "error": f"Validation failed: {error}"}), 400
            
            email = data['email'].lower().strip()
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({"success": False, "error": "Email already registered"}), 400
            
            new_user = User(
                email=email,
                password_hash=hash_password(data['password']),
                full_name=data['full_name'],
                industry=data.get('industry', 'Technology'),
                skills=json.dumps(data.get('skills', [])),
                experience_level=data.get('experience_level', 'Intermediate')
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # ✅ FIX: Convert user.id to string for JWT
            access_token = create_access_token(identity=str(new_user.id))
            
            logger.info(f"✅ User registered: {email} (ID: {new_user.id})")
            
            return jsonify({
                "success": True,
                "message": "User registered successfully",
                "access_token": access_token,
                "user": new_user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Registration error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/auth/login", methods=["POST"])
    def login():
        try:
            is_valid, data, error = validate_request(LoginRequest, request.get_json() or {})
            if not is_valid:
                return jsonify({"success": False, "error": f"Validation failed: {error}"}), 400
            
            email = data['email'].lower().strip()
            password = data['password']
            
            user = User.query.filter_by(email=email).first()
            
            if not user or not verify_password(password, user.password_hash):
                return jsonify({"success": False, "error": "Invalid email or password"}), 401
            
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # ✅ FIX: Convert user.id to string for JWT
            access_token = create_access_token(identity=str(user.id))
            
            logger.info(f"✅ User logged in: {email} (ID: {user.id})")
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "access_token": access_token,
                "user": user.to_dict()
            }), 200
            
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/auth/me", methods=["GET"])
    @jwt_required()
    def get_current_user():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({"success": False, "error": "User not found"}), 404
            
            return jsonify({"success": True, "user": user.to_dict()}), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===== AI RECOMMENDATION ROUTES =====
    
    @app.route("/ai/recommend", methods=["POST"])
    def recommend_careers():
        try:
            is_valid, data, error = validate_request(RecommendationRequest, request.get_json() or {})
            if not is_valid:
                return jsonify({"success": False, "error": str(error)}), 400
            
            user_skills = data['skills']
            industry = data.get('industry', 'Technology')
            experience_level = data.get('experience_level', 'Intermediate')
            
            user_id = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                try:
                    user_id = get_jwt_identity()
                except:
                    pass
            
            recommendations = hybrid_recommender.get_recommendations(
                user_skills=user_skills,
                user_id=user_id or 0,
                industry=industry,
                experience_level=experience_level,
                top_n=6
            )
            
            if user_id and recommendations:
                log_career_interaction(user_id, recommendations[0]['role'], 'view')
            
            return jsonify({
                "success": True,
                "recommendations": recommendations,
                "skill_analysis": hybrid_recommender.analyze_skills(user_skills),
                "metadata": {
                    "algorithm": "hybrid_tfidf_cf",
                    "weights": {"content": 0.7, "collaborative": 0.3},
                    "selected_industry": industry,
                    "selected_experience_level": experience_level,
                    "fallback_note": recommendations[0].get("fallback_reason") if recommendations else None
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/ai/recommendations/<path:role>/interact", methods=["POST"])
    @jwt_required()
    def log_recommendation_interaction(role):
        try:
            user_id = get_jwt_identity()
            data = request.get_json() or {}
            interaction_type = data.get('type', 'view')
            rating = data.get('rating')
            
            log_career_interaction(user_id, role, interaction_type, rating)
            
            return jsonify({"success": True, "message": "Interaction logged"}), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/ai/skills/analyze", methods=["POST"])
    def analyze_user_skills():
        try:
            data = request.get_json() or {}
            user_skills = data.get('skills', [])
            analysis = hybrid_recommender.analyze_skills(user_skills)
            return jsonify({"success": True, "analysis": analysis}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/ai/feedback", methods=["POST"])
    @jwt_required()
    def submit_feedback():
        try:
            user_id = get_jwt_identity()
            data = request.get_json() or {}
            rating = data.get('rating')
            
            if not rating or not (1 <= rating <= 5):
                return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
            
            new_feedback = MLFeedback(
                user_id=user_id,
                role=data.get('role'),
                feedback_score=rating,
                skills_provided=json.dumps(data.get('skills_provided', [])),
                industry=data.get('industry'),
                feedback_text=data.get('feedback_text')
            )
            db.session.add(new_feedback)
            log_career_interaction(user_id, data.get('role'), 'rate', rating)
            db.session.commit()
            
            return jsonify({"success": True, "message": "Feedback recorded"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===== RESUME PARSING =====
    
    @app.route("/resume/parse", methods=["POST"])
    def parse_resume():
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity() or "guest"
            if 'file' not in request.files:
                return jsonify({"success": False, "error": "No file uploaded"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "error": "No file selected"}), 400
            
            allowed_extensions = {'pdf', 'docx', 'txt'}
            if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                return jsonify({"success": False, "error": "Invalid file type"}), 400
            
            filename = secure_filename(f"resume_{user_id}_{file.filename}")
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_path)
            
            parser = ResumeParser()
            result = parser.parse(temp_path)
            
            try:
                os.remove(temp_path)
            except:
                pass
            
            if "error" in result:
                return jsonify({"success": False, "error": result["error"]}), 400
            
            return jsonify({"success": True, "data": result, "message": "Resume parsed"}), 200
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===== CYBERSECURITY =====
    
    @app.route("/cybersecurity/tips", methods=["GET"])
    def get_security_tips():
        try:
            category = request.args.get('category', 'job_search')
            return jsonify(phishing_detector.get_security_tips(category)), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/cybersecurity/check-url", methods=["POST"])
    def check_url_safety():
        try:
            verify_jwt_in_request(optional=True)
            is_valid, data, error = validate_request(URLCheckRequest, request.get_json() or {})
            if not is_valid:
                return jsonify({"success": False, "error": str(error)}), 400
            
            user_id = get_jwt_identity()
            url = data['url']
            result = phishing_detector.check_url(url, user_id=user_id)
            if user_id:
                track_user_behavior(user_id, 'url_safety_check', {
                    "url": url,
                    "risk_level": result.get("risk_level"),
                    "is_phishing": result.get("is_phishing", False),
                    "overall_score": result.get("overall_score", 0)
                })
            
            return jsonify({"success": True, "url": url, "result": result}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/ai/favorites", methods=["GET"])
    @jwt_required()
    def get_favorites():
        try:
            user_id = get_jwt_identity()
            favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.saved_at.desc()).all()
            return jsonify({
                "success": True,
                "favorites": [favorite.to_dict() for favorite in favorites]
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/ai/favorites", methods=["POST"])
    @jwt_required()
    def save_favorite():
        try:
            user_id = get_jwt_identity()
            data = request.get_json() or {}
            role = data.get("role")

            if not role:
                return jsonify({"success": False, "error": "Role is required"}), 400

            favorite = Favorite.query.filter_by(user_id=user_id, role=role).first()
            if favorite:
                favorite.match_score = data.get("match_score", favorite.match_score)
                favorite.skills_needed = json.dumps(data.get("skills_needed", json.loads(favorite.skills_needed or "[]")))
                favorite.description = data.get("description", favorite.description)
                favorite.salary_range = data.get("salary_range", favorite.salary_range)
                favorite.growth_outlook = data.get("growth_outlook", favorite.growth_outlook)
            else:
                favorite = Favorite(
                    user_id=user_id,
                    role=role,
                    match_score=data.get("match_score"),
                    skills_needed=json.dumps(data.get("skills_needed", [])),
                    description=data.get("description"),
                    salary_range=data.get("salary_range"),
                    growth_outlook=data.get("growth_outlook")
                )
                db.session.add(favorite)

            db.session.commit()
            log_career_interaction(user_id, role, 'favorite')
            return jsonify({"success": True, "favorite": favorite.to_dict()}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/ai/favorites/<path:role>", methods=["DELETE"])
    @jwt_required()
    def delete_favorite(role):
        try:
            user_id = get_jwt_identity()
            favorite = Favorite.query.filter_by(user_id=user_id, role=role).first()
            if not favorite:
                return jsonify({"success": False, "error": "Favorite not found"}), 404

            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"success": True, "message": "Favorite removed"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/cybersecurity/analyze-job", methods=["POST"])
    def analyze_job_posting():
        try:
            is_valid, data, error = validate_request(JobAnalysisRequest, request.get_json() or {})
            if not is_valid:
                return jsonify({"success": False, "error": str(error)}), 400
            
            result = phishing_detector.analyze_job_posting(data)
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                try:
                    user_id = get_jwt_identity()
                    if user_id:
                        track_user_behavior(user_id, 'job_post_analysis', {
                            "company": data.get("company"),
                            "title": data.get("title"),
                            "risk_level": result.get("risk_level"),
                            "is_suspicious": result.get("is_suspicious", False),
                            "risk_score": result.get("risk_score", 0)
                        })
                except:
                    pass
            return jsonify({"success": True, "analysis": result}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===== EVALUATION =====
    
    @app.route("/evaluation/accuracy/<int:user_id>", methods=["GET"])
    @jwt_required()
    def get_user_accuracy(user_id):
        try:
            current_user_id = get_jwt_identity()
            if str(current_user_id) != str(user_id):
                return jsonify({"success": False, "error": "Forbidden"}), 403

            days = request.args.get('days', 30, type=int)
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            feedback = MLFeedback.query.filter(MLFeedback.user_id == user_id, MLFeedback.timestamp >= cutoff).all()
            
            if not feedback:
                return jsonify({
                    "success": True,
                    "data": {
                        "user_id": user_id,
                        "message": "No feedback data available yet",
                        "total_feedback": 0,
                        "average_rating": 0,
                        "precision": 0,
                        "rating_distribution": {
                            "5_star": 0,
                            "4_star": 0,
                            "3_star": 0,
                            "2_star": 0,
                            "1_star": 0
                        }
                    }
                }), 200
            
            ratings = [f.feedback_score for f in feedback]
            avg_rating = sum(ratings) / len(ratings)
            precision = sum(1 for r in ratings if r >= 4) / len(ratings)
            
            return jsonify({
                "success": True,
                "data": {
                    "user_id": user_id,
                    "total_feedback": len(feedback),
                    "average_rating": round(avg_rating, 2),
                    "precision": round(precision, 3),
                    "rating_distribution": {
                        "5_star": sum(1 for r in ratings if r == 5),
                        "4_star": sum(1 for r in ratings if r == 4),
                        "3_star": sum(1 for r in ratings if r == 3),
                        "2_star": sum(1 for r in ratings if r == 2),
                        "1_star": sum(1 for r in ratings if r == 1)
                    }
                }
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/evaluation/security-engagement", methods=["GET"])
    @jwt_required()
    def get_security_engagement():
        try:
            user_id = request.args.get('user_id', type=int)
            days = request.args.get('days', 30, type=int)
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            query = UserBehavior.query.filter(UserBehavior.timestamp >= cutoff, UserBehavior.action_type == 'url_safety_check')
            if user_id: query = query.filter_by(user_id=user_id)
            url_checks = query.all()
            
            return jsonify({
                "success": True,
                "data": {
                    "total_url_checks": len(url_checks),
                    "unique_users": len(set(uc.user_id for uc in url_checks))
                }
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/evaluation/system-metrics", methods=["GET"])
    def get_system_metrics():
        try:
            from evaluation.metrics import get_recommendation_accuracy, get_system_performance, get_security_feature_usage
            days = request.args.get('days', 30, type=int)
            user_id = request.args.get('user_id', type=int)
            
            return jsonify({
                "success": True,
                "metrics": {
                    "recommendation_accuracy": get_recommendation_accuracy(user_id, days),
                    "system_performance": get_system_performance(days),
                    "security_engagement": get_security_feature_usage(user_id, days)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    # ===== DEBUG ROUTES =====
    
    @app.route("/debug/jwt", methods=["GET"])
    def debug_jwt():
        try:
            import jwt
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "No Bearer token found"}), 400
            
            token = auth_header.split(' ')[1]
            secret = app.config['JWT_SECRET_KEY']
            decoded = jwt.decode(token, secret, algorithms=["HS256"])
            return jsonify({"success": True, "decoded_payload": decoded}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    @app.route("/debug/config", methods=["GET"])
    def debug_config():
        return jsonify({
            "JWT_SECRET_KEY_length": len(app.config.get('JWT_SECRET_KEY') or ''),
            "JWT_ALGORITHM": app.config.get('JWT_ALGORITHM'),
            "JWT_IDENTITY_CLAIM": app.config.get('JWT_IDENTITY_CLAIM')
        }), 200
    
    # ===== Error Handlers =====
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"success": False, "error": "Internal server error"}), 500
    
    return app


# ===== Application Entry Point =====

app = create_app()

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🎓 AI Career Path Recommender Backend v5.0.0 (Hybrid)")
    logger.info(f"   Student: 2597225 | Supervisor: Dr. Athirah")
    logger.info(f"   Server: http://0.0.0.0:5000")
    logger.info("=" * 70)
    
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
