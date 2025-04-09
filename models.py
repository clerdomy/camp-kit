from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, Text
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relacionamentos
    ratings = relationship("Rating", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")
    trips = relationship("Trip", back_populates="user")

class Campsite(Base):
    __tablename__ = "campsites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
    has_water = Column(Boolean, default=False)
    has_electricity = Column(Boolean, default=False)
    difficulty = Column(Integer)  # 1-5 escala
    
    # Relacionamentos
    ratings = relationship("Rating", back_populates="campsite")
    weather_data = relationship("WeatherData", back_populates="campsite")
    trips = relationship("Trip", back_populates="campsite")

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    campsite_id = Column(Integer, ForeignKey("campsites.id"))
    rating = Column(Integer)  # 1-5 escala
    comment = Column(Text, nullable=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="ratings")
    campsite = relationship("Campsite", back_populates="ratings")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prefer_water = Column(Boolean, default=False)
    prefer_electricity = Column(Boolean, default=False)
    max_difficulty = Column(Integer, default=5)
    min_elevation = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="preferences")

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    campsite_id = Column(Integer, ForeignKey("campsites.id"))
    date = Column(Date)
    temperature = Column(Float)
    precipitation = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    
    # Relacionamentos
    campsite = relationship("Campsite", back_populates="weather_data")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    campsite_id = Column(Integer, ForeignKey("campsites.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    notes = Column(Text, nullable=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="trips")
    campsite = relationship("Campsite", back_populates="trips")