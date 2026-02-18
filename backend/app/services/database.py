"""Neon PostgreSQL Database Service for conversations, analytics, and ratings."""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager
from app.config import settings

Base = declarative_base()


# Database Models
class ConversationModel(Base):
    """Conversation table."""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = Column(Integer, default=0)
    language = Column(String, default="en")
    total_response_time_ms = Column(Float, default=0.0)
    average_response_time_ms = Column(Float, default=0.0)
    total_queries = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class MessageModel(Base):
    """Message table."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sources = Column(JSON, nullable=True)
    response_time_ms = Column(Float, nullable=True)


class RatingModel(Base):
    """Rating table."""
    __tablename__ = "ratings"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, index=True)
    conversation_id = Column(String, index=True)
    rating = Column(Integer)  # 1-5 stars
    timestamp = Column(DateTime, default=datetime.utcnow)


class FeedbackModel(Base):
    """Feedback table."""
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, index=True)
    conversation_id = Column(String, index=True)
    feedback_type = Column(String)  # 'helpful', 'not_helpful', 'incorrect', etc.
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DatabaseService:
    """Service for managing PostgreSQL database connections."""
    
    _instance = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize()
    
    def _initialize(self):
        """Initialize database connection."""
        if not settings.neon_database_url:
            print("[WARNING] NEON_DATABASE_URL not configured. Database features disabled.")
            return
        
        try:
            # Clean up the connection string (remove quotes if present)
            db_url = settings.neon_database_url.strip("'\"")
            
            # Create engine with connection timeout
            self._engine = create_engine(
                db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args={"connect_timeout": 5}  # 5 second timeout
            )
            
            # Create session factory
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            # Test connection with timeout
            from sqlalchemy import text
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create tables
            Base.metadata.create_all(bind=self._engine)
            print("[OK] Connected to Neon PostgreSQL database")
            print("[OK] Database tables created/verified")
            
        except Exception as e:
            print(f"[WARNING] Neon database connection failed: {e}")
            print("[INFO] Continuing with Azure Blob Storage fallback")
            self._engine = None
            self._SessionLocal = None
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._engine is not None
    
    @contextmanager
    def get_session(self):
        """Get a database session."""
        if not self._SessionLocal:
            raise RuntimeError("Database not initialized")
        
        session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # Conversation methods
    def create_conversation(self, conversation_id: str, title: str = "New Conversation", language: str = "en") -> Optional[str]:
        """Create a new conversation."""
        if not self.is_connected:
            return None
        
        with self.get_session() as session:
            conv = ConversationModel(
                id=conversation_id,
                title=title,
                language=language,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conv)
            return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get a conversation by ID."""
        if not self.is_connected:
            return None
        
        with self.get_session() as session:
            conv = session.query(ConversationModel).filter_by(id=conversation_id).first()
            if conv:
                return {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at,
                    "updated_at": conv.updated_at,
                    "message_count": conv.message_count,
                    "language": conv.language,
                    "total_response_time_ms": conv.total_response_time_ms,
                    "average_response_time_ms": conv.average_response_time_ms,
                    "total_queries": conv.total_queries,
                    "is_active": conv.is_active
                }
            return None
    
    def update_conversation(self, conversation_id: str, **kwargs) -> bool:
        """Update conversation fields."""
        if not self.is_connected:
            return False
        
        with self.get_session() as session:
            conv = session.query(ConversationModel).filter_by(id=conversation_id).first()
            if conv:
                for key, value in kwargs.items():
                    if hasattr(conv, key):
                        setattr(conv, key, value)
                conv.updated_at = datetime.utcnow()
                return True
            return False
    
    def list_conversations(self, limit: int = 50) -> List[dict]:
        """List recent conversations."""
        if not self.is_connected:
            return []
        
        with self.get_session() as session:
            convs = session.query(ConversationModel).order_by(
                ConversationModel.updated_at.desc()
            ).limit(limit).all()
            
            return [{
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "message_count": c.message_count,
                "language": c.language,
                "total_response_time_ms": c.total_response_time_ms,
                "average_response_time_ms": c.average_response_time_ms,
                "total_queries": c.total_queries,
                "is_active": c.is_active
            } for c in convs]
    
    # Message methods
    def add_message(self, message_id: str, conversation_id: str, role: str, content: str,
                   sources: Optional[List] = None, response_time_ms: Optional[float] = None) -> bool:
        """Add a message to a conversation."""
        if not self.is_connected:
            return False
        
        with self.get_session() as session:
            msg = MessageModel(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                sources=sources,
                response_time_ms=response_time_ms,
                timestamp=datetime.utcnow()
            )
            session.add(msg)
            
            # Update conversation stats
            conv = session.query(ConversationModel).filter_by(id=conversation_id).first()
            if conv:
                conv.message_count += 1
                conv.updated_at = datetime.utcnow()
                if role == "user":
                    conv.total_queries += 1
                if response_time_ms and response_time_ms > 0:
                    conv.total_response_time_ms += response_time_ms
                    if conv.total_queries > 0:
                        conv.average_response_time_ms = conv.total_response_time_ms / conv.total_queries
            
            return True
    
    def get_conversation_messages(self, conversation_id: str) -> List[dict]:
        """Get all messages for a conversation."""
        if not self.is_connected:
            return []
        
        with self.get_session() as session:
            messages = session.query(MessageModel).filter_by(
                conversation_id=conversation_id
            ).order_by(MessageModel.timestamp).all()
            
            return [{
                "id": m.id,
                "conversation_id": m.conversation_id,
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                "sources": m.sources,
                "response_time_ms": m.response_time_ms
            } for m in messages]
    
    # Rating methods
    def add_rating(self, rating_id: str, message_id: str, conversation_id: str, rating: int) -> bool:
        """Add a rating for a message."""
        if not self.is_connected:
            return False
        
        with self.get_session() as session:
            r = RatingModel(
                id=rating_id,
                message_id=message_id,
                conversation_id=conversation_id,
                rating=rating,
                timestamp=datetime.utcnow()
            )
            session.add(r)
            return True
    
    def get_average_rating(self, days: int = 30) -> float:
        """Get average rating over time period."""
        if not self.is_connected:
            return 0.0
        
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            from sqlalchemy import func
            result = session.query(func.avg(RatingModel.rating)).filter(
                RatingModel.timestamp >= cutoff
            ).scalar()
            return float(result) if result else 0.0
    
    # Feedback methods
    def add_feedback(self, feedback_id: str, message_id: str, conversation_id: str,
                    feedback_type: str, comment: Optional[str] = None) -> bool:
        """Add feedback for a message."""
        if not self.is_connected:
            return False
        
        with self.get_session() as session:
            fb = FeedbackModel(
                id=feedback_id,
                message_id=message_id,
                conversation_id=conversation_id,
                feedback_type=feedback_type,
                comment=comment,
                timestamp=datetime.utcnow()
            )
            session.add(fb)
            return True
    
    # Analytics methods
    def get_analytics_summary(self, days: int = 30) -> dict:
        """Get analytics summary."""
        if not self.is_connected:
            return {}
        
        from datetime import timedelta
        from sqlalchemy import func
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            # Total conversations
            total_convs = session.query(func.count(ConversationModel.id)).filter(
                ConversationModel.updated_at >= cutoff
            ).scalar() or 0
            
            # Total messages
            total_msgs = session.query(func.count(MessageModel.id)).filter(
                MessageModel.timestamp >= cutoff
            ).scalar() or 0
            
            # Average response time
            avg_response = session.query(func.avg(MessageModel.response_time_ms)).filter(
                MessageModel.timestamp >= cutoff,
                MessageModel.response_time_ms > 0
            ).scalar() or 0
            
            # Average rating
            avg_rating = session.query(func.avg(RatingModel.rating)).filter(
                RatingModel.timestamp >= cutoff
            ).scalar()
            
            return {
                "total_conversations": total_convs,
                "total_messages": total_msgs,
                "average_response_time_ms": float(avg_response),
                "average_rating": float(avg_rating) if avg_rating else None,
                "period_days": days
            }


# Global instance
db_service = DatabaseService()
