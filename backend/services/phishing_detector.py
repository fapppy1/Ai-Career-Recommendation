"""
Phishing Detection Service with Real API Integration
Proposal Alignment: Objective 5 - Open-source phishing detection APIs
"""
import os, re, hashlib, time, requests, base64
from urllib.parse import urlparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class PhishingDetector:
    def __init__(self):
        self.vt_api_key = os.getenv('VIRUSTOTAL_API_KEY', '')
        self.urlscan_api_key = os.getenv('URLSCAN_API_KEY', '')
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(hours=24)
        
        self.indicators = {
            'suspicious_keywords': ['login', 'verify', 'account', 'secure', 'update', 'confirm', 'signin', 'password', 'urgent', 'claim'],
            'suspicious_tlds': ['.tk', '.ml', '.ga', '.cf', '.xyz', '.top', '.club', '.work', '.click', '.link', '.invalid'],
            'brand_mimics': ['paypal', 'amazon', 'linkedin', 'indeed', 'glassdoor', 'upwork', 'fiverr', 'monster']
        }

    def _check_rate_limit(self, status_code: int, retries: int = 2) -> bool:
        """Handle API rate limits gracefully"""
        if status_code == 429 and retries > 0:
            time.sleep(60)  # VT free tier: 1 req/min
            return True
        return False

    def check_url_virustotal(self, url: str) -> Optional[Dict]:
        if not self.vt_api_key: return None
        try:
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            headers = {"x-apikey": self.vt_api_key}
            
            for _ in range(3):
                res = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=15)
                if res.status_code == 429:
                    time.sleep(60); continue
                if res.status_code == 200:
                    data = res.json().get('data', {}).get('attributes', {})
                    stats = data.get('last_analysis_stats', {})
                    return {
                        "source": "virustotal",
                        "malicious": stats.get('malicious', 0),
                        "suspicious": stats.get('suspicious', 0),
                        "is_malicious": stats.get('malicious', 0) > 0,
                        "reputation": data.get('reputation', 0)
                    }
                return None
        except Exception as e:
            print(f"VirusTotal API error: {e}")
        return None

    def check_url_urlscan(self, url: str) -> Optional[Dict]:
        if not self.urlscan_api_key: return None
        try:
            headers = {"API-Key": self.urlscan_api_key}
            res = requests.get(f"https://urlscan.io/api/v1/search/?q=page.url:{url}", headers=headers, timeout=15)
            if res.status_code == 200:
                results = res.json().get('results', [])
                if results:
                    v = results[0].get('verdicts', {})
                    return {
                        "source": "urlscan",
                        "malicious": v.get('malicious', False),
                        "suspicious": v.get('suspicious', False),
                        "phishing": v.get('phishing', False),
                        "score": v.get('score', 0)
                    }
        except Exception as e:
            print(f"URLScan.io API error: {e}")
        return None

    def analyze_url_pattern(self, url: str) -> Dict:
        parsed = urlparse(url)
        domain, path = parsed.netloc.lower(), parsed.path.lower()
        indicators, score = [], 0
        
        for kw in self.indicators['suspicious_keywords']:
            if kw in domain or kw in path:
                indicators.append(f"Suspicious keyword: {kw}"); score += 15
        for tld in self.indicators['suspicious_tlds']:
            if domain.endswith(tld):
                indicators.append(f"High-risk TLD: {tld}"); score += 20; break
        for brand in self.indicators['brand_mimics']:
            if brand in domain and not any(domain.endswith(f"{brand}.{ext}") for ext in ['com','co.uk','org','net']):
                indicators.append(f"Possible '{brand}' impersonation"); score += 35; break
        if domain.count('-') >= 2:
            indicators.append("Multiple hyphens in domain"); score += 10
        if len(url) > 100: indicators.append("Unusually long URL"); score += 10
        if re.match(r'\d+\.\d+\.\d+\.\d+', domain): indicators.append("IP address used"); score += 30
        if parsed.scheme != 'https' and any(k in url.lower() for k in ['login','account']):
            indicators.append("No HTTPS for sensitive page"); score += 25
            
        return {"is_suspicious": score >= 50, "risk_score": min(score, 100), "indicators": indicators}

    def check_url(self, url: str, user_id: Optional[int] = None) -> Dict:
        if not url: return {"success": False, "error": "URL required", "is_safe": False}
        url = url.strip()
        if not url.startswith(('http://', 'https://')): url = 'https://' + url
        
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self.cache and datetime.now() - self.cache[cache_key]['timestamp'] < self.cache_ttl:
            return {**self.cache[cache_key]['result'], "cached": True}

        results = {"success": True, "url": url, "timestamp": datetime.now().isoformat(), 
                   "is_phishing": False, "is_safe": True, "overall_score": 0, "risk_level": "unknown",
                   "indicators": [], "api_results": {}, "recommendations": [], "cached": False}

        # Heuristic analysis (always runs)
        pattern = self.analyze_url_pattern(url)
        results["overall_score"] += pattern["risk_score"]
        results["indicators"].extend(pattern["indicators"])

        # API checks (with fallback)
        vt = self.check_url_virustotal(url)
        if vt:
            results["api_results"]["virustotal"] = vt
            if vt["is_malicious"]: results["overall_score"] += 40; results["indicators"].append(f"VT: {vt['malicious']} engines flagged malicious")
            
        us = self.check_url_urlscan(url)
        if us:
            results["api_results"]["urlscan"] = us
            if us.get("malicious") or us.get("phishing"): results["overall_score"] += 45; results["indicators"].append("URLScan: Confirmed malicious/phishing")

        # Final assessment
        score = results["overall_score"]
        if score >= 70:
            results.update({"is_phishing": True, "is_safe": False, "risk_level": "critical",
                           "message": "🚨 CRITICAL: Confirmed phishing/malicious",
                           "recommendations": ["🛑 DO NOT click", "🔍 Verify official site", "📧 Report to report@phishing.gov.uk"]})
        elif score >= 50:
            results.update({"is_phishing": True, "is_safe": False, "risk_level": "high",
                           "message": "⚠️ HIGH RISK: Strong phishing indicators",
                           "recommendations": ["⚠️ Extreme caution", "🔎 Verify sender independently", "🌐 Check official career page"]})
        elif score >= 30:
            results.update({"is_phishing": False, "is_safe": False, "risk_level": "medium",
                           "message": "⚠️ MEDIUM RISK: Some suspicious patterns",
                           "recommendations": ["🔍 Verify through official channels", "🔐 Ensure HTTPS before data entry"]})
        else:
            results.update({"is_phishing": False, "is_safe": True, "risk_level": "low",
                           "message": "✅ LOW RISK: URL appears safe",
                           "recommendations": ["✅ URL appears safe", "🔐 Still verify company website"]})

        self.cache[cache_key] = {"timestamp": datetime.now(), "result": results}
        return results

    def analyze_job_posting(self, job_data: Dict) -> Dict:
        """
        Analyze job posting for fraud indicators
        Proposal Alignment: Objective 2 - Cybersecurity awareness methods
        """
        if not job_data:
            return {"error": "No job data provided", "is_suspicious": False, "risk_level": "unknown"}
        
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        salary = job_data.get('salary', '').lower()
        company = job_data.get('company', '').lower()
        contact_email = job_data.get('contact_email', '').lower()
        
        red_flags = []
        green_flags = []
        risk_score = 0
        
        # Check for urgency indicators
        urgency_words = ['urgent', 'immediate', 'asap', 'quick', 'fast', 'now']
        if any(word in description for word in urgency_words):
            red_flags.append("Urgency language detected ('immediate hiring', 'act now')")
            risk_score += 20
        
        # Check for unrealistic salary
        if salary:
            try:
                # Look for very high salaries for entry-level positions
                if any(phrase in salary for phrase in ['$5000', '$10000', '£5000', '£10000', 'per week', 'weekly']):
                    if 'entry' in title or 'junior' in title or 'no experience' in description:
                        red_flags.append("Unrealistically high salary for entry-level position")
                        risk_score += 30
            except:
                pass
        
        # Check for vague job description
        if len(description) < 100:
            red_flags.append("Very short job description (potential scam)")
            risk_score += 15
        
        # Check for generic email domains
        if contact_email:
            generic_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            if any(domain in contact_email for domain in generic_domains):
                red_flags.append(f"Contact email uses generic domain ({contact_email})")
                risk_score += 25
            else:
                green_flags.append("Professional company email domain")
        
        # Check for work-from-home + no experience
        if 'remote' in description or 'work from home' in description:
            if 'no experience' in description or 'no skills' in description:
                red_flags.append("Remote work with no experience required (common scam pattern)")
                risk_score += 25
        
        # Check for requests for personal information
        personal_info_words = ['bank details', 'social security', 'national insurance', 'passport', 'id card']
        if any(word in description for word in personal_info_words):
            red_flags.append("Requests personal/financial information upfront")
            risk_score += 35
        
        # Check for company information
        if company and len(company) > 3:
            green_flags.append(f"Company name provided: {company}")
        else:
            red_flags.append("No company name provided")
            risk_score += 10
        
        # Check for professional language
        if description and len(description) > 200:
            green_flags.append("Detailed job description provided")
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = "high"
            is_suspicious = True
            message = "⚠️ HIGH RISK: Multiple fraud indicators detected"
        elif risk_score >= 30:
            risk_level = "medium"
            is_suspicious = True
            message = "⚠️ MEDIUM RISK: Some suspicious patterns"
        else:
            risk_level = "low"
            is_suspicious = False
            message = "✅ LOW RISK: Appears legitimate"
        
        # Add recommendations
        recommendations = []
        if is_suspicious:
            recommendations.append("🔍 Research company on LinkedIn/Glassdoor")
            recommendations.append("📧 Verify email domain matches company website")
            recommendations.append("🚫 Never share bank details upfront")
            recommendations.append("📞 Request phone interview with verified number")
        else:
            recommendations.append("✅ Still verify company legitimacy")
            recommendations.append("🔐 Use secure application methods")
        
        return {
            "is_suspicious": is_suspicious,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "message": message,
            "red_flags": red_flags,
            "green_flags": green_flags,
            "recommendations": recommendations
        }

    def get_security_tips(self, category: str = "job_search") -> Dict:
        tips = {
            "job_search": ["🔐 Verify postings on official company sites", "📧 Use dedicated job email", "🔍 Research on LinkedIn/Glassdoor", "⚠️ Beware of 'too good to be true' offers", "📱 Never share NI/bank details initially"],
            "phishing_awareness": ["🎣 Urgency = red flag", "🔗 Hover to preview links", "📧 Legit companies never ask passwords via email", "🔐 Enable 2FA on job portals", "🗑️ Report to report@phishing.gov.uk"],
            "data_privacy": ["📋 Minimal info in initial apps", "🔒 Ensure HTTPS + padlock", "🗄️ Keep application records", "🧹 Review privacy settings regularly", "🔐 Unique passwords per site"]
        }
        import random
        selected = tips.get(category, tips["job_search"])
        return {"success": True, "category": category, "tip": random.choice(selected), "all_tips": selected,
                "resources": {"report_phishing": "report@phishing.gov.uk", "action_fraud": "https://actionfraud.police.uk", "ncsc": "https://ncsc.gov.uk/phishing"}}


# ===== Singleton Instance =====
# Create a single instance for application-wide use
phishing_detector = PhishingDetector()
