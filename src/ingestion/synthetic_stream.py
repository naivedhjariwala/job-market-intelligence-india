"""
Authentic Indian Tech Market Feed Synthesizer & Streamer (2025-2026).
Generates realistic unstructured job listings reflecting current hiring trends,
skill distributions, and regional compensation scales across Indian Tech Hubs (in LPA and INR).
"""

import random
import time
from typing import List, Dict, Any
from datetime import datetime, timezone

INDIAN_COMPANIES = [
    ("Razorpay", "India's leading full-stack fintech & payment gateway unicorn", "Bengaluru (Bangalore)"),
    ("CRED", "High-trust community of creditworthy individuals and financial products", "Bengaluru (Bangalore)"),
    ("Swiggy", "Hyperlocal on-demand convenience and food delivery giant", "Bengaluru (Bangalore)"),
    ("Zomato / Blinkit", "Quick-commerce logistics and food marketplace ecosystem", "Delhi NCR (Gurgaon / Noida)"),
    ("PhonePe", "Digital payments and financial inclusion super-app", "Bengaluru (Bangalore)"),
    ("Flipkart", "Pioneering Indian e-commerce marketplace and supply chain", "Bengaluru (Bangalore)"),
    ("Zerodha", "India's largest retail brokerage & fintech platform", "Bengaluru (Bangalore)"),
    ("Postman", "Leading global API development and collaboration platform", "Bengaluru (Bangalore)"),
    ("Freshworks", "Enterprise customer engagement SaaS pioneer", "Chennai"),
    ("Google India", "Frontier search, cloud, and Android engineering centers", "Bengaluru (Bangalore)"),
    ("Microsoft IDC", "Global innovation and cloud enterprise systems", "Hyderabad"),
    ("Amazon India", "Retail systems, AWS cloud services, and logistics technology", "Hyderabad"),
    ("Uber Tech India", "High-throughput rider dispatch and mobility platform", "Bengaluru (Bangalore)"),
    ("Atlassian India", "Collaboration and developer productivity tools (Jira/Confluence)", "Bengaluru (Bangalore)"),
    ("Adobe India", "Creative Cloud and digital experience engineering", "Delhi NCR (Gurgaon / Noida)"),
    ("Salesforce India", "Enterprise cloud CRM and AI agent platforms", "Hyderabad"),
    ("Goldman Sachs Services", "Quantitative engineering and financial architecture", "Bengaluru (Bangalore)"),
    ("InMobi", "Global mobile advertising and ad-tech platforms", "Bengaluru (Bangalore)"),
    ("Meesho", "Social commerce and value e-commerce marketplace", "Bengaluru (Bangalore)"),
    ("Zepto", "Instant 10-minute grocery and delivery logistics", "Mumbai"),
    ("Krutrim AI", "India's indigenous foundational AI and LLM computing infrastructure", "Bengaluru (Bangalore)"),
    ("Sarvam AI", "Sovereign generative AI models for Indian languages", "Bengaluru (Bangalore)"),
    ("Yellow.ai", "Autonomous generative AI customer service agents", "Bengaluru (Bangalore)"),
    ("BrowserStack", "World's leading web and mobile testing cloud", "Mumbai")
]

INDIAN_HUBS = [
    ("Bengaluru (Bangalore)", 1.05, ["Koramangala, Bengaluru", "HSR Layout, Bengaluru", "Whitefield, Bengaluru", "Indiranagar, Bengaluru", "Bellandur, Bengaluru"]),
    ("Hyderabad", 0.98, ["Hitec City, Hyderabad", "Gachibowli, Hyderabad", "Financial District, Hyderabad", "Madhapur, Hyderabad"]),
    ("Delhi NCR (Gurgaon / Noida)", 0.97, ["Cyber City, Gurugram", "Golf Course Road, Gurugram", "Sector 62, Noida", "Sector 125, Noida"]),
    ("Pune", 0.88, ["Hinjewadi Phase 1, Pune", "Magarpatta City, Pune", "Kharadi, Pune", "Baner, Pune"]),
    ("Mumbai", 0.96, ["BKC, Mumbai", "Powai, Mumbai", "Lower Parel, Mumbai", "Navi Mumbai"]),
    ("Chennai", 0.87, ["OMR (IT Corridor), Chennai", "Taramani, Chennai", "Guindy, Chennai"]),
    ("Remote (India)", 0.92, ["Remote (Pan-India)", "India Remote", "WFH (Anywhere in India)"])
]

