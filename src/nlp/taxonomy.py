"""
Technical Skill Taxonomy and Category Definitions.
Standardizes 120+ modern technical competencies across 7 core disciplines (2025-2026 market).
"""

from typing import Dict, List, Pattern
import re

# Taxonomy mapping: Category -> Subcategory / Canonical Skill Name -> Regex Patterns
SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "AI & Machine Learning": {
        "Python": [r"\bpython\b"],
        "PyTorch": [r"\bpytorch\b"],
        "TensorFlow": [r"\btensorflow\b"],
        "Scikit-Learn": [r"\bscikit[-_]?learn\b", r"\bsklearn\b"],
        "LLMs / Generative AI": [r"\bllms?\b", r"\blarge language models?\b", r"\bgenerative ai\b", r"\bgenai\b"],
        "RAG (Retrieval-Augmented)": [r"\brag\b", r"\bretrieval[- ]augmented\b"],
        "LangChain": [r"\blangchain\b", r"\blanggraph\b"],
        "Hugging Face": [r"\bhugging\s*face\b", r"\btransformers\b"],
        "Deep Learning": [r"\bdeep learning\b", r"\bneural networks?\b"],
        "NLP": [r"\bnlp\b", r"\bnatural language processing\b"],
        "Computer Vision": [r"\bcomputer vision\b", r"\bopencv\b"],
        "MLOps": [r"\bmlops\b", r"\bmodel serving\b", r"\bmlflow\b", r"\bkubeflow\b"],
        "Vector Databases": [r"\bvector (?:database|db|store)s?\b", r"\bpinecone\b", r"\bchromadb\b", r"\bweaviate\b", r"\bmilvus\b", r"\bqdrant\b"],
        "Fine-tuning / Alignment": [r"\bfine[- ]tuning\b", r"\blo(?:ra|ra)\b", r"\brlhf\b"],
    },
    "Backend & Systems": {
        "Go (Golang)": [r"\bgolang\b", r"\bgo\s+developer\b", r"\bgo\s+backend\b"],
        "Rust": [r"\brust\b", r"\brustlang\b"],
        "Java": [r"\bjava\b(?!script)"],
        "C++": [r"\bc\+\+\b"],
        "C# / .NET": [r"\bc#\b", r"\bc\s*sharp\b", r"\b\.net\b", r"\bdotnet\b"],
        "Node.js": [r"\bnode(?:\.js)?\b"],
        "FastAPI": [r"\bfastapi\b"],
        "Django": [r"\bdjango\b"],
        "Flask": [r"\bflask\b"],
        "Spring Boot": [r"\bspring\s*boot\b", r"\bspring\s*framework\b"],
        "Microservices": [r"\bmicroservices?\b", r"\bdistributed systems?\b"],
        "REST APIs": [r"\brest(?:ful)?\s*(?:api|apis)?\b"],
        "GraphQL": [r"\bgraphql\b"],
        "gRPC": [r"\bgrpc\b"],
        "Apache Kafka": [r"\b(?:apache\s*)?kafka\b"],
        "RabbitMQ": [r"\brabbitmq\b"],
    },
    "Cloud & DevOps": {
        "AWS": [r"\baws\b", r"\bamazon web services\b"],
        "Azure": [r"\bazure\b", r"\bmicrosoft azure\b"],
        "GCP": [r"\bgcp\b", r"\bgoogle cloud(?:\s*platform)?\b"],
        "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
        "Docker": [r"\bdocker\b", r"\bcontainers?\b"],
        "Terraform": [r"\bterraform\b", r"\biac\b", r"\binfrastructure as code\b"],
        "CI/CD": [r"\bci[/-]?cd\b", r"\bcontinuous integration\b", r"\bjenkins\b", r"\bgithub actions\b", r"\bgitlab ci\b"],
        "Linux": [r"\blinux\b", r"\bunix\b", r"\bbash\b", r"\bshell scripting\b"],
        "Prometheus & Grafana": [r"\bprometheus\b", r"\bgrafana\b", r"\bdatadog\b", r"\bobservability\b"],
        "Ansible": [r"\bansible\b"],
    },
    "Data Engineering & Databases": {
        "SQL": [r"\bsql\b"],
        "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
        "MySQL": [r"\bmysql\b"],
        "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
        "Redis": [r"\bredis\b"],
        "Snowflake": [r"\bsnowflake\b"],
        "Databricks": [r"\bdatabricks\b"],
        "Apache Spark": [r"\b(?:apache\s*)?spark\b", r"\bpyspark\b"],
        "Airflow": [r"\b(?:apache\s*)?airflow\b"],
        "dbt": [r"\bdbt\b"],
        "BigQuery": [r"\bbigquery\b"],
        "Data Warehousing": [r"\bdata warehous(?:e|ing)\b", r"\betl\b", r"\belt\b", r"\bdata pipelines?\b"],
    },
    "Frontend & Mobile": {
        "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
        "TypeScript": [r"\btypescript\b", r"\bts\b"],
        "React": [r"\breact(?:\.js)?\b(?! native)"],
        "Next.js": [r"\bnext(?:\.js)?\b"],
        "Vue.js": [r"\bvue(?:\.js)?\b"],
        "Angular": [r"\bangular\b"],
        "Tailwind CSS": [r"\btailwind(?:css)?\b"],
        "React Native": [r"\breact\s*native\b"],
        "Flutter": [r"\bflutter\b"],
        "Swift / iOS": [r"\bswift\b", r"\bios developer\b"],
        "Kotlin / Android": [r"\bkotlin\b", r"\bandroid developer\b"],
    },
    "Security & Architecture": {
        "Cyber Security": [r"\bcyber\s*security\b", r"\binformation security\b", r"\bsecops\b", r"\bdevsecops\b"],
        "IAM & Auth": [r"\biam\b", r"\boauth(?:2)?\b", r"\bsso\b", r"\bjwt\b"],
        "System Architecture": [r"\bsystem architecture\b", r"\bsystem design\b", r"\bhigh availability\b"],
        "Agile / Scrum": [r"\bagile\b", r"\bscrum\b"],
        "Testing / QA": [r"\btest-driven\b", r"\btdd\b", r"\bunit test(?:ing|s)?\b", r"\bcypress\b", r"\bplaywright\b", r"\bselenium\b"],
    }
}

