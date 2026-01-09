"""
User management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from backend.app.models.user import User, UserUpdate, UserResponse
from backend.app.core.auth import get_current_active_user
from backend.app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return UserResponse(**current_user.to_dict())


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user profile"""
    user_service = UserService()
    
    updated_user = await user_service.update_user(str(current_user.id), user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**updated_user.to_dict())


@router.post("/me/favorites/attractions/{attraction_id}")
async def add_favorite_attraction(
    attraction_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Add attraction to user's favorites"""
    user_service = UserService()
    
    updated_user = await user_service.add_favorite_attraction(str(current_user.id), attraction_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Attraction added to favorites"}


@router.delete("/me/favorites/attractions/{attraction_id}")
async def remove_favorite_attraction(
    attraction_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Remove attraction from user's favorites"""
    user_service = UserService()
    
    updated_user = await user_service.remove_favorite_attraction(str(current_user.id), attraction_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Attraction removed from favorites"}


@router.post("/me/visited/{place_id}")
async def add_visited_place(
    place_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Add place to user's visited places"""
    user_service = UserService()
    
    updated_user = await user_service.add_visited_place(str(current_user.id), place_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Place added to visited list"}


@router.get("/me/stats")
async def get_user_stats(current_user: User = Depends(get_current_active_user)):
    """Get user statistics"""
    from backend.app.services.chat_service import ChatService
    
    chat_service = ChatService()
    stats = await chat_service.get_conversation_stats(str(current_user.id))
    
    return {
        "user_stats": current_user.stats.dict(),
        "conversation_stats": stats
    }


@router.get("/me/export")
async def export_user_data(current_user: User = Depends(get_current_active_user)):
    """
    Export all user data in GDPR-compliant format
    
    Returns a JSON object containing all personal data, conversations,
    feedback, and itineraries associated with the user.
    
    GDPR Article 20 - Right to Data Portability
    """
    from backend.app.services.gdpr_export_service import gdpr_export_service
    
    export_data = await gdpr_export_service.export_user_data(str(current_user.id))
    
    return export_data


@router.get("/me/export/download")
async def download_user_data_archive(current_user: User = Depends(get_current_active_user)):
    """
    Download all user data as a ZIP archive
    
    Returns a downloadable ZIP file containing:
    - user_data.json (complete export)
    - personal_info.json
    - conversations.json
    - feedback.json
    - itineraries.json
    - README.md
    
    GDPR Article 20 - Right to Data Portability
    """
    from fastapi.responses import Response
    from backend.app.services.gdpr_export_service import gdpr_export_service
    
    zip_data = await gdpr_export_service.create_export_archive(str(current_user.id))
    
    return Response(
        content=zip_data,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=user_data_export_{current_user.id}.zip"
        }
    )


@router.delete("/me")
async def delete_current_user_account(current_user: User = Depends(get_current_active_user)):
    """Delete current user account (soft delete)"""
    user_service = UserService()
    
    success = await user_service.delete_user(str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Account deleted successfully"}


@router.delete("/me/data")
async def delete_user_data_gdpr(current_user: User = Depends(get_current_active_user)):
    """
    Delete all user data (GDPR Right to Erasure)
    
    This endpoint:
    - Deletes all conversations
    - Deletes all feedback
    - Deletes all itineraries
    - Anonymizes the user account
    
    GDPR Article 17 - Right to Erasure
    """
    from backend.app.services.gdpr_export_service import gdpr_export_service
    
    deletion_summary = await gdpr_export_service.delete_user_data(str(current_user.id))
    
    return {
        "message": "Your data has been deleted",
        "summary": deletion_summary
    }
