from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from backend.database import SessionLocal
from backend.models import Speisen, Restaurant
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Speisekarten API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"] for Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Speisekarten API is running"}

@app.get("/restaurants")
def list_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).all()
    return [{"r_ID": r.r_ID, "Name": r.Name} for r in restaurants]

@app.get("/menu")
def get_menu_for_day(
    date_str: str = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")
    else:
        target_date = date.today()

    dishes = (
        db.query(Speisen, Restaurant)
        .join(Restaurant, Speisen.r_ID == Restaurant.r_ID)
        .filter(Speisen.Datum == target_date)
        .order_by(Restaurant.Name)
        .all()
    )

    if not dishes:
        raise HTTPException(status_code=404, detail=f"No dishes found for {target_date}")

    return [
        {
            "s_ID": s.s_ID,
            "Name": s.Name,
            "Preis": s.Preis,
            "Datum": s.Datum,
            "r_ID": r.r_ID,
            "Restaurant": r.Name,
        }
        for s, r in dishes
    ]
