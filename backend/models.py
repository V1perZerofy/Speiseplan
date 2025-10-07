from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Restaurant(Base):
    __tablename__ = "Restaurant"

    r_ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)

    # Relationship: one restaurant → many dishes
    speisen = relationship("Speisen", back_populates="restaurant", cascade="all, delete-orphan")


class Speisen(Base):
    __tablename__ = "Speisen"

    s_ID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Preis = Column(Float, nullable=False)
    Datum = Column(Date, nullable=False)
    r_ID = Column(Integer, ForeignKey("Restaurant.r_ID"), nullable=False)

    # Relationship: link back to the parent restaurant
    restaurant = relationship("Restaurant", back_populates="speisen")