TITLES_BY_FAMILY = {
    "Machine Learning & AI": [
        ("AI / LLM Research Engineer (GenAI & Fine-Tuning)", 4, 8, ["Python", "PyTorch", "LLMs / Generative AI", "RAG (Retrieval-Augmented)", "LangChain"]),
        ("Senior Machine Learning Engineer (MLOps)", 5, 8, ["Python", "PyTorch", "Scikit-Learn", "MLOps", "Docker", "Kubernetes"]),
        ("Staff AI Systems Architect", 8, 14, ["Python", "C++", "PyTorch", "Deep Learning", "Vector Databases", "Microservices"]),
        ("SDE-2 (Machine Learning & Data Science)", 3, 5, ["Python", "Scikit-Learn", "PyTorch", "SQL", "FastAPI"]),
        ("Foundational Model Scientist (Indic NLP)", 4, 7, ["Python", "NLP", "PyTorch", "Hugging Face", "Deep Learning"])
    ],
    "Backend & Distributed Systems": [
        ("SDE-3 (Backend / High-Scale Microservices)", 5, 8, ["Go (Golang)", "PostgreSQL", "Docker", "Kubernetes", "gRPC", "Apache Kafka"]),
        ("Principal Distributed Systems Engineer", 10, 15, ["Rust", "C++", "Microservices", "System Architecture", "Apache Kafka", "Linux"]),
        ("SDE-2 (Backend Engineer - Python/FastAPI)", 3, 5, ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "REST APIs"]),
        ("Lead Backend Engineer (Java / Spring Boot)", 7, 11, ["Java", "Spring Boot", "Microservices", "AWS", "MySQL", "CI/CD"]),
        ("SDE-1 (Backend Platform Engineer)", 1, 3, ["Java", "Python", "SQL", "REST APIs", "Docker"])
    ],
    "DevOps, Cloud & SRE": [
        ("Staff Site Reliability Engineer (SRE)", 7, 12, ["Kubernetes", "AWS", "Terraform", "Linux", "Prometheus & Grafana", "CI/CD"]),
        ("Cloud Infrastructure Architect", 8, 14, ["AWS", "GCP", "Terraform", "Kubernetes", "System Architecture"]),
        ("Senior DevOps Engineer", 5, 8, ["Docker", "Kubernetes", "CI/CD", "Linux", "AWS", "Ansible"]),
        ("Platform Engineer (Developer Experience & Infra)", 3, 6, ["Go (Golang)", "Kubernetes", "Docker", "Linux", "CI/CD"])
    ],
    "Data Engineering & Warehousing": [
        ("Senior Data Engineer (Spark & Streaming Pipelines)", 5, 8, ["Python", "SQL", "Apache Spark", "Apache Kafka", "Snowflake", "dbt"]),
        ("Lead Analytics Engineer (Modern Data Stack)", 6, 9, ["SQL", "dbt", "Snowflake", "Databricks", "Airflow", "BigQuery"]),
        ("Data Platform Architect", 9, 13, ["SQL", "Databricks", "Apache Spark", "Airflow", "AWS", "System Architecture"]),
        ("SDE-2 Data Engineer (Airflow & Postgres)", 3, 5, ["SQL", "PostgreSQL", "Python", "Airflow", "Data Warehousing"])
    ],
    "Full Stack Engineering": [
        ("Senior Full Stack Engineer (Next.js & Python)", 5, 8, ["TypeScript", "Next.js", "React", "Python", "FastAPI", "PostgreSQL"]),
        ("Staff Full Stack Architect", 8, 12, ["TypeScript", "React", "Node.js", "GraphQL", "PostgreSQL", "System Architecture"]),
        ("SDE-2 Full Stack Developer (React & Node.js)", 3, 5, ["JavaScript", "TypeScript", "React", "Node.js", "MongoDB", "Tailwind CSS"]),
        ("SDE-1 Full Stack Engineer", 1, 2, ["JavaScript", "React", "Node.js", "SQL", "HTML5", "CSS3"])
    ],
    "Frontend & Web Engineering": [
        ("Senior Frontend Engineer (React/TypeScript)", 5, 8, ["JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS", "Testing / QA"]),
        ("Principal UI/UX Architect", 8, 12, ["TypeScript", "React", "Next.js", "Tailwind CSS", "System Architecture"]),
        ("SDE-2 Frontend Engineer", 3, 5, ["JavaScript", "TypeScript", "React", "Tailwind CSS", "REST APIs"])
    ],
    "Mobile Engineering": [
        ("Senior iOS Engineer (Swift)", 5, 8, ["Swift / iOS", "REST APIs", "System Architecture", "Testing / QA"]),
        ("Staff Android Engineer (Kotlin)", 7, 11, ["Kotlin / Android", "Microservices", "CI/CD", "System Architecture"]),
        ("React Native Mobile Developer (SDE-2)", 3, 5, ["React Native", "TypeScript", "JavaScript", "REST APIs"])
    ],
    "Security & QA Engineering": [
        ("Senior DevSecOps & Cloud Security Engineer", 5, 8, ["Cyber Security", "IAM & Auth", "Kubernetes", "AWS", "Docker", "CI/CD"]),
        ("Lead SDET / Automation Architect", 6, 9, ["Python", "Testing / QA", "CI/CD", "Docker", "REST APIs"])
    ],
    "Engineering Leadership & Architecture": [
        ("Director of Engineering / Head of Tech", 12, 18, ["System Architecture", "Agile / Scrum", "Microservices", "Cloud & DevOps"]),
        ("Principal Architect (Core Systems)", 10, 16, ["Kubernetes", "AWS", "System Architecture", "Linux", "CI/CD"])
    ]
}

