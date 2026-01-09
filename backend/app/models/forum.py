"""
Forum Post Model for Community Discussions
"""

from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PostCategory(str, Enum):
    """Forum post categories"""
    GENERAL = "general"
    ATTRACTIONS = "attractions"
    ACCOMMODATION = "accommodation"
    TRANSPORT = "transport"
    FOOD = "food"
    EVENTS = "events"
    SAFETY = "safety"
    TIPS = "tips"
    QUESTIONS = "questions"
    REVIEWS = "reviews"


class Comment(Document):
    """Comment on a forum post"""
    
    post_id: Indexed(str)
    author_id: Indexed(str)
    author_username: str
    content: str = Field(..., min_length=1, max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    likes: int = 0
    liked_by: List[str] = Field(default_factory=list)  # User IDs who liked
    is_edited: bool = False
    is_deleted: bool = False
    
    class Settings:
        name = "forum_comments"
        indexes = [
            "post_id",
            "author_id",
            "created_at",
            [("post_id", 1), ("created_at", -1)]
        ]


class ForumPost(Document):
    """Forum post document model"""
    
    # Basic Information
    title: Indexed(str) = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10, max_length=5000)
    
    # Author
    author_id: Indexed(str)
    author_username: str
    
    # Classification
    category: PostCategory = PostCategory.GENERAL
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    # Engagement
    views: int = 0
    likes: int = 0
    liked_by: List[str] = Field(default_factory=list)  # User IDs who liked
    comment_count: int = 0
    
    # Status
    is_pinned: bool = False
    is_locked: bool = False
    is_deleted: bool = False
    
    # Moderation
    moderated_by: Optional[str] = None  # Moderator/Admin user ID
    moderation_notes: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_posts"
        indexes = [
            "author_id",
            "category",
            "created_at",
            "is_pinned",
            "is_locked",
            [("category", 1), ("created_at", -1)],
            [("author_id", 1), ("created_at", -1)],
            "tags"
        ]
    
    def to_dict(self):
        """Convert post to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "author_id": self.author_id,
            "author_username": self.author_username,
            "category": self.category.value,
            "tags": self.tags,
            "views": self.views,
            "likes": self.likes,
            "comment_count": self.comment_count,
            "is_pinned": self.is_pinned,
            "is_locked": self.is_locked,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_activity_at": self.last_activity_at
        }




