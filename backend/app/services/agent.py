"""AI agent blast-radius assessment (Section 27). See
docs/decisions/0009-agent-blast-radius-not-reusing-risk-engine.md for why
this is a parallel scorer rather than a forced reuse of app/risk_engine/.
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.agent import AgentAssessment, AIAgent, AutonomyLevel

_AUTONOMY_LIKELIHOOD_WEIGHT = {
    AutonomyLevel.OBSERVATION_ONLY: 0,
    AutonomyLevel.HUMAN_APPROVAL_REQUIRED: 0,
    AutonomyLevel.AUTONOMOUS_WITHIN_GUARDRAILS: 1,
    AutonomyLevel.FULLY_AUTONOMOUS: 2,
}

RATING_BANDS = [(1, 4, "Low"), (5, 9, "Moderate"), (10, 16, "High"), (17, 25, "Critical")]
RECOMMENDATION_FOR_RATING = {
    "Low": "Approve for current scope",
    "Moderate": "Approve with additional guardrails",
    "High": "Require human-in-the-loop before any irreversible action",
    "Critical": "Halt autonomous operation pending governance review",
}


def _rating_for_score(score: int) -> str:
    for low, high, rating in RATING_BANDS:
        if low <= score <= high:
            return rating
    return "Critical"


@dataclass
class AgentBlastRadiusFactor:
    name: str
    axis: str
    weight: int
    reason: str


@dataclass
class AgentBlastRadiusResult:
    likelihood: int
    impact: int
    score: int
    rating: str
    contributing_factors: list[AgentBlastRadiusFactor] = field(default_factory=list)
    recommendation: str = ""


def assess_agent(agent: AIAgent) -> AgentBlastRadiusResult:
    factors: list[AgentBlastRadiusFactor] = []
    likelihood = 1
    impact = 1

    autonomy_weight = _AUTONOMY_LIKELIHOOD_WEIGHT.get(agent.autonomy_level, 0)
    if autonomy_weight:
        likelihood += autonomy_weight
        factors.append(
            AgentBlastRadiusFactor(
                name=f"Autonomy level: {agent.autonomy_level.value}",
                axis="likelihood",
                weight=autonomy_weight,
                reason=f"This agent operates at '{agent.autonomy_level.value}' autonomy.",
            )
        )

    if not agent.requires_human_approval:
        likelihood += 1
        factors.append(
            AgentBlastRadiusFactor(
                name="No human approval required",
                axis="likelihood",
                weight=1,
                reason="The agent can act without a human confirming the action first.",
            )
        )

    if not agent.guardrails_description.strip():
        likelihood += 1
        factors.append(
            AgentBlastRadiusFactor(
                name="No documented guardrails",
                axis="likelihood",
                weight=1,
                reason="No documented constraints limit what the agent can attempt.",
            )
        )

    if agent.can_take_irreversible_actions:
        impact += 2
        factors.append(
            AgentBlastRadiusFactor(
                name="Can take irreversible actions",
                axis="impact",
                weight=2,
                reason="A manipulated or malfunctioning run cannot simply be undone.",
            )
        )

    if agent.can_initiate_financial_transactions:
        impact += 2
        factors.append(
            AgentBlastRadiusFactor(
                name="Can initiate financial transactions",
                axis="impact",
                weight=2,
                reason="A manipulated or malfunctioning run has direct financial consequences.",
            )
        )

    if len(agent.tools_available) > 2:
        impact += 1
        factors.append(
            AgentBlastRadiusFactor(
                name="Broad tool access",
                axis="impact",
                weight=1,
                reason=f"Access to {len(agent.tools_available)} tools widens what a bad run can affect.",
            )
        )

    likelihood = min(likelihood, 5)
    impact = min(impact, 5)
    score = likelihood * impact
    rating = _rating_for_score(score)

    return AgentBlastRadiusResult(
        likelihood=likelihood,
        impact=impact,
        score=score,
        rating=rating,
        contributing_factors=factors,
        recommendation=RECOMMENDATION_FOR_RATING[rating],
    )


def create_agent(db: Session, data: dict) -> AIAgent:
    agent = AIAgent(**data)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def list_agents(db: Session) -> list[AIAgent]:
    return db.query(AIAgent).order_by(AIAgent.name).all()


def get_agent(db: Session, agent_id: int) -> AIAgent | None:
    return db.get(AIAgent, agent_id)


def run_assessment(db: Session, agent: AIAgent) -> AgentAssessment:
    result = assess_agent(agent)
    assessment = AgentAssessment(
        agent_id=agent.id,
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


def latest_assessment(db: Session, agent_id: int) -> AgentAssessment | None:
    return (
        db.query(AgentAssessment)
        .filter(AgentAssessment.agent_id == agent_id)
        .order_by(AgentAssessment.assessed_at.desc())
        .first()
    )
