"""
Forum API endpoints
Community posts and discussions
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId

from backend.app.models.user import User, UserRole
from backend.app.core.auth import get_current_active_user, get_optional_user
from backend.app.core.sanitize import sanitize_html, sanitize_text, sanitize_list
from fastapi import Request
from backend.app.middleware.error_handler import NotFoundException, BadRequestException

router = APIRouter(prefix="/forum", tags=["Forum"])


# Request/Response Models
class Comment(BaseModel):
    """Comment model"""
    id: Optional[str] = None
    post_id: str
    author_id: str
    author_username: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    likes: int = 0
    is_edited: bool = False


class Post(BaseModel):
    """Forum post model"""
    id: Optional[str] = None
    title: str
    content: str
    author_id: str
    author_username: str
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    views: int = 0
    likes: int = 0
    comment_count: int = 0
    is_pinned: bool = False
    is_locked: bool = False


class PostCreate(BaseModel):
    """Create post request"""
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    category: str = "general"
    tags: List[str] = Field(default_factory=list, max_items=10)


class PostUpdate(BaseModel):
    """Update post request"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    tags: Optional[List[str]] = Field(None, max_items=10)


class CommentCreate(BaseModel):
    """Create comment request"""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    """Update comment request"""
    content: str = Field(..., min_length=1, max_length=2000)


# Mock database - In production, use MongoDB models
POSTS_DB = []
COMMENTS_DB = []


@router.get("/posts", response_model=List[Post])
async def list_posts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    List forum posts
    
    - Returns all posts (public)
    - Can filter by category, tag, or author
    - Supports pagination
    """
    posts = POSTS_DB.copy()
    
    if category:
        posts = [p for p in posts if p.get("category") == category]
    
    if tag:
        posts = [p for p in posts if tag in p.get("tags", [])]
    
    if author_id:
        posts = [p for p in posts if p.get("author_id") == author_id]
    
    # Sort by created_at (newest first)
    posts.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
    
    # Paginate
    posts = posts[skip:skip + limit]
    
    return [Post(**p) for p in posts]


@router.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new forum post
    
    - Requires authentication
    - Validates content
    - Sanitizes HTML to prevent XSS attacks
    """
    # Sanitize user input to prevent XSS
    sanitized_title = sanitize_text(post_data.title)
    sanitized_content = sanitize_html(post_data.content)
    sanitized_tags = sanitize_list(post_data.tags, strip_tags=True)
    
    post = {
        "id": str(len(POSTS_DB) + 1),
        "title": sanitized_title,
        "content": sanitized_content,
        "author_id": str(current_user.id),
        "author_username": current_user.username,
        "category": post_data.category,
        "tags": sanitized_tags,
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "views": 0,
        "likes": 0,
        "comment_count": 0,
        "is_pinned": False,
        "is_locked": False
    }
    
    POSTS_DB.append(post)
    
    return Post(**post)


@router.get("/posts/{post_id}", response_model=Post)
async def get_post(
    post_id: str,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get post details
    
    - Returns full post information
    - Increments view count
    """
    post = next((p for p in POSTS_DB if p.get("id") == post_id), None)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    # Increment views
    post["views"] = post.get("views", 0) + 1
    
    return Post(**post)


@router.put("/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update post
    
    - Only author or moderator/admin can update
    - Sanitizes HTML to prevent XSS attacks
    """
    post = next((p for p in POSTS_DB if p.get("id") == post_id), None)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    # Check permissions
    if post.get("author_id") != str(current_user.id) and current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this post"
        )
    
    # Update fields with sanitization
    if post_update.title is not None:
        post["title"] = sanitize_text(post_update.title)
    if post_update.content is not None:
        post["content"] = sanitize_html(post_update.content)
    if post_update.tags is not None:
        post["tags"] = sanitize_list(post_update.tags, strip_tags=True)
    
    post["updated_at"] = datetime.utcnow()
    
    return Post(**post)


@router.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete post
    
    - Only author or moderator/admin can delete
    """
    post = next((p for p in POSTS_DB if p.get("id") == post_id), None)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    # Check permissions
    if post.get("author_id") != str(current_user.id) and current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post"
        )
    
    # Remove post and its comments
    POSTS_DB.remove(post)
    COMMENTS_DB[:] = [c for c in COMMENTS_DB if c.get("post_id") != post_id]
    
    return {"message": "Post deleted successfully"}


@router.post("/posts/{post_id}/comments", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Add comment to post
    
    - Requires authentication
    - Sanitizes HTML to prevent XSS attacks
    """
    post = next((p for p in POSTS_DB if p.get("id") == post_id), None)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    if post.get("is_locked"):
        raise BadRequestException("Post is locked, comments are disabled")
    
    # Sanitize comment content
    sanitized_content = sanitize_html(comment_data.content)
    
    comment = {
        "id": str(len(COMMENTS_DB) + 1),
        "post_id": post_id,
        "author_id": str(current_user.id),
        "author_username": current_user.username,
        "content": sanitized_content,
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "likes": 0,
        "is_edited": False
    }
    
    COMMENTS_DB.append(comment)
    
    # Update comment count
    post["comment_count"] = post.get("comment_count", 0) + 1
    
    return Comment(**comment)


@router.get("/posts/{post_id}/comments", response_model=List[Comment])
async def get_post_comments(
    post_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get post comments
    
    - Returns all comments for a post
    - Supports pagination
    """
    post = next((p for p in POSTS_DB if p.get("id") == post_id), None)
    
    if not post:
        raise NotFoundException(f"Post {post_id} not found")
    
    comments = [c for c in COMMENTS_DB if c.get("post_id") == post_id]
    
    # Sort by created_at (oldest first)
    comments.sort(key=lambda x: x.get("created_at", datetime.min))
    
    # Paginate
    comments = comments[skip:skip + limit]
    
    return [Comment(**c) for c in comments]

