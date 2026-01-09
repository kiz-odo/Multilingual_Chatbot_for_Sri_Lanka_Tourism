"""
Feedback API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from backend.app.models.feedback import Feedback, FeedbackCreate, FeedbackResponse, FeedbackStats
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user
from backend.app.core.sanitize import sanitize_html, sanitize_text

router = APIRouter()


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Submit feedback
    
    - Sanitizes user input to prevent XSS attacks
    """
    # Sanitize feedback content
    feedback_dict = feedback_data.dict()
    if 'message' in feedback_dict:
        feedback_dict['message'] = sanitize_html(feedback_dict['message'])
    if 'subject' in feedback_dict:
        feedback_dict['subject'] = sanitize_text(feedback_dict['subject'])
    
    feedback = Feedback(**feedback_dict)
    
    if current_user:
        feedback.user_id = str(current_user.id)
        feedback.user_name = current_user.full_name or current_user.username
        feedback.user_email = current_user.email
    
    await feedback.save()
    return FeedbackResponse(**feedback.dict())


@router.get("/", response_model=List[FeedbackResponse])
async def get_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's feedback (user must be authenticated)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    feedback_list = await Feedback.find(
        Feedback.user_id == str(current_user.id)
    ).sort(-Feedback.created_at).skip(skip).limit(limit).to_list()
    
    return [FeedbackResponse(**feedback.dict()) for feedback in feedback_list]


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback_by_id(
    feedback_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific feedback"""
    try:
        feedback = await Feedback.get(feedback_id)
        
        # Check if user owns this feedback or is admin
        if feedback.user_id != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FeedbackResponse(**feedback.dict())
    except:
        raise HTTPException(status_code=404, detail="Feedback not found")
