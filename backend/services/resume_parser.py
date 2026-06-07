"""
Resume/CV Parser Service
Proposal Alignment: Objective 3 - ML engine integration for user personalization
Extracts skills, experience, and education from PDF/DOCX/TXT uploads
"""
import os, re, json, tempfile
from typing import Dict
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
import spacy

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        self.skill_patterns = {
            "programming": ["python", "javascript", "java", "c++", "sql", "r", "typescript"],
            "ml_frameworks": ["tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy"],
            "cloud_devops": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "ci/cd", "terraform"],
            "security": ["network security", "risk assessment", "penetration testing", "siem", "compliance", "gdpr"],
            "soft_skills": ["communication", "leadership", "problem solving", "agile", "scrum", "project management", "teamwork"],
            "healthcare_support": ["first aid", "patient care", "health and safety", "health safety", "documentation", "microsoft office", "microsoft word"]
        }

    def extract_text(self, file_path: str) -> str:
        ext = file_path.rsplit('.', 1)[1].lower()
        text = ""
        try:
            if ext == 'pdf':
                for page in PdfReader(file_path).pages: text += page.extract_text() or ""
            elif ext == 'docx':
                doc = Document(file_path)
                text = "\n".join(p.text for p in doc.paragraphs)
            else:
                with open(file_path, 'r', encoding='utf-8') as f: text = f.read()
        except Exception as e:
            print(f"Text extraction error: {e}")
        return text

    def parse(self, file_path: str) -> Dict:
        text = self.extract_text(file_path).lower()
        if not text: return {"error": "Could not extract text from file"}

        skills_found = []
        for category, keywords in self.skill_patterns.items():
            matched = [kw.title() for kw in keywords if re.search(rf'\b{re.escape(kw)}\b', text)]
            if matched: skills_found.append({"category": category, "skills": matched})

        # Basic experience/education extraction
        exp_years = len(re.findall(r'\d+\s*years?', text))
        edu_matches = [m.group() for m in re.finditer(r'(bachelor|master|phd|diploma).*?(university|college|institute)', text, re.I)]
        
        # NER fallback if spaCy loaded
        entities = []
        if self.nlp:
            doc = self.nlp(text)
            entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents if ent.label_ in ["ORG", "DATE", "PRODUCT"]]

        return {
            "skills": skills_found,
            "all_skills_flat": [s for cat in skills_found for s in cat["skills"]],
            "estimated_experience_years": max(1, exp_years) if exp_years else None,
            "education_highlights": edu_matches[:3],
            "key_entities": entities[:10],
            "text_preview": text[:300] + "..." if len(text) > 300 else text
        }
