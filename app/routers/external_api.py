from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND
from sqlalchemy.orm import Session
from app.crud import get_transcription_by_external_id
from ..dependencies import get_db
from ..schemas_external import ExternalJobCreate, JobQueuedResp, JobStatusResp
from ..auth_api import get_current_service_user
from ..tasks import enqueue_external_job

router = APIRouter(prefix="/v1", tags=["external-api"])

@router.post("/jobs", response_model=JobQueuedResp, status_code=HTTP_202_ACCEPTED)
def create_job(
    payload: ExternalJobCreate,
    db: Session = Depends(get_db),
    service_user=Depends(get_current_service_user),
):
    job = create_external_job(db, service_user, payload)
    
    # بررسی وجود تابع enqueue_external_job
    if not hasattr(enqueue_external_job, 'delay'):
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job queue system not properly configured"
        )
    
    enqueue_external_job.delay(
        job_id=job.id,
        file_url=payload.file_url,
        language=payload.language,
        mode=payload.mode,
        callback_url=payload.callback_url,
    )
    return JobQueuedResp(
        job_id=job.external_id,
        status="queued",
        estimated_cost=job.estimated_cost,
    )

@router.get("/jobs/{external_id}", response_model=JobStatusResp)
def job_status(
    external_id: str,
    db: Session = Depends(get_db),
    service_user=Depends(get_current_service_user),
):
    job = get_transcription_by_external_id(db, external_id, owner_id=service_user.id)
    if not job:
        HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return JobStatusResp.from_orm(job)