# Base salary ranges in India (in Lakhs Per Annum - LPA) for Mid-Level baseline
BASE_FAMILY_LPA = {
    "Machine Learning & AI": (24.0, 42.0),
    "Engineering Leadership & Architecture": (50.0, 95.0),
    "Backend & Distributed Systems": (20.0, 38.0),
    "DevOps, Cloud & SRE": (19.0, 36.0),
    "Data Engineering & Warehousing": (19.0, 36.0),
    "Full Stack Engineering": (16.0, 32.0),
    "Mobile Engineering": (17.0, 33.0),
    "Frontend & Web Engineering": (15.0, 30.0),
    "Security & QA Engineering": (16.0, 31.0)
}

TIER_MULTIPLIERS = {
    (0, 2): 0.55,    # Freshers / Entry-Level: ~8 to 16 LPA
    (3, 5): 1.00,    # Mid-Level / SDE-2: ~18 to 36 LPA
    (6, 8): 1.55,    # Senior / SDE-3: ~32 to 58 LPA
    (9, 12): 2.15,   # Lead / Staff: ~48 to 85 LPA
    (13, 25): 3.10   # Principal / Director: ~75 to 150+ LPA
}

class SyntheticStreamGenerator:
    """Simulates authentic real-time Indian tech job listings in LPA and INR."""

    def __init__(self, seed: int = 2026):
        self.rng = random.Random(seed)

    def generate_single_job(self, job_idx: int) -> Dict[str, Any]:
        company_name, company_mission, home_city = self.rng.choice(INDIAN_COMPANIES)
        job_family = self.rng.choice(list(TITLES_BY_FAMILY.keys()))
        title_template, min_exp, max_exp, core_skills = self.rng.choice(TITLES_BY_FAMILY[job_family])
        
        hub_name, hub_mult, sample_locations = self.rng.choice(INDIAN_HUBS)
        location = self.rng.choice(sample_locations)
        is_remote = "remote" in hub_name.lower() or self.rng.random() < 0.35

        # Experience tier multiplier
        mult = 1.0
        for (t_min, t_max), m in TIER_MULTIPLIERS.items():
            if t_min <= min_exp <= t_max:
                mult = m
                break

        # Base salary range in LPA
        base_low_lpa, base_high_lpa = BASE_FAMILY_LPA[job_family]
        # High-demand skill premium in India (e.g. LLMs, Kubernetes, Go, Rust command premium)
        skill_bonus = 1.0 + (0.035 * len(core_skills))
        
        noise = self.rng.uniform(0.94, 1.06)
        salary_min_lpa = round(base_low_lpa * mult * hub_mult * skill_bonus * noise, 1)
        salary_max_lpa = round(base_high_lpa * mult * hub_mult * skill_bonus * noise, 1)
        
        # Ensure minimum reasonable spread
        if salary_max_lpa - salary_min_lpa < 4.0:
            salary_max_lpa = round(salary_min_lpa + 6.0, 1)

        salary_str = f"₹{salary_min_lpa} - ₹{salary_max_lpa} LPA (Fixed + Variable CTC)"
        skills_formatted = ", ".join(core_skills)

        # Unstructured description reflecting Indian tech ecosystem
        description = f"""
        <h3>About {company_name}</h3>
        <p>{company_name} is one of India's leading technology powerhouses, driving {company_mission}. Our engineering engineering team operates out of modern development hubs across India.</p>
        
        <h3>Role Overview</h3>
        <p>We are actively looking for a <strong>{title_template}</strong> to join our core engineering division in {hub_name}. You will design and scale mission-critical services handling high-concurrency workloads across the Indian subcontinent.</p>
        
        <h3>What You Will Do</h3>
        <ul>
            <li>Architect, develop, and maintain high-performance, fault-tolerant microservices and platforms.</li>
            <li>Collaborate with Product Managers, Data Scientists, and Engineering Leads to ship high-impact features.</li>
            <li>Enforce top-tier engineering hygiene: automated testing, CI/CD pipelines, and observability.</li>
            <li>Drive technical design reviews, mentor junior engineers, and participate in on-call rotations.</li>
        </ul>
        
        <h3>Qualifications & Skills Required</h3>
        <ul>
            <li>{min_exp} to {max_exp}+ years of relevant software engineering experience in modern product tech stacks.</li>
            <li>Hands-on expertise with <strong>{skills_formatted}</strong> and modern system design.</li>
            <li>Strong computer science fundamentals: algorithms, data structures, and database optimization.</li>
            <li>Experience with cloud native infrastructure, low-latency microservices, and distributed caches.</li>
        </ul>
        
        <h3>Compensation & Perks</h3>
        <p>Annual CTC: <strong>{salary_str}</strong> + Lucrative ESOP grant + Comprehensive Medical Insurance for family + Generous annual learning allowance.</p>
        """

        job_id = f"ind-{job_idx}-{int(time.time())}"
        
        return {
            "id": job_id,
            "source": "India Tech Stream",
            "title": title_template,
            "company_name": company_name,
            "location": location,
            "remote": is_remote,
            "description": description,
            "salary": salary_str,
            "url": f"https://techjobs.in/positions/{job_id}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def generate_batch(self, count: int = 600) -> List[Dict[str, Any]]:
        """Generates realistic Indian tech listings."""
        return [self.generate_single_job(i) for i in range(1, count + 1)]
