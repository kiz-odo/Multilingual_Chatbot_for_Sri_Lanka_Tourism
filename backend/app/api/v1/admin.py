"""
Admin API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from backend.app.models.user import User, UserRole
from backend.app.models.feedback import Feedback, FeedbackStats
from backend.app.core.auth import get_current_active_user
from backend.app.core.config import settings

router = APIRouter(tags=["Admin"])


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/overview")
async def get_admin_overview(admin_user: User = Depends(get_admin_user)):
    """Get system overview (alias for /dashboard)"""
    return await get_admin_dashboard(admin_user)

@router.get("/dashboard")
async def get_admin_dashboard(admin_user: User = Depends(get_admin_user)):
    """Get admin dashboard statistics"""
    
    # Get basic counts
    total_users = await User.find(User.is_active == True).count()
    total_feedback = await Feedback.find().count()
    
    from backend.app.models.attraction import Attraction
    from backend.app.models.restaurant import Restaurant
    from backend.app.models.hotel import Hotel
    from backend.app.models.event import Event
    
    total_attractions = await Attraction.find(Attraction.is_active == True).count()
    total_restaurants = await Restaurant.find(Restaurant.is_active == True).count()
    total_hotels = await Hotel.find(Hotel.is_active == True).count()
    total_events = await Event.find().count()
    
    return {
        "users": {
            "total": total_users,
            "active": total_users  # All counted users are active
        },
        "content": {
            "attractions": total_attractions,
            "restaurants": total_restaurants,
            "hotels": total_hotels,
            "events": total_events
        },
        "feedback": {
            "total": total_feedback
        }
    }


@router.get("/feedback", response_model=List[dict])
async def get_all_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_admin_user)
):
    """Get all feedback for admin review"""
    
    feedback_list = await Feedback.find().sort(-Feedback.created_at).skip(skip).limit(limit).to_list()
    
    return [feedback.dict() for feedback in feedback_list]


@router.get("/users", response_model=List[dict])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_user: User = Depends(get_admin_user)
):
    """Get all users for admin management"""
    
    users = await User.find().sort(-User.created_at).skip(skip).limit(limit).to_list()
    
    return [user.to_dict() for user in users]


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user_update: Dict[str, Any] = Body(...),
    admin_user: User = Depends(get_admin_user)
):
    """Update user details (Admin only)"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update allowed fields
        if "role" in user_update:
            user.role = UserRole(user_update["role"])
        if "is_active" in user_update:
            user.is_active = user_update["is_active"]
        if "is_verified" in user_update:
            user.is_verified = user_update["is_verified"]
        if "username" in user_update:
            user.username = user_update["username"]
        if "email" in user_update:
            user.email = user_update["email"]
        
        user.updated_at = datetime.utcnow()
        await user.save()
        
        return {"message": "User updated successfully", "user": user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid value: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Delete a user (Admin only)"""
    try:
        user = await User.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent self-deletion
        if str(user.id) == str(admin_user.id):
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        await user.delete()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    admin_user: User = Depends(get_admin_user)
):
    """Get analytics data"""
    try:
        from backend.app.models.conversation import Conversation
        from backend.app.models.itinerary import TripItinerary
        
        # Get conversation stats
        total_conversations = await Conversation.find().count()
        recent_conversations = await Conversation.find(
            Conversation.created_at >= datetime.utcnow().replace(day=1)  # This month
        ).count()
        
        # Get itinerary stats
        total_itineraries = await TripItinerary.find().count()
        
        # Get user growth
        new_users_this_month = await User.find(
            User.created_at >= datetime.utcnow().replace(day=1)
        ).count()
        
        return {
            "conversations": {
                "total": total_conversations,
                "this_month": recent_conversations
            },
            "itineraries": {
                "total": total_itineraries
            },
            "users": {
                "new_this_month": new_users_this_month
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")


@router.get("/logs", response_model=List[Dict[str, Any]])
async def get_system_logs(
    level: Optional[str] = Query(None, description="Log level filter (DEBUG, INFO, WARNING, ERROR)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of log entries"),
    admin_user: User = Depends(get_admin_user)
):
    """Get system logs"""
    import os
    import json
    
    try:
        log_file = settings.LOG_FILE or "logs/app.log"
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Get last N lines
                for line in lines[-limit:]:
                    try:
                        log_entry = json.loads(line.strip())
                        if level and log_entry.get("level") != level.upper():
                            continue
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        # Skip non-JSON lines
                        continue
        
        return logs[-limit:]  # Return most recent logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")


class ContentModerationRequest(BaseModel):
    content_id: str
    content_type: str  # "forum_post", "comment", "review", etc.
    action: str  # "approve", "reject", "flag"
    reason: Optional[str] = None


@router.post("/content/moderate", status_code=status.HTTP_200_OK)
async def moderate_content(
    moderation: ContentModerationRequest,
    admin_user: User = Depends(get_admin_user)
):
    """Moderate content (forum posts, comments, etc.)"""
    try:
        from backend.app.models.forum import ForumPost
        
        if moderation.content_type == "forum_post":
            post = await ForumPost.get(moderation.content_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            
            if moderation.action == "approve":
                post.status = "published"
            elif moderation.action == "reject":
                post.status = "moderated"
            elif moderation.action == "flag":
                # Flag for review
                post.status = "moderated"
            
            post.updated_at = datetime.utcnow()
            await post.save()
            
            return {
                "message": f"Post {moderation.action}d successfully",
                "post_id": moderation.content_id,
                "status": post.status
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {moderation.content_type}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moderating content: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def get_admin_health_check(admin_user: User = Depends(get_admin_user)):
    """Detailed health check for admin (includes system metrics)"""
    try:
        from backend.app.core.database import db
        import redis.asyncio as redis
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        # Check MongoDB
        try:
            await db.client.admin.command("ping")
            health_status["services"]["mongodb"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["mongodb"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check Redis
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            await redis_client.close()
            health_status["services"]["redis"] = {"status": "healthy"}
        except Exception as e:
            health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
            health_status["status"] = "degraded"
        
        # Check LLM services
        from backend.app.services.llm_service import get_llm_service
        llm_service = get_llm_service()
        await llm_service.ensure_initialized()
        health_status["services"]["llm"] = {
            "status": "healthy" if llm_service.enabled else "disabled",
            "enabled": llm_service.enabled
        }
        
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


class MaintenanceModeRequest(BaseModel):
    enabled: bool
    message: Optional[str] = None


# Global maintenance mode flag (in production, use Redis or database)
_maintenance_mode = False
_maintenance_message = "System is under maintenance. Please check back later."


@router.post("/maintenance", status_code=status.HTTP_200_OK)
async def toggle_maintenance_mode(
    request: MaintenanceModeRequest,
    admin_user: User = Depends(get_admin_user)
):
    """Toggle maintenance mode"""
    global _maintenance_mode, _maintenance_message
    
    _maintenance_mode = request.enabled
    if request.message:
        _maintenance_message = request.message
    
    return {
        "maintenance_mode": _maintenance_mode,
        "message": _maintenance_message,
        "updated_by": admin_user.username,
        "updated_at": datetime.utcnow().isoformat()
    }


@router.put("/feedback/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: str,
    status: str,
    admin_user: User = Depends(get_admin_user)
):
    """Update feedback status"""
    try:
        feedback = await Feedback.get(feedback_id)
        feedback.status = status
        feedback.updated_at = datetime.utcnow()
        await feedback.save()
        
        return {"message": "Feedback status updated successfully"}
    except:
        raise HTTPException(status_code=404, detail="Feedback not found")


# ================== Circuit Breaker Management ==================

@router.get("/circuit-breakers")
async def get_circuit_breaker_status(admin_user: User = Depends(get_admin_user)):
    """
    Get status of all circuit breakers for external services
    
    Returns status, failure counts, and recovery info for each service
    """
    from backend.app.core.circuit_breaker import get_all_circuit_breaker_status
    
    return {
        "circuit_breakers": get_all_circuit_breaker_status(),
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.post("/circuit-breakers/{service_name}/reset")
async def reset_circuit_breaker_endpoint(
    service_name: str,
    admin_user: User = Depends(get_admin_user)
):
    """
    Manually reset a circuit breaker to CLOSED state
    
    Use this to recover from a service outage after the underlying issue is fixed
    """
    from backend.app.core.circuit_breaker import reset_circuit_breaker
    
    success = reset_circuit_breaker(service_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Circuit breaker for '{service_name}' not found"
        )
    
    return {
        "message": f"Circuit breaker for '{service_name}' reset successfully",
        "service": service_name,
        "new_state": "CLOSED",
        "reset_by": admin_user.username,
        "reset_at": datetime.utcnow().isoformat()
    }


# ================== WebSocket Management ==================

@router.get("/websocket/stats")
async def get_websocket_stats(admin_user: User = Depends(get_admin_user)):
    """Get WebSocket connection statistics"""
    from backend.app.middleware.websocket_security import secure_ws_manager
    
    return {
        "stats": secure_ws_manager.get_stats(),
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.post("/websocket/cleanup")
async def cleanup_websocket_connections(admin_user: User = Depends(get_admin_user)):
    """Manually trigger cleanup of expired WebSocket connections"""
    from backend.app.middleware.websocket_security import secure_ws_manager
    
    await secure_ws_manager.cleanup_expired_connections()
    
    return {
        "message": "WebSocket cleanup completed",
        "stats": secure_ws_manager.get_stats()
    }


# ================== API Version Management ==================

@router.get("/api-versions")
async def get_api_version_info(admin_user: User = Depends(get_admin_user)):
    """Get API version information and deprecated endpoints"""
    from backend.app.middleware.api_versioning import get_version_info, DEPRECATED_ENDPOINTS
    
    return {
        "version_info": get_version_info(),
        "deprecated_endpoints": DEPRECATED_ENDPOINTS
    }

