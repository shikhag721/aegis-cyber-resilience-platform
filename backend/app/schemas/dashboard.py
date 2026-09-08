from pydantic import BaseModel, ConfigDict


class ExecutiveSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assets_total: int
    assets_by_criticality: dict[str, int]

    risks_open: int
    risks_by_residual_rating: dict[str, int]

    vulnerabilities_open: int
    vulnerabilities_overdue: int
    vulnerabilities_known_exploited_open: int

    iam_findings_total: int
    iam_findings_critical: int
    cloud_findings_open: int
    appsec_findings_open: int
    secrets_open: int

    incidents_open: int
    incidents_open_high_or_critical: int

    control_gaps_total: int
    control_gaps_critical: int

    vendors_high_or_critical: int
    data_security_findings: int
    continuity_findings: int

    ai_governance_gaps: int
    ai_governance_gaps_critical: int
    rag_findings: int
    agents_high_or_critical: int


class ReportHighlightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str
    title: str
    severity: str
    detail: str


class ExecutiveReportRead(BaseModel):
    generated_at: str
    summary: ExecutiveSummaryRead
    top_risks: list[ReportHighlightRead]
    top_control_gaps: list[ReportHighlightRead]
    top_ai_findings: list[ReportHighlightRead]
    recommended_actions: list[str]
