from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

Base = declarative_base()


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    user_email = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("product_id", "user_email", name="uq_review_product_user"),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>"


class ReviewBase(BaseModel):
    product_id: int
    user_email: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewSummary(BaseModel):
    product_id: int
    total_reviews: int
    avg_rating: float
    reviews: List[ReviewRead]
