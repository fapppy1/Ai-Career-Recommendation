"""
Career Dataset for AI Recommendations
Aligned with Proposal: Multi-industry career paths (Technology + Healthcare + Finance + Education)
"""

CAREER_DATASET = [
    # ===== TECHNOLOGY CAREERS =====
    {
        "role": "AI Engineer",
        "required_skills": ["Python", "TensorFlow", "Machine Learning", "Deep Learning", "PyTorch", "Data Analysis"],
        "industry": "Technology",
        "experience_level": "Expert",
        "salary_min": 60000,
        "salary_max": 100000,
        "growth": "Very High",
        "description": "Design, build, and deploy AI/ML models for production systems. Work with neural networks, NLP, and computer vision."
    },
    {
        "role": "Machine Learning Engineer",
        "required_skills": ["Python", "Scikit-Learn", "TensorFlow", "Data Pipelines", "MLOps", "Statistics"],
        "industry": "Technology",
        "experience_level": "Advanced",
        "salary_min": 65000,
        "salary_max": 105000,
        "growth": "Very High",
        "description": "Build scalable ML systems, optimize model performance, and deploy algorithms to production environments."
    },
    {
        "role": "Data Scientist",
        "required_skills": ["Python", "Statistics", "SQL", "Data Visualization", "Machine Learning", "Pandas"],
        "industry": "Technology",
        "experience_level": "Intermediate",
        "salary_min": 55000,
        "salary_max": 95000,
        "growth": "Very High",
        "description": "Extract insights from complex datasets using statistical analysis, ML, and visualization techniques."
    },
    {
        "role": "Cybersecurity Analyst",
        "required_skills": ["Network Security", "Risk Assessment", "Python", "SIEM Tools", "Incident Response", "Linux"],
        "industry": "Technology",
        "experience_level": "Advanced",
        "salary_min": 50000,
        "salary_max": 85000,
        "growth": "Very High",
        "description": "Protect organizational systems from cyber threats, monitor security events, and respond to incidents."
    },
    {
        "role": "Cloud Engineer",
        "required_skills": ["AWS", "Azure", "Docker", "Kubernetes", "Python", "Infrastructure as Code"],
        "industry": "Technology",
        "experience_level": "Advanced",
        "salary_min": 58000,
        "salary_max": 92000,
        "growth": "Very High",
        "description": "Design and manage cloud infrastructure, implement scalable solutions, and ensure system reliability."
    },
    {
        "role": "Full Stack Developer",
        "required_skills": ["JavaScript", "React", "Node.js", "Python", "SQL", "Git"],
        "industry": "Technology",
        "experience_level": "Beginner",
        "salary_min": 45000,
        "salary_max": 75000,
        "growth": "High",
        "description": "Build end-to-end web applications, working on both frontend interfaces and backend APIs."
    },
    {
        "role": "DevOps Engineer",
        "required_skills": ["CI/CD", "Docker", "Kubernetes", "Linux", "Python", "Monitoring Tools"],
        "industry": "Technology",
        "experience_level": "Advanced",
        "salary_min": 55000,
        "salary_max": 88000,
        "growth": "High",
        "description": "Bridge development and operations, automate deployments, and ensure system reliability and scalability."
    },
    {
        "role": "Data Engineer",
        "required_skills": ["Python", "SQL", "Apache Spark", "ETL", "Data Warehousing", "Cloud Platforms"],
        "industry": "Technology",
        "experience_level": "Intermediate",
        "salary_min": 52000,
        "salary_max": 85000,
        "growth": "Very High",
        "description": "Build and maintain data pipelines, ensure data quality, and enable analytics at scale."
    },
    
    # ===== HEALTHCARE CAREERS (NEW) =====
    {
        "role": "Healthcare Data Analyst",
        "required_skills": ["SQL", "Python", "Healthcare Analytics", "Data Visualization", "Excel", "Statistical Analysis"],
        "industry": "Healthcare",
        "experience_level": "Intermediate",
        "salary_min": 35000,
        "salary_max": 55000,
        "growth": "High",
        "description": "Analyze healthcare data to improve patient outcomes and operational efficiency. Work with electronic health records and clinical data."
    },
    {
        "role": "Health Information Technician",
        "required_skills": ["Medical Records", "HIPAA Compliance", "Database Management", "Attention to Detail", "Microsoft Office"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 28000,
        "salary_max": 42000,
        "growth": "Very High",
        "description": "Manage and organize patient health information systems. Ensure data accuracy and compliance with healthcare regulations."
    },
    {
        "role": "Clinical Data Coordinator",
        "required_skills": ["Clinical Research", "Data Management", "Communication", "Microsoft Office", "Regulatory Compliance", "Excel"],
        "industry": "Healthcare",
        "experience_level": "Intermediate",
        "salary_min": 32000,
        "salary_max": 48000,
        "growth": "High",
        "description": "Coordinate clinical trial data collection and management. Work with healthcare professionals to ensure data quality."
    },
    {
        "role": "Medical Records Specialist",
        "required_skills": ["Medical Terminology", "Database Management", "Communication", "Organization", "Confidentiality"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 25000,
        "salary_max": 38000,
        "growth": "High",
        "description": "Maintain and organize patient medical records. Ensure accuracy and compliance with healthcare privacy laws."
    },
    {
        "role": "Healthcare IT Support Specialist",
        "required_skills": ["IT Support", "Healthcare Systems", "Communication", "Problem Solving", "Microsoft Office", "Networking"],
        "industry": "Healthcare",
        "experience_level": "Intermediate",
        "salary_min": 30000,
        "salary_max": 45000,
        "growth": "Very High",
        "description": "Provide technical support for healthcare IT systems. Assist medical staff with software and hardware issues."
    },
    {
        "role": "Patient Care Coordinator",
        "required_skills": ["Communication", "Organization", "Microsoft Office", "Customer Service", "Healthcare Administration", "Team Work"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 26000,
        "salary_max": 40000,
        "growth": "High",
        "description": "Coordinate patient care services and appointments. Liaise between patients, families, and healthcare providers."
    },
    {
        "role": "Health Informatics Specialist",
        "required_skills": ["Health Informatics", "SQL", "Data Analysis", "Healthcare Systems", "Project Management", "Communication"],
        "industry": "Healthcare",
        "experience_level": "Advanced",
        "salary_min": 45000,
        "salary_max": 70000,
        "growth": "Very High",
        "description": "Bridge healthcare and technology by implementing health information systems and improving clinical workflows."
    },
    {
        "role": "Healthcare Administrative Assistant",
        "required_skills": ["Communication", "Microsoft Office", "Organization", "Documentation", "Healthcare Administration", "Team Work"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 24000,
        "salary_max": 36000,
        "growth": "High",
        "description": "Support daily healthcare office operations, maintain records, handle appointments, and communicate with patients and staff."
    },
    {
        "role": "Care Support Worker",
        "required_skills": ["Communication", "Patient Care", "First Aid", "Health Safety", "Team Work", "Documentation"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 22000,
        "salary_max": 32000,
        "growth": "High",
        "description": "Provide practical support to patients and care teams, follow safety procedures, and maintain clear care records."
    },
    {
        "role": "Ward Clerk",
        "required_skills": ["Communication", "Microsoft Office", "Documentation", "Organization", "Team Work", "Customer Service"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 23000,
        "salary_max": 34000,
        "growth": "Moderate",
        "description": "Handle ward administration tasks, update records, support staff communication, and help coordinate patient services."
    },
    {
        "role": "Healthcare Receptionist",
        "required_skills": ["Communication", "Customer Service", "Microsoft Office", "Healthcare Administration", "Organization", "Team Work"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 23000,
        "salary_max": 33000,
        "growth": "High",
        "description": "Welcome patients, manage appointments, maintain front-desk records, and support smooth communication in healthcare settings."
    },
    {
        "role": "Community Health Support Assistant",
        "required_skills": ["Communication", "Patient Care", "Health Safety", "Team Work", "Documentation", "Commitment"],
        "industry": "Healthcare",
        "experience_level": "Beginner",
        "salary_min": 24000,
        "salary_max": 35000,
        "growth": "High",
        "description": "Assist community health teams with patient support, safe working practices, record keeping, and service coordination."
    },
    
    # ===== FINANCE CAREERS =====
    {
        "role": "Financial Data Analyst",
        "required_skills": ["SQL", "Excel", "Python", "Financial Modeling", "Data Visualization", "Statistics"],
        "industry": "Finance",
        "experience_level": "Intermediate",
        "salary_min": 40000,
        "salary_max": 65000,
        "growth": "High",
        "description": "Analyze financial data to support investment decisions, risk assessment, and business strategy."
    },
    {
        "role": "FinTech Developer",
        "required_skills": ["Python", "JavaScript", "SQL", "Blockchain", "API Development", "Security"],
        "industry": "Finance",
        "experience_level": "Intermediate",
        "salary_min": 55000,
        "salary_max": 90000,
        "growth": "Very High",
        "description": "Build innovative financial technology solutions including payment systems, trading platforms, and blockchain applications."
    },

    # ===== E-COMMERCE CAREERS =====
    {
        "role": "E-commerce Executive",
        "required_skills": ["Communication", "Customer Service", "Microsoft Office", "Content Management", "Organization", "Team Work"],
        "industry": "E-commerce",
        "experience_level": "Beginner",
        "salary_min": 24000,
        "salary_max": 36000,
        "growth": "High",
        "description": "Support online store operations, product listings, customer queries, and day-to-day e-commerce administration."
    },
    {
        "role": "Digital Merchandising Assistant",
        "required_skills": ["Communication", "Microsoft Office", "Content Management", "Attention to Detail", "Team Work", "Customer Service"],
        "industry": "E-commerce",
        "experience_level": "Beginner",
        "salary_min": 25000,
        "salary_max": 38000,
        "growth": "High",
        "description": "Help manage digital product content, promotions, category pages, and merchandising activities for online retail."
    },
    {
        "role": "E-commerce Data Analyst",
        "required_skills": ["Excel", "SQL", "Data Analysis", "Data Visualization", "Communication", "Statistics"],
        "industry": "E-commerce",
        "experience_level": "Intermediate",
        "salary_min": 32000,
        "salary_max": 52000,
        "growth": "High",
        "description": "Analyze online sales and customer data to improve product performance, conversion rates, and business decisions."
    },
    
    # ===== EDUCATION CAREERS =====
    {
        "role": "Educational Technology Specialist",
        "required_skills": ["Instructional Design", "LMS Platforms", "Communication", "Project Management", "Basic Coding"],
        "industry": "Education",
        "experience_level": "Beginner",
        "salary_min": 35000,
        "salary_max": 52000,
        "growth": "High",
        "description": "Implement and support educational technology solutions to enhance teaching and learning experiences."
    },
    {
        "role": "Learning Analytics Specialist",
        "required_skills": ["Data Analysis", "SQL", "Python", "Educational Theory", "Statistics", "Visualization"],
        "industry": "Education",
        "experience_level": "Intermediate",
        "salary_min": 42000,
        "salary_max": 62000,
        "growth": "High",
        "description": "Use data analytics to improve educational outcomes, student engagement, and institutional effectiveness."
    },

    # ===== GENERAL / OTHER CAREERS =====
    {
        "role": "Administrative Assistant",
        "required_skills": ["Communication", "Microsoft Office", "Organization", "Documentation", "Team Work", "Customer Service"],
        "industry": "Other",
        "experience_level": "Beginner",
        "salary_min": 23000,
        "salary_max": 34000,
        "growth": "Moderate",
        "description": "Provide office support through scheduling, record keeping, communication, and general administrative coordination."
    },
    {
        "role": "Operations Support Assistant",
        "required_skills": ["Communication", "Problem Solving", "Organization", "Documentation", "Team Work", "Commitment"],
        "industry": "Other",
        "experience_level": "Beginner",
        "salary_min": 24000,
        "salary_max": 35000,
        "growth": "High",
        "description": "Support day-to-day operational tasks, maintain records, coordinate with teams, and help services run efficiently."
    }
]
