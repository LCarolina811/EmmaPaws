from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database_sql import get_db, create_db_and_tables
from models import Review, ReviewCreate, ReviewRead, ReviewSummary

app = FastAPI(title="EmmaPaws — Reseñas de Productos")
router = APIRouter()


@app.on_event("startup")
def startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"message": "Servicio de Reseñas de EmmaPaws funcionando."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/reviews/{product_id}", response_model=ReviewSummary)
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    avg = round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else 0.0
    return ReviewSummary(
        product_id=product_id,
        total_reviews=len(reviews),
        avg_rating=avg,
        reviews=reviews,
    )


@router.post("/reviews/", response_model=ReviewRead, status_code=201)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    db_review = Review(**review.model_dump())
    db.add(db_review)
    try:
        db.commit()
        db.refresh(db_review)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una reseña de este usuario para ese producto"
        )
    return db_review


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    db.delete(db_review)
    db.commit()


app.include_router(router, prefix="/api/v1")
