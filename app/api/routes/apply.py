from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.deps import get_db
from models.apply import Apply
from schemas.apply import ApplyCreate, ApplyRead, ApplyUpdate, ApplyReview
from crud import apply as crud_apply
from common.decorators import log_exceptions


router = APIRouter()


@router.get("/list", response_model=list[ApplyRead])
@log_exceptions
def list_applies(
    db: Session = Depends(get_db),
    begin: int = Query(0, ge=0, description="起始位置"),
    length: int = Query(20, ge=1, le=100, description="返回记录数"),
):
    """获取申请列表"""
    applies = crud_apply.get_applies(db, skip=begin, limit=length)
    apply_data = [ApplyRead.model_validate(apply).model_dump(mode='json') for apply in applies]
    total = db.query(Apply).count()
    return JSONResponse(
        content={"message": "success", "data": {"list": apply_data, "total": total}},
        status_code=200
    )


@router.post("/create", response_model=ApplyRead, status_code=status.HTTP_201_CREATED)
@log_exceptions
def create_apply(payload: ApplyCreate, db: Session = Depends(get_db)):
    """创建申请"""
    apply = crud_apply.create_apply(db, apply=payload)
    return JSONResponse(
        content={"message": "申请创建成功", "data": ApplyRead.model_validate(apply).model_dump(mode='json')},
        status_code=200
    )


@router.get("/info", response_model=ApplyRead)
@log_exceptions
def get_apply(
    apply_id: str = Query(..., description="申请ID"),
    db: Session = Depends(get_db)
):
    """获取申请详情"""
    apply = crud_apply.get_apply(db, apply_id=apply_id)
    if not apply:
        raise HTTPException(status_code=404, detail="申请不存在")
    return apply


@router.post("/update", response_model=ApplyRead)
@log_exceptions
def update_apply(payload: ApplyUpdate, db: Session = Depends(get_db)):
    """更新申请（仅限待审批状态）"""
    apply = crud_apply.update_apply(db, apply_id=payload.apply_id, apply=payload)
    if not apply:
        return JSONResponse(
            content={"message": "申请不存在或已审批，无法更新", "data": {"apply_id": payload.apply_id}, "success": False},
            status_code=400,
        )
    return JSONResponse(
        content={"message": "更新成功", "data": {"apply_id": payload.apply_id}, "success": True},
        status_code=200,
    )


@router.post("/review", response_model=ApplyRead)
@log_exceptions
def review_apply(payload: ApplyReview, db: Session = Depends(get_db)):
    """审批申请"""
    apply = crud_apply.review_apply(db, apply_review=payload)
    if not apply:
        return JSONResponse(
            content={"message": "申请不存在或已审批", "data": {"apply_id": payload.apply_id}, "success": False},
            status_code=400,
        )
    return JSONResponse(
        content={
            "message": f"审批{'通过' if payload.status == 'approved' else '拒绝'}",
            "data": ApplyRead.model_validate(apply).model_dump(mode='json'),
            "success": True
        },
        status_code=200,
    )


@router.post("/{apply_id}/delete")
@log_exceptions
def delete_apply(apply_id: str, db: Session = Depends(get_db)):
    """删除申请（逻辑删除）"""
    success = crud_apply.delete_apply(db, apply_id=apply_id)
    if not success:
        raise HTTPException(status_code=404, detail="申请不存在")
    return JSONResponse(
        content={"message": "删除成功", "success": True},
        status_code=200
    )


@router.get("/user/{user_id}", response_model=list[ApplyRead])
@log_exceptions
def get_applies_by_user(
    user_id: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """获取某用户的申请列表"""
    applies = crud_apply.get_applies_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return applies


@router.get("/sample/{sample_id}", response_model=list[ApplyRead])
@log_exceptions
def get_applies_by_sample(
    sample_id: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """获取某样本的申请列表"""
    applies = crud_apply.get_applies_by_sample(db, sample_id=sample_id, skip=skip, limit=limit)
    return applies


@router.get("/status/{status_value}", response_model=list[ApplyRead])
@log_exceptions
def get_applies_by_status(
    status_value: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """根据状态获取申请列表（pending/approved/rejected）"""
    if status_value not in ["pending", "approved", "rejected"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    applies = crud_apply.get_applies_by_status(db, status=status_value, skip=skip, limit=limit)
    return applies
