"""Seed synthetic demo data: two hospital tenants (H1, H2), their users,
synthetic patients, and default AI governance policies.

RULE 11: Use synthetic healthcare data only. Every name, email, and phone
number below is fictional demo data.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User
from app.models.patient import Patient
from app.models.ai_policy import AIPolicy
from app.security.auth import hash_password

DEMO_PASSWORD = "Demo@123"

POLICY_DEFS = [
    ("TENANT_ISOLATION", "Tenant Isolation", "BLOCK", "CRITICAL"),
    ("PHI_PROTECTION", "PII/PHI Protection", "MASK", "MEDIUM"),
    ("AI_INPUT_SECURITY", "Prompt Injection Protection", "BLOCK", "CRITICAL"),
    ("HIGH_RISK_HEALTHCARE", "High-Risk Healthcare Request", "HUMAN_REVIEW", "HIGH"),
    ("CROSS_TENANT_ACCESS", "Cross-Tenant Access", "BLOCK", "CRITICAL"),
    ("AUDIT_LOGGING", "Audit Logging", "LOG", "LOW"),
    ("SENSITIVE_EXPORT", "Sensitive Data Export", "BLOCK", "HIGH"),
]

H1_PATIENTS = [
    ("H1-P001", "Arun Kumar", 45, "Male", "arun.kumar@h1demo.in", "+91-9000000001", "Chennai", "Diabetes"),
    ("H1-P002", "Meena Ravi", 32, "Female", "meena.ravi@h1demo.in", "+91-9000000002", "Chennai", "Hypertension"),
    ("H1-P003", "Suresh Kumar", 67, "Male", "suresh.kumar@h1demo.in", "+91-9000000003", "Chennai", "Cardiac Follow-up"),
    ("H1-P004", "Lakshmi Narayanan", 54, "Female", "lakshmi.n@h1demo.in", "+91-9000000004", "Chennai", "Thyroid Disorder"),
    ("H1-P005", "Rajesh Kumar", 41, "Male", "rajesh.kumar@h1demo.in", "+91-9000000005", "Chennai", "Asthma"),
    ("H1-P006", "Priya Sundaram", 29, "Female", "priya.s@h1demo.in", "+91-9000000006", "Chennai", "Prenatal Care"),
    ("H1-P007", "Kannan Pillai", 58, "Male", "kannan.p@h1demo.in", "+91-9000000007", "Chennai", "Cardiac Follow-up"),
    ("H1-P008", "Divya Shree", 36, "Female", "divya.shree@h1demo.in", "+91-9000000008", "Chennai", "Migraine"),
    ("H1-P009", "Muthu Vel", 72, "Male", "muthu.vel@h1demo.in", "+91-9000000009", "Chennai", "Arthritis"),
    ("H1-P010", "Anjali Krishnan", 48, "Female", "anjali.k@h1demo.in", "+91-9000000010", "Chennai", "Diabetes"),
    ("H1-P011", "Karthik Subramaniam", 39, "Male", "karthik.s@h1demo.in", "+91-9000000011", "Chennai", "Hypertension"),
]

H2_PATIENTS = [
    ("H2-P001", "Manjunath Rao", 50, "Male", "manjunath.rao@h2demo.in", "+91-8000000001", "Bengaluru", "Hypertension"),
    ("H2-P002", "Deepa Shetty", 34, "Female", "deepa.shetty@h2demo.in", "+91-8000000002", "Bengaluru", "PCOS"),
    ("H2-P003", "Ramesh Gowda", 61, "Male", "ramesh.gowda@h2demo.in", "+91-8000000003", "Bengaluru", "Cardiac Follow-up"),
    ("H2-P004", "Shalini Reddy", 27, "Female", "shalini.reddy@h2demo.in", "+91-8000000004", "Bengaluru", "Anemia"),
    ("H2-P005", "Vinay Hegde", 44, "Male", "vinay.hegde@h2demo.in", "+91-8000000005", "Bengaluru", "Diabetes"),
    ("H2-P006", "Kavya Nair", 31, "Female", "kavya.nair@h2demo.in", "+91-8000000006", "Bengaluru", "Prenatal Care"),
    ("H2-P007", "Srinivas Murthy", 66, "Male", "srinivas.murthy@h2demo.in", "+91-8000000007", "Bengaluru", "Arthritis"),
    ("H2-P008", "Pooja Bhat", 38, "Female", "pooja.bhat@h2demo.in", "+91-8000000008", "Bengaluru", "Migraine"),
    ("H2-P009", "Nagesh Iyer", 70, "Male", "nagesh.iyer@h2demo.in", "+91-8000000009", "Bengaluru", "Cardiac Follow-up"),
    ("H2-P010", "Ritu Kulkarni", 46, "Female", "ritu.kulkarni@h2demo.in", "+91-8000000010", "Bengaluru", "Thyroid Disorder"),
    ("H2-P011", "Abhishek Pai", 33, "Male", "abhishek.pai@h2demo.in", "+91-8000000011", "Bengaluru", "Asthma"),
]


def _admission_dates(n: int) -> list[datetime]:
    """Spread admissions across this month and last month so 'admitted this
    month' queries return a realistic, non-trivial count."""
    now = datetime.now(timezone.utc)
    dates = []
    for i in range(n):
        if i % 3 == 0:
            dates.append(now - timedelta(days=45 + i))  # last month
        else:
            dates.append(now - timedelta(days=(i % 20) + 1))  # this month
    return dates


