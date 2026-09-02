from pydantic import BaseModel, ConfigDict


class RAGPipelineCreate(BaseModel):
    name: str
    ai_system_id: int | None = None
    data_sources: list[str] = []
    document_level_access_control: bool = False
    retrieved_content_sanitized: bool = False
    allows_untrusted_data_sources: bool = False
    source_content_validated: bool = False
    output_validated_before_use: bool = False
    notes: str = ""


class RAGPipelineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ai_system_id: int | None
    data_sources: list[str]
    document_level_access_control: bool
    retrieved_content_sanitized: bool
    allows_untrusted_data_sources: bool
    source_content_validated: bool
    output_validated_before_use: bool
    notes: str


class RAGFindingRead(BaseModel):
    pipeline_name: str
    root_cause: str
    severity: str
    detail: str
