"""Seed demo users, the Northstar Financial Services asset inventory, and
its threat model for local/demo use.

Run: python scripts/seed_demo_data.py (from backend/)

Passwords below are LOCAL DEMO CREDENTIALS for the fictional Northstar
Financial Services environment, not real secrets - usable only against
your own local Docker Compose stack. Override via the DEMO_*_PASSWORD env
vars if you want different ones. See SECURITY.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.risk import RiskStatus, TreatmentDecision
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.seed_data.northstar_appsec import (
    NORTHSTAR_APPSEC_FINDINGS,
    SAMPLE_LEAKED_CONFIG_EXPOSURE,
    SAMPLE_LEAKED_CONFIG_LOCATION,
    SAMPLE_LEAKED_CONFIG_TEXT,
)
from app.seed_data.northstar_assets import NORTHSTAR_ASSET_DEPENDENCIES, NORTHSTAR_ASSETS
from app.seed_data.northstar_iam_cloud import NORTHSTAR_CLOUD_FINDINGS, NORTHSTAR_IDENTITY_ACCOUNTS
from app.seed_data.northstar_risks import NORTHSTAR_RISKS
from app.seed_data.northstar_threats import (
    NORTHSTAR_ATTACK_PATHS,
    NORTHSTAR_THREAT_ACTORS,
    NORTHSTAR_THREATS,
)
from app.seed_data.northstar_vulnerabilities import NORTHSTAR_VULNERABILITIES
from app.services import appsec as appsec_service
from app.services import asset as asset_service
from app.services import cloud as cloud_service
from app.services import iam as iam_service
from app.services import risk as risk_service
from app.services import threat as threat_service
from app.services import vulnerability as vuln_service
from app.services.auth import create_user, get_user_by_username

DEMO_USERS = [
    (
        "admin",
        "admin@northstar-financial.example",
        ROLE_ADMIN,
        os.getenv("DEMO_ADMIN_PASSWORD", "ChangeMe123!"),
    ),
    (
        "risk_analyst",
        "risk.analyst@northstar-financial.example",
        ROLE_RISK_ANALYST,
        os.getenv("DEMO_ANALYST_PASSWORD", "ChangeMe123!"),
    ),
    (
        "viewer",
        "viewer@northstar-financial.example",
        ROLE_VIEWER,
        os.getenv("DEMO_VIEWER_PASSWORD", "ChangeMe123!"),
    ),
]


def seed_users(db) -> None:
    for username, email, role, password in DEMO_USERS:
        if get_user_by_username(db, username):
            print(f"User '{username}' already exists - skipping.")
            continue
        create_user(db, username, email, password, role)
        print(f"Created demo user '{username}' ({role}) - local/demo use only.")


def seed_assets(db) -> dict[str, int]:
    existing = asset_service.list_assets(db)
    if existing:
        print("Assets already seeded - skipping.")
        return {a.asset_tag: a.id for a in existing}

    tag_to_id = {}
    for data in NORTHSTAR_ASSETS:
        asset = asset_service.create_asset(db, data)
        tag_to_id[asset.asset_tag] = asset.id
    print(f"Created {len(NORTHSTAR_ASSETS)} Northstar Financial Services assets.")

    for from_tag, to_tag, description in NORTHSTAR_ASSET_DEPENDENCIES:
        asset_service.add_dependency(db, tag_to_id[from_tag], tag_to_id[to_tag], description)
    print(f"Created {len(NORTHSTAR_ASSET_DEPENDENCIES)} asset dependencies.")

    return tag_to_id


def seed_threats(db, tag_to_id: dict[str, int]) -> dict[str, int]:
    if threat_service.list_threat_actors(db):
        print("Threat model already seeded - skipping.")
        return {t.name: t.id for t in threat_service.list_threats(db)}

    actor_name_to_id = {}
    for data in NORTHSTAR_THREAT_ACTORS:
        actor = threat_service.create_threat_actor(db, data)
        actor_name_to_id[actor.name] = actor.id
    print(f"Created {len(NORTHSTAR_THREAT_ACTORS)} threat actors.")

    threat_name_to_id = {}
    for name, description, mitre_id, mitre_name, why_relevant, actor_name in NORTHSTAR_THREATS:
        threat = threat_service.create_threat(
            db,
            dict(
                name=name,
                description=description,
                mitre_technique_id=mitre_id,
                mitre_technique_name=mitre_name,
                why_relevant=why_relevant,
                threat_actor_id=actor_name_to_id.get(actor_name) if actor_name else None,
            ),
        )
        threat_name_to_id[threat.name] = threat.id
    print(f"Created {len(NORTHSTAR_THREATS)} threats.")

    for path_data in NORTHSTAR_ATTACK_PATHS:
        steps = [
            {
                "sequence": step["sequence"],
                "description": step["description"],
                "asset_id": tag_to_id.get(step["asset_tag"]) if step.get("asset_tag") else None,
                "threat_id": threat_name_to_id.get(step["threat_name"]) if step.get("threat_name") else None,
            }
            for step in path_data["steps"]
        ]
        threat_service.create_attack_path(
            db,
            dict(
                name=path_data["name"],
                description=path_data["description"],
                entry_point=path_data["entry_point"],
                target_asset_id=tag_to_id[path_data["target_asset_tag"]],
                likelihood=path_data["likelihood"],
                impact=path_data["impact"],
                notes=path_data["notes"],
                steps=steps,
            ),
        )
    print(f"Created {len(NORTHSTAR_ATTACK_PATHS)} attack paths.")
    return threat_name_to_id


def seed_risks(db, tag_to_id: dict[str, int], threat_name_to_id: dict[str, int]) -> None:
    if risk_service.list_risk_records(db):
        print("Risk register already seeded - skipping.")
        return

    for item in NORTHSTAR_RISKS:
        record = risk_service.create_risk_record(
            db,
            dict(
                title=item["title"],
                description=item["description"],
                asset_id=tag_to_id[item["asset_tag"]],
                threat_id=threat_name_to_id.get(item["threat_name"]) if item["threat_name"] else None,
                threat_severity=item["threat_severity"],
                known_exploited=item["known_exploited"],
                control_effectiveness=item["control_effectiveness"],
            ),
        )
        if item["treatment"]:
            treatment = dict(item["treatment"])
            treatment["treatment_decision"] = TreatmentDecision(treatment["treatment_decision"])
            treatment["status"] = RiskStatus(treatment["status"])
            risk_service.update_treatment(db, record, treatment)
    print(f"Created {len(NORTHSTAR_RISKS)} risk register entries.")


def seed_vulnerabilities(db, tag_to_id: dict[str, int]) -> None:
    if vuln_service.list_vulnerabilities(db):
        print("Vulnerabilities already seeded - skipping.")
        return

    assessed = 0
    for item in NORTHSTAR_VULNERABILITIES:
        vuln = vuln_service.create_vulnerability(
            db,
            dict(
                cve_id=item["cve_id"],
                title=item["title"],
                description=item["description"],
                asset_id=tag_to_id[item["asset_tag"]],
                cvss_score=item["cvss_score"],
                known_exploited=item["known_exploited"],
                compensating_controls=item["compensating_controls"],
            ),
        )
        if item["assess"]:
            vuln_service.assess_vulnerability(
                db, vuln, control_effectiveness=0.2, risk_appetite="moderate"
            )
            assessed += 1
    print(
        f"Created {len(NORTHSTAR_VULNERABILITIES)} vulnerabilities ({assessed} assessed for business risk)."
    )


def seed_iam_and_cloud(db, tag_to_id: dict[str, int]) -> None:
    if iam_service.list_identity_accounts(db):
        print("IAM accounts already seeded - skipping.")
    else:
        for item in NORTHSTAR_IDENTITY_ACCOUNTS:
            data = dict(item)
            asset_tag = data.pop("asset_tag", None)
            data["associated_asset_id"] = tag_to_id.get(asset_tag) if asset_tag else None
            iam_service.create_identity_account(db, data)
        print(f"Created {len(NORTHSTAR_IDENTITY_ACCOUNTS)} IAM accounts.")

    if cloud_service.list_findings(db):
        print("Cloud findings already seeded - skipping.")
    else:
        for item in NORTHSTAR_CLOUD_FINDINGS:
            data = dict(item)
            asset_tag = data.pop("asset_tag", None)
            data["asset_id"] = tag_to_id.get(asset_tag) if asset_tag else None
            cloud_service.create_finding(db, data)
        print(f"Created {len(NORTHSTAR_CLOUD_FINDINGS)} cloud security findings.")


def seed_app_security(db, tag_to_id: dict[str, int]) -> None:
    if appsec_service.list_appsec_findings(db):
        print("App security findings already seeded - skipping.")
    else:
        for item in NORTHSTAR_APPSEC_FINDINGS:
            data = dict(item)
            asset_tag = data.pop("asset_tag", None)
            data["asset_id"] = tag_to_id.get(asset_tag) if asset_tag else None
            appsec_service.create_appsec_finding(db, data)
        print(f"Created {len(NORTHSTAR_APPSEC_FINDINGS)} app security findings.")

    if appsec_service.list_secret_findings(db):
        print("Secret findings already seeded - skipping.")
    else:
        found = appsec_service.scan_and_record(
            db, SAMPLE_LEAKED_CONFIG_TEXT, SAMPLE_LEAKED_CONFIG_LOCATION, SAMPLE_LEAKED_CONFIG_EXPOSURE
        )
        print(f"Secret scan of sample leaked config found and recorded {len(found)} matches.")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
        tag_to_id = seed_assets(db)
        threat_name_to_id = seed_threats(db, tag_to_id)
        seed_risks(db, tag_to_id, threat_name_to_id)
        seed_vulnerabilities(db, tag_to_id)
        seed_iam_and_cloud(db, tag_to_id)
        seed_app_security(db, tag_to_id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
