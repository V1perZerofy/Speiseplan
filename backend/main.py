from fastapi import FastAPI, Depends, HTTPException, Query, Header, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, date
from backend.database import SessionLocal
from backend.models import Speisen, Restaurant
from fastapi.middleware.cors import CORSMiddleware
from backend.parsers.AugustinerParser import AugustinerParser
from backend.parsers.WeitblickParser import WeitblickParser
from backend.scripts.scraper_augustiner import download_augustiner_menu
from backend.scripts.scraper_weitblick import download_weitblick_menu
import subprocess

app = FastAPI(title="Speisekarten API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

def run_all_updates():
    try:

        download_augustiner_menu()
        download_weitblick_menu()
        
        AugustinerParser("backend/menus/TageskarteAugustiner.pdf").run()
        WeitblickParser("backend/menus/Wochenkarte.pdf").run()

    except Exception as e:
        print(f"[Update Error] {e}")


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
    restaurant_str: str = Query(None, description="Restaurant name"),
    db: Session = Depends(get_db)
):
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")
    else:
        target_date = date.today()

    if restaurant_str:
        restaurant = db.query(Restaurant).filter(Restaurant.Name == restaurant_str).first()
        if not restaurant:
            raise HTTPException(status_code=400, detail=f"Invalid restaurant name: {restaurant_str}")
    else:
        restaurant = db.query(Restaurant).filter(Restaurant.Name == "Augustiner").first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Default restaurant 'Augustiner' not found")

    dishes = (
        db.query(Speisen, Restaurant)
        .join(Restaurant, Speisen.r_ID == Restaurant.r_ID)
        .filter(Speisen.Datum == target_date)
        .filter(Restaurant.r_ID == restaurant.r_ID)
        .order_by(Restaurant.Name)
        .all()
    )

    if not dishes:
        raise HTTPException(status_code=404, detail=f"No dishes found for {restaurant.Name} on {target_date}")

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

@app.post("/update-menus")
def update_menus(background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    if x_api_key != "super-secret-key":
        raise HTTPException(status_code=403, detail="forbidden")

    run_all_updates()
    return {"status": "update started"}
