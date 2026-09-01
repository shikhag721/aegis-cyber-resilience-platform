import pytest

from app.db.session import SessionLocal
from app.models.asset import AssetType, Criticality, DataClassification, Environment
from app.models.threat import ThreatActorCategory
from app.services import asset as asset_service
from app.services import threat as threat_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def target_asset(db_session):
    return asset_service.create_asset(
        db_session,
        dict(
            asset_tag="AST-TEST",
            name="Test Payment Service",
            asset_type=AssetType.APPLICATION,
            owner="Test Owner",
            business_unit="Test BU",
            environment=Environment.PRODUCTION,
            criticality=Criticality.CRITICAL,
            data_classification=DataClassification.RESTRICTED,
        ),
    )


def test_create_threat_actor(db_session):
    actor = threat_service.create_threat_actor(
        db_session,
        dict(
            name="Organized Cybercrime Group",
            category=ThreatActorCategory.EXTERNAL_CYBERCRIMINAL,
            motivation="Financial gain via fraud",
            sophistication="High",
        ),
    )
    assert actor.id is not None


def test_create_threat_with_mitre_mapping(db_session):
    threat = threat_service.create_threat(
        db_session,
        dict(
            name="Credential stuffing against customer login",
            description="Automated login attempts using breached credential lists.",
            mitre_technique_id="T1110.004",
            mitre_technique_name="Brute Force: Credential Stuffing",
            why_relevant=(
                "The Customer Web Portal has no documented account lockout policy, and "
                "reused-password rates among retail banking customers are historically high."
            ),
        ),
    )
    assert threat.mitre_technique_id == "T1110.004"


def test_create_attack_path_with_steps(db_session, target_asset):
    attack_path = threat_service.create_attack_path(
        db_session,
        dict(
            name="Compromised credential to data exfiltration",
            description="Section 8 worked example applied to the Payment Processing Service.",
            entry_point="Internet",
            target_asset_id=target_asset.id,
            likelihood=3,
            impact=5,
            steps=[
                {"sequence": 1, "description": "Attacker obtains valid customer credential (phishing)"},
                {"sequence": 2, "description": "Authenticated API access via Public API Gateway"},
                {"sequence": 3, "description": "Privilege abuse within Payment Processing Service"},
                {"sequence": 4, "description": "Database access and data exfiltration"},
            ],
        ),
    )
    assert attack_path.score == 15
    fetched = threat_service.get_attack_path(db_session, attack_path.id)
    assert len(fetched.steps) == 4
    assert fetched.steps[0].sequence == 1


def test_list_attack_paths_sorted_by_score_descending(db_session, target_asset):
    threat_service.create_attack_path(
        db_session,
        dict(
            name="Low score path",
            description="d",
            entry_point="Internet",
            target_asset_id=target_asset.id,
            likelihood=1,
            impact=2,
            steps=[],
        ),
    )
    threat_service.create_attack_path(
        db_session,
        dict(
            name="High score path",
            description="d",
            entry_point="Internet",
            target_asset_id=target_asset.id,
            likelihood=5,
            impact=5,
            steps=[],
        ),
    )
    results = threat_service.list_attack_paths(db_session)
    assert results[0].name == "High score path"
    assert results[0].score >= results[1].score
