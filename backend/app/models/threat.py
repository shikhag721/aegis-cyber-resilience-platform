"""Threat modeling and attack-path data model (Section 8 of the project
brief).

Design: a ThreatActor motivates one or more Threats. A Threat is a
reusable catalog entry (e.g. "Credential stuffing against customer login")
that can recur across multiple attack paths. An AttackPath is a concrete,
asset-specific scenario built from ordered AttackPathSteps - this is what
lets the same generic Threat ("Privilege abuse") mean something different
and asset-specific ("...against the Payment Processing Service") in two
different attack paths, matching Section 8's explicit warning: MITRE
technique IDs must be explained in the specific enterprise scenario they
apply to, not just listed.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ThreatActorCategory(StrEnum):
    EXTERNAL_CYBERCRIMINAL = "external_cybercriminal"
    INSIDER_MALICIOUS = "insider_malicious"
    INSIDER_NEGLIGENT = "insider_negligent"
    NATION_STATE = "nation_state"
    HACKTIVIST = "hacktivist"
    THIRD_PARTY = "third_party"


class ThreatActor(Base):
    __tablename__ = "threat_actors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[ThreatActorCategory] = mapped_column(
        Enum(ThreatActorCategory, native_enum=False, length=32)
    )
    motivation: Mapped[str] = mapped_column(String(255))
    sophistication: Mapped[str] = mapped_column(String(20), default="Medium")  # Low/Medium/High
    description: Mapped[str] = mapped_column(Text, default="")


class Threat(Base):
    """A reusable threat catalog entry, optionally linked to a MITRE
    ATT&CK technique. `why_relevant` is mandatory in practice (enforced at
    the service layer) precisely because the brief calls out that quoting
    a MITRE ID with no scenario context is not acceptable threat modeling.
    """

    __tablename__ = "threats"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    threat_actor_id: Mapped[int | None] = mapped_column(ForeignKey("threat_actors.id"), nullable=True)
    mitre_technique_id: Mapped[str | None] = mapped_column(String(20), nullable=True)  # e.g. "T1078"
    mitre_technique_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    why_relevant: Mapped[str] = mapped_column(
        Text, default="", doc="Why this technique matters for THIS environment, not a generic definition."
    )

    threat_actor: Mapped["ThreatActor | None"] = relationship()


class AttackPath(Base):
    """A concrete, asset-specific attack scenario, e.g.
    'Compromised customer credential -> authenticated API access ->
    privilege abuse -> database access -> data exfiltration' (Section 8's
    worked example). Likelihood/impact reuse the same 1-5 scale as
    app/risk_engine/ (Phase 3) so an attack path can be compared on the
    same footing as any other risk.
    """

    __tablename__ = "attack_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    entry_point: Mapped[str] = mapped_column(String(200))  # e.g. "Internet", "Phishing email"
    target_asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    likelihood: Mapped[int] = mapped_column(Integer)  # 1-5
    impact: Mapped[int] = mapped_column(Integer)  # 1-5
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    target_asset: Mapped["Asset"] = relationship()  # noqa: F821
    steps: Mapped[list["AttackPathStep"]] = relationship(
        back_populates="attack_path", order_by="AttackPathStep.sequence", cascade="all, delete-orphan"
    )

    @property
    def score(self) -> int:
        return self.likelihood * self.impact


class AttackPathStep(Base):
    __tablename__ = "attack_path_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    attack_path_id: Mapped[int] = mapped_column(ForeignKey("attack_paths.id"))
    sequence: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(255))
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    threat_id: Mapped[int | None] = mapped_column(ForeignKey("threats.id"), nullable=True)

    attack_path: Mapped["AttackPath"] = relationship(back_populates="steps")
    asset: Mapped["Asset | None"] = relationship()  # noqa: F821
    threat: Mapped["Threat | None"] = relationship()
