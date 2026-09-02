"""Third-party vendor risk (Section 20). See
docs/decisions/0008-vendor-risk-not-reusing-risk-engine.md for why this is
a parallel scorer rather than a forced reuse of app/risk_engine/.
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.vendor import Vendor, VendorAssessment

_CRITICALITY_BASE_IMPACT = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_CLASSIFICATION_IMPACT_BONUS = {
    "public": 0,
    "internal": 0,
    "confidential": 1,
    "restricted": 1,
    "highly_restricted": 2,
}

RATING_BANDS = [(1, 4, "Low"), (5, 9, "Moderate"), (10, 16, "High"), (17, 25, "Critical")]
RECOMMENDATION_FOR_RATING = {
    "Low": "Approve",
    "Moderate": "Approve with conditions",
    "High": "Approve with conditions",
    "Critical": "Escalate",
}


def _rating_for_score(score: int) -> str:
    for low, high, rating in RATING_BANDS:
        if low <= score <= high:
            return rating
    return "Critical"


@dataclass
class VendorRiskFactor:
    name: str
    axis: str
    weight: int
    reason: str


@dataclass
class VendorRiskResult:
    likelihood: int
    impact: int
    score: int
    rating: str
    contributing_factors: list[VendorRiskFactor] = field(default_factory=list)
    recommendation: str = ""


def assess_vendor(vendor: Vendor) -> VendorRiskResult:
    factors: list[VendorRiskFactor] = []
    likelihood = 1
    impact = 1

    if not vendor.certifications.strip():
        likelihood += 1
        factors.append(
            VendorRiskFactor(
                name="No independent certification on file",
                axis="likelihood",
                weight=1,
                reason="No SOC 2 / ISO 27001 / equivalent certification evidence has been provided.",
            )
        )

    if not vendor.contractual_security_clause:
        likelihood += 1
        factors.append(
            VendorRiskFactor(
                name="No contractual security clause",
                axis="likelihood",
                weight=1,
                reason="The contract does not include a confirmed security/data-protection clause.",
            )
        )

    if vendor.has_incident_history:
        likelihood += 2
        factors.append(
            VendorRiskFactor(
                name="Prior security incident history",
                axis="likelihood",
                weight=2,
                reason=vendor.incident_history_notes or "This vendor has a known prior security incident.",
            )
        )

    if vendor.subprocessors.strip():
        likelihood += 1
        factors.append(
            VendorRiskFactor(
                name="Uses subprocessors",
                axis="likelihood",
                weight=1,
                reason=(
                    f"Vendor relies on subprocessors ({vendor.subprocessors}), extending the data "
                    "supply chain."
                ),
            )
        )

    impact += _CRITICALITY_BASE_IMPACT.get(vendor.business_criticality.value, 1) - 1
    factors.append(
        VendorRiskFactor(
            name=f"Business criticality: {vendor.business_criticality.value}",
            axis="impact",
            weight=_CRITICALITY_BASE_IMPACT.get(vendor.business_criticality.value, 1),
            reason=(
                f"This vendor relationship is classified as {vendor.business_criticality.value} "
                "criticality."
            ),
        )
    )

    classification_bonus = _CLASSIFICATION_IMPACT_BONUS.get(vendor.data_classification_handled.value, 0)
    if classification_bonus:
        impact += classification_bonus
        factors.append(
            VendorRiskFactor(
                name=f"Data classification handled: {vendor.data_classification_handled.value}",
                axis="impact",
                weight=classification_bonus,
                reason=f"Vendor processes {vendor.data_classification_handled.value} data.",
            )
        )

    if not vendor.exit_strategy_defined:
        impact += 1
        factors.append(
            VendorRiskFactor(
                name="No defined exit strategy",
                axis="impact",
                weight=1,
                reason=(
                    "No documented plan exists for migrating away from this vendor if needed - "
                    "vendor lock-in risk."
                ),
            )
        )

    likelihood = min(likelihood, 5)
    impact = min(impact, 5)
    score = likelihood * impact
    rating = _rating_for_score(score)

    return VendorRiskResult(
        likelihood=likelihood,
        impact=impact,
        score=score,
        rating=rating,
        contributing_factors=factors,
        recommendation=RECOMMENDATION_FOR_RATING[rating],
    )


def create_vendor(db: Session, data: dict) -> Vendor:
    vendor = Vendor(**data)
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


def list_vendors(db: Session) -> list[Vendor]:
    return db.query(Vendor).order_by(Vendor.name).all()


def get_vendor(db: Session, vendor_id: int) -> Vendor | None:
    return db.get(Vendor, vendor_id)


def run_assessment(db: Session, vendor: Vendor) -> VendorAssessment:
    result = assess_vendor(vendor)
    assessment = VendorAssessment(
        vendor_id=vendor.id,
        likelihood=result.likelihood,
        impact=result.impact,
        score=result.score,
        rating=result.rating,
        contributing_factors=[
            {"name": f.name, "axis": f.axis, "weight": f.weight, "reason": f.reason}
            for f in result.contributing_factors
        ],
        recommendation=result.recommendation,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def latest_assessment(db: Session, vendor_id: int) -> VendorAssessment | None:
    return (
        db.query(VendorAssessment)
        .filter(VendorAssessment.vendor_id == vendor_id)
        .order_by(VendorAssessment.assessed_at.desc())
        .first()
    )
