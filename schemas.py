from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# Esquemas para Usuário
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# Esquemas para Local de Acampamento
class CampsiteBase(BaseModel):
    name: str
    description: str
    latitude: float
    longitude: float
    elevation: float
    has_water: bool
    has_electricity: bool
    difficulty: int

class CampsiteCreate(CampsiteBase):
    pass

class Campsite(CampsiteBase):
    id: int

    class Config:
        orm_mode = True

# Esquemas para Avaliação
class RatingBase(BaseModel):
    rating: int
    comment: Optional[str] = None

class RatingCreate(RatingBase):
    campsite_id: int

class Rating(RatingBase):
    id: int
    user_id: int
    campsite_id: int

    class Config:
        orm_mode = True

# Esquemas para Preferências do Usuário
class UserPreferenceBase(BaseModel):
    prefer_water: bool = False
    prefer_electricity: bool = False
    max_difficulty: int = 5
    min_elevation: Optional[float] = None
    max_elevation: Optional[float] = None

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreference(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Esquemas para Dados de Clima
class WeatherDataBase(BaseModel):
    date: date
    temperature: float
    precipitation: float
    humidity: float
    wind_speed: float

class WeatherDataCreate(WeatherDataBase):
    campsite_id: int

class WeatherData(WeatherDataBase):
    id: int
    campsite_id: int

    class Config:
        orm_mode = True

# Esquemas para Viagem
class TripBase(BaseModel):
    start_date: date
    end_date: date
    notes: Optional[str] = None

class TripCreate(TripBase):
    campsite_id: int

class Trip(TripBase):
    id: int
    user_id: int
    campsite_id: int

    class Config:
        orm_mode = True

# Esquema para previsão de clima
class WeatherPredictionItem(BaseModel):
    date: str
    temperature: float
    precipitation: float
    humidity: float
    wind_speed: float
    forecast: str

class WeatherPrediction(BaseModel):
    campsite_id: int
    predictions: List[WeatherPredictionItem]

# Esquemas para autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None