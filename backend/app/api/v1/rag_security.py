from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models.user import ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER
from app.schemas.rag import RAGFindingRead, RAGPipelineCreate, RAGPipelineRead
from app.services import rag as rag_service

router = APIRouter(prefix="/rag-security", tags=["rag-security"])

READ_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST, ROLE_VIEWER)
WRITE_ROLES = (ROLE_ADMIN, ROLE_RISK_ANALYST)

require_read = Depends(require_role(*READ_ROLES))
require_write = Depends(require_role(*WRITE_ROLES))


@router.get("/pipelines", response_model=list[RAGPipelineRead])
def list_pipelines(db: Session = Depends(get_db), _user=require_read):
    return rag_service.list_rag_pipelines(db)


@router.post("/pipelines", response_model=RAGPipelineRead, status_code=201)
def create_pipeline(payload: RAGPipelineCreate, db: Session = Depends(get_db), _user=require_write):
    return rag_service.create_rag_pipeline(db, payload.model_dump())


@router.get("/pipelines/{pipeline_id}", response_model=RAGPipelineRead)
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db), _user=require_read):
    pipeline = rag_service.get_rag_pipeline(db, pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="RAG pipeline not found")
    return pipeline


@router.get("/gap-analysis", response_model=list[RAGFindingRead])
def gap_analysis(db: Session = Depends(get_db), _user=require_read):
    return rag_service.analyze_all_rag_pipelines(db)