# Compile regex patterns once for optimal parsing performance
COMPILED_PATTERNS: Dict[str, Dict[str, List[Pattern]]] = {}
for category, skills in SKILL_TAXONOMY.items():
    COMPILED_PATTERNS[category] = {}
    for skill, patterns in skills.items():
        COMPILED_PATTERNS[category][skill] = [
            re.compile(p, re.IGNORECASE) for p in patterns
        ]

# Flat lookup: canonical skill -> category
SKILL_TO_CATEGORY: Dict[str, str] = {
    skill: category
    for category, skills in SKILL_TAXONOMY.items()
    for skill in skills
}

ALL_CANONICAL_SKILLS: List[str] = sorted(list(SKILL_TO_CATEGORY.keys()))

# Job Family classifications
JOB_FAMILIES = [
    "Backend & Distributed Systems",
    "Frontend & Web Engineering",
    "Full Stack Engineering",
    "Data Engineering & Warehousing",
    "Machine Learning & AI",
    "DevOps, Cloud & SRE",
    "Mobile Engineering",
    "Security & QA Engineering",
    "Engineering Leadership & Architecture"
]

# Experience tiers definition
EXPERIENCE_TIERS = [
    "Entry-Level (0-2 yrs)",
    "Mid-Level (3-5 yrs)",
    "Senior (6-8 yrs)",
    "Lead / Staff (9-12 yrs)",
    "Principal / Director (12+ yrs)"
]

# Major Indian Tech Ecosystem Hubs
INDIAN_TECH_HUBS = [
    "Bengaluru (Bangalore)",
    "Hyderabad",
    "Delhi NCR (Gurgaon / Noida)",
    "Pune",
    "Mumbai",
    "Chennai",
    "Remote (India)"
]