def seed_if_empty(db: Session) -> None:
    if db.query(Tenant).first() is not None:
        return  # already seeded

    h1 = Tenant(tenant_code="H1", name="H1 Hospital", location="Chennai", status="PROTECTED")
    h2 = Tenant(tenant_code="H2", name="H2 Hospital", location="Bengaluru", status="PROTECTED")
    db.add_all([h1, h2])
    db.commit()
    db.refresh(h1)
    db.refresh(h2)

    users = [
        User(tenant_id=h1.id, name="Dr. Arun", email="arun@h1.demo", role="DOCTOR", password_hash=hash_password(DEMO_PASSWORD)),
        User(tenant_id=h1.id, name="Priya", email="priya@h1.demo", role="HOSPITAL_ADMIN", password_hash=hash_password(DEMO_PASSWORD)),
        User(tenant_id=h1.id, name="Kumar", email="kumar@h1.demo", role="HOSPITAL_ADMIN", password_hash=hash_password(DEMO_PASSWORD)),
        User(tenant_id=h2.id, name="Dr. Meera", email="meera@h2.demo", role="DOCTOR", password_hash=hash_password(DEMO_PASSWORD)),
        User(tenant_id=h2.id, name="Ravi", email="ravi@h2.demo", role="HOSPITAL_ADMIN", password_hash=hash_password(DEMO_PASSWORD)),
        User(tenant_id=None, name="Platform Admin", email="admin@securemed.demo", role="SUPER_ADMIN", password_hash=hash_password(DEMO_PASSWORD)),
    ]
    db.add_all(users)

    for tenant, patient_rows in [(h1, H1_PATIENTS), (h2, H2_PATIENTS)]:
        dates = _admission_dates(len(patient_rows))
        for row, admission_date in zip(patient_rows, dates):
            code, name, age, gender, email, phone, city, condition = row
            db.add(Patient(
                tenant_id=tenant.id, patient_code=code, name=name, age=age, gender=gender,
                email=email, phone=phone, city=city, condition=condition, admission_date=admission_date,
            ))

    for tenant in (h1, h2):
        for code, name, action, risk in POLICY_DEFS:
            db.add(AIPolicy(tenant_id=tenant.id, policy_code=code, policy_name=name, action=action, enabled=True, risk_level=risk))

    db.commit()
