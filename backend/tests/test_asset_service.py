import pytest

from app.db.session import SessionLocal
from app.models.asset import AssetType, Criticality, DataClassification, Environment
from app.services import asset as asset_service


@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def _asset_data(**overrides):
    data = dict(
        asset_tag="AST-001",
        name="Customer API Gateway",
        asset_type=AssetType.API,
        owner="Platform Team",
        business_unit="Digital Banking",
        environment=Environment.PRODUCTION,
        criticality=Criticality.HIGH,
        data_classification=DataClassification.CONFIDENTIAL,
        internet_exposed=True,
    )
    data.update(overrides)
    return data


def test_create_and_get_asset(db_session):
    asset = asset_service.create_asset(db_session, _asset_data())
    fetched = asset_service.get_asset(db_session, asset.id)
    assert fetched is not None
    assert fetched.name == "Customer API Gateway"


def test_list_assets_orders_by_criticality_severity_not_alphabetically(db_session):
    """Regression guard: criticality is stored as a string ('critical',
    'high', 'low', 'medium'), so a naive alphabetical DESC sort would put
    'medium' first and 'critical' last - the opposite of what a risk
    register must show.
    """
    asset_service.create_asset(db_session, _asset_data(asset_tag="AST-LOW", criticality=Criticality.LOW))
    asset_service.create_asset(
        db_session, _asset_data(asset_tag="AST-CRIT", criticality=Criticality.CRITICAL)
    )
    asset_service.create_asset(
        db_session, _asset_data(asset_tag="AST-MED", criticality=Criticality.MEDIUM)
    )
    asset_service.create_asset(db_session, _asset_data(asset_tag="AST-HIGH", criticality=Criticality.HIGH))

    results = asset_service.list_assets(db_session)
    criticalities = [a.criticality for a in results]
    assert criticalities == [
        Criticality.CRITICAL,
        Criticality.HIGH,
        Criticality.MEDIUM,
        Criticality.LOW,
    ]


def test_list_assets_filters_by_criticality(db_session):
    asset_service.create_asset(db_session, _asset_data(asset_tag="AST-A", criticality=Criticality.LOW))
    asset_service.create_asset(
        db_session, _asset_data(asset_tag="AST-B", criticality=Criticality.CRITICAL)
    )

    results = asset_service.list_assets(db_session, criticality=Criticality.CRITICAL)
    assert len(results) == 1
    assert results[0].asset_tag == "AST-B"


def test_list_assets_search_matches_name_tag_or_owner(db_session):
    asset_service.create_asset(db_session, _asset_data(asset_tag="AST-PAY", name="Payment Service"))
    results = asset_service.list_assets(db_session, search="payment")
    assert len(results) == 1
    assert results[0].asset_tag == "AST-PAY"


def test_add_dependency(db_session):
    api = asset_service.create_asset(db_session, _asset_data(asset_tag="AST-API"))
    db = asset_service.create_asset(
        db_session, _asset_data(asset_tag="AST-DB", asset_type=AssetType.DATABASE)
    )
    dependency = asset_service.add_dependency(db_session, api.id, db.id, "reads customer records")
    assert dependency.asset_id == api.id
    assert dependency.depends_on_asset_id == db.id


def test_asset_cannot_depend_on_itself(db_session):
    api = asset_service.create_asset(db_session, _asset_data(asset_tag="AST-SELF"))
    with pytest.raises(ValueError):
        asset_service.add_dependency(db_session, api.id, api.id, "invalid")
