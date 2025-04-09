import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
import requests

# Importações locais
from database import SessionLocal, engine
import models, schemas
from ml_models import train_recommendation_model, train_weather_model, recommend_locations, predict_weather

# Criar tabelas no banco de dados
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Camp Kit API", description="API para gestão de acampamentos")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Autenticação
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rotas para usuários
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Rotas para locais de acampamento
@app.post("/campsites/", response_model=schemas.Campsite)
def create_campsite(campsite: schemas.CampsiteCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_campsite = models.Campsite(**campsite.dict())
    db.add(db_campsite)
    db.commit()
    db.refresh(db_campsite)
    return db_campsite

@app.get("/campsites/", response_model=List[schemas.Campsite])
def read_campsites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    campsites = db.query(models.Campsite).offset(skip).limit(limit).all()
    return campsites

@app.get("/campsites/{campsite_id}", response_model=schemas.Campsite)
def read_campsite(campsite_id: int, db: Session = Depends(get_db)):
    campsite = db.query(models.Campsite).filter(models.Campsite.id == campsite_id).first()
    if campsite is None:
        raise HTTPException(status_code=404, detail="Local de acampamento não encontrado")
    return campsite

# Rotas para recomendações de locais
@app.get("/recommendations/", response_model=List[schemas.Campsite])
def get_recommendations(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    # Obter preferências do usuário
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Obter todos os locais de acampamento
    campsites = db.query(models.Campsite).all()
    
    # Converter para DataFrame para processamento ML
    campsites_df = pd.DataFrame([{
        'id': c.id,
        'latitude': c.latitude,
        'longitude': c.longitude,
        'elevation': c.elevation,
        'has_water': c.has_water,
        'has_electricity': c.has_electricity,
        'difficulty': c.difficulty
    } for c in campsites])
    
    # Obter avaliações do usuário
    ratings = db.query(models.Rating).filter(models.Rating.user_id == user_id).all()
    ratings_df = pd.DataFrame([{
        'campsite_id': r.campsite_id,
        'rating': r.rating
    } for r in ratings])
    
    # Obter recomendações
    recommended_ids = recommend_locations(user_id, campsites_df, ratings_df)
    
    # Retornar locais recomendados
    recommended_campsites = db.query(models.Campsite).filter(models.Campsite.id.in_(recommended_ids)).all()
    return recommended_campsites

# Rotas para previsão de clima
@app.get("/weather/{campsite_id}", response_model=schemas.WeatherPrediction)
def get_weather_prediction(campsite_id: int, days_ahead: int = 7, db: Session = Depends(get_db)):
    campsite = db.query(models.Campsite).filter(models.Campsite.id == campsite_id).first()
    if campsite is None:
        raise HTTPException(status_code=404, detail="Local de acampamento não encontrado")
    
    # Obter dados históricos de clima
    weather_data = db.query(models.WeatherData).filter(
        models.WeatherData.campsite_id == campsite_id
    ).order_by(models.WeatherData.date.desc()).limit(30).all()
    
    if len(weather_data) < 7:
        # Se não houver dados suficientes, buscar de API externa
        weather_data = fetch_weather_data(campsite.latitude, campsite.longitude)
    
    # Converter para DataFrame
    weather_df = pd.DataFrame([{
        'date': w.date,
        'temperature': w.temperature,
        'precipitation': w.precipitation,
        'humidity': w.humidity,
        'wind_speed': w.wind_speed
    } for w in weather_data])
    
    # Fazer previsão
    predictions = predict_weather(weather_df, days_ahead)
    
    # Formatar resposta
    result = []
    for i, pred in enumerate(predictions):
        date = datetime.now() + timedelta(days=i+1)
        result.append({
            'date': date.strftime('%Y-%m-%d'),
            'temperature': pred['temperature'],
            'precipitation': pred['precipitation'],
            'humidity': pred['humidity'],
            'wind_speed': pred['wind_speed'],
            'forecast': get_forecast_description(pred)
        })
    
    return {'campsite_id': campsite_id, 'predictions': result}

# Função auxiliar para descrição do clima
def get_forecast_description(prediction):
    temp = prediction['temperature']
    precip = prediction['precipitation']
    
    if precip > 5:
        if temp < 15:
            return "Frio e chuvoso"
        else:
            return "Chuva"
    elif precip > 0.5:
        return "Possibilidade de chuva"
    else:
        if temp > 25:
            return "Ensolarado e quente"
        elif temp > 15:
            return "Ensolarado e agradável"
        else:
            return "Frio e seco"

# Função para buscar dados de clima de API externa
def fetch_weather_data(lat, lon):
    # Simulação de API de clima
    # Em um sistema real, usaríamos uma API como OpenWeatherMap
    base_temp = 20 + np.random.normal(0, 5)
    data = []
    
    for i in range(30):
        date = datetime.now() - timedelta(days=30-i)
        temp = base_temp + np.random.normal(0, 3)
        precip = max(0, np.random.exponential(1))
        humidity = min(100, max(30, 60 + np.random.normal(0, 10)))
        wind = max(0, np.random.normal(10, 5))
        
        data.append({
            'date': date,
            'temperature': temp,
            'precipitation': precip,
            'humidity': humidity,
            'wind_speed': wind
        })
    
    return data

# Iniciar servidor se executado diretamente
if __name__ == "__main__":
    if "train" in sys.argv:
        print("Treinando modelos de ML...")
        train_recommendation_model()
        train_weather_model()
        print("Modelos treinados com sucesso!")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)