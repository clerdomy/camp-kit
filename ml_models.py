import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

# Modelo de recomendação de locais
def train_recommendation_model():
    """
    Treina o modelo de recomendação de locais baseado em preferências do usuário
    e avaliações anteriores.
    """
    try:
        # Em um sistema real, carregaríamos dados do banco
        # Aqui vamos simular alguns dados
        
        # Características dos locais
        campsites_data = {
            'id': list(range(1, 21)),
            'latitude': np.random.uniform(20, 50, 20),
            'longitude': np.random.uniform(-100, -70, 20),
            'elevation': np.random.uniform(0, 3000, 20),
            'has_water': np.random.choice([0, 1], 20),
            'has_electricity': np.random.choice([0, 1], 20),
            'difficulty': np.random.randint(1, 6, 20)
        }
        
        campsites_df = pd.DataFrame(campsites_data)
        
        # Preparar dados para o modelo
        features = ['latitude', 'longitude', 'elevation', 'has_water', 'has_electricity', 'difficulty']
        X = campsites_df[features].values
        
        # Normalizar dados
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Treinar modelo KNN para recomendações baseadas em conteúdo
        model = NearestNeighbors(n_neighbors=5, algorithm='auto')
        model.fit(X_scaled)
        
        # Salvar modelo e scaler
        joblib.dump(model, 'recommendation_model.pkl')
        joblib.dump(scaler, 'recommendation_scaler.pkl')
        
        print("Modelo de recomendação treinado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao treinar modelo de recomendação: {e}")
        return False

def recommend_locations(user_id, campsites_df, ratings_df=None, n_recommendations=5):
    """
    Recomenda locais de acampamento para um usuário específico.
    
    Args:
        user_id: ID do usuário
        campsites_df: DataFrame com dados dos locais
        ratings_df: DataFrame com avaliações do usuário (opcional)
        n_recommendations: Número de recomendações a retornar
        
    Returns:
        Lista de IDs dos locais recomendados
    """
    try:
        # Carregar modelo e scaler
        model = joblib.load('recommendation_model.pkl')
        scaler = joblib.load('recommendation_scaler.pkl')
        
        # Se temos avaliações do usuário, usamos para personalizar
        if ratings_df is not None and not ratings_df.empty:
            # Encontrar o local mais bem avaliado pelo usuário
            best_rated = ratings_df.sort_values('rating', ascending=False).iloc[0]
            best_campsite_id = best_rated['campsite_id']
            
            # Obter características desse local
            best_campsite = campsites_df[campsites_df['id'] == best_campsite_id]
            
            if not best_campsite.empty:
                features = ['latitude', 'longitude', 'elevation', 'has_water', 'has_electricity', 'difficulty']
                query_point = best_campsite[features].values
                
                # Normalizar
                query_point_scaled = scaler.transform(query_point)
                
                # Encontrar vizinhos mais próximos
                distances, indices = model.kneighbors(query_point_scaled, n_neighbors=n_recommendations+1)
                
                # Pular o primeiro resultado (é o próprio local)
                recommended_indices = indices[0][1:]
                
                # Obter IDs dos locais recomendados
                recommended_ids = campsites_df.iloc[recommended_indices]['id'].tolist()
                return recommended_ids
        
        # Se não temos avaliações ou o local não foi encontrado, recomendamos os mais populares
        # Em um sistema real, teríamos dados de popularidade
        # Aqui vamos simplesmente retornar alguns IDs aleatórios
        return np.random.choice(campsites_df['id'].values, 
                               size=min(n_recommendations, len(campsites_df)), 
                               replace=False).tolist()
    
    except (FileNotFoundError, Exception) as e:
        print(f"Erro ao gerar recomendações: {e}")
        # Se o modelo não existir, treinar e tentar novamente
        if isinstance(e, FileNotFoundError):
            if train_recommendation_model():
                return recommend_locations(user_id, campsites_df, ratings_df, n_recommendations)
        
        # Em caso de erro, retornar alguns locais aleatórios
        return np.random.choice(campsites_df['id'].values, 
                               size=min(n_recommendations, len(campsites_df)), 
                               replace=False).tolist()

# Modelo de previsão de clima
def train_weather_model():
    """
    Treina o modelo de previsão de clima baseado em dados históricos.
    """
    try:
        # Em um sistema real, carregaríamos dados históricos do banco
        # Aqui vamos simular alguns dados
        
        # Criar datas para os últimos 365 dias
        dates = [datetime.now() - timedelta(days=i) for i in range(365, 0, -1)]
        
        # Simular temperatura com sazonalidade
        base_temp = 20
        annual_cycle = 10 * np.sin([2 * np.pi * i / 365 for i in range(365)])
        noise = np.random.normal(0, 3, 365)
        temperatures = base_temp + annual_cycle + noise
        
        # Simular precipitação
        precip_prob = 0.3 + 0.2 * np.sin([2 * np.pi * i / 365 for i in range(365)])
        precipitation = np.zeros(365)
        for i in range(365):
            if np.random.random() < precip_prob[i]:
                precipitation[i] = np.random.exponential(5)
        
        # Simular umidade
        humidity = 60 + 20 * np.sin([2 * np.pi * i / 365 for i in range(365)]) + np.random.normal(0, 10, 365)
        humidity = np.clip(humidity, 30, 100)
        
        # Simular velocidade do vento
        wind_speed = 10 + 5 * np.sin([2 * np.pi * i / 365 for i in range(365)]) + np.random.normal(0, 3, 365)
        wind_speed = np.clip(wind_speed, 0, 30)
        
        # Criar DataFrame
        weather_data = pd.DataFrame({
            'date': dates,
            'temperature': temperatures,
            'precipitation': precipitation,
            'humidity': humidity,
            'wind_speed': wind_speed
        })
        
        # Adicionar features temporais
        weather_data['day_of_year'] = weather_data['date'].dt.dayofyear
        weather_data['month'] = weather_data['date'].dt.month
        
        # Preparar dados para o modelo
        X = weather_data[['day_of_year', 'month']].values
        y_temp = weather_data['temperature'].values
        y_precip = weather_data['precipitation'].values
        y_humidity = weather_data['humidity'].values
        y_wind = weather_data['wind_speed'].values
        
        # Treinar modelos
        model_temp = RandomForestRegressor(n_estimators=100)
        model_temp.fit(X, y_temp)
        
        model_precip = RandomForestRegressor(n_estimators=100)
        model_precip.fit(X, y_precip)
        
        model_humidity = RandomForestRegressor(n_estimators=100)
        model_humidity.fit(X, y_humidity)
        
        model_wind = RandomForestRegressor(n_estimators=100)
        model_wind.fit(X, y_wind)
        
        # Salvar modelos
        joblib.dump(model_temp, 'weather_model_temp.pkl')
        joblib.dump(model_precip, 'weather_model_precip.pkl')
        joblib.dump(model_humidity, 'weather_model_humidity.pkl')
        joblib.dump(model_wind, 'weather_model_wind.pkl')
        
        print("Modelo de previsão de clima treinado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao treinar modelo de previsão de clima: {e}")
        return False

def predict_weather(weather_df, days_ahead=7):
    """
    Faz previsão de clima para os próximos dias.
    
    Args:
        weather_df: DataFrame com dados históricos de clima
        days_ahead: Número de dias para prever
        
    Returns:
        Lista de dicionários com previsões
    """
    try:
        # Carregar modelos
        model_temp = joblib.load('weather_model_temp.pkl')
        model_precip = joblib.load('weather_model_precip.pkl')
        model_humidity = joblib.load('weather_model_humidity.pkl')
        model_wind = joblib.load('weather_model_wind.pkl')
        
        # Preparar datas para previsão
        future_dates = [datetime.now() + timedelta(days=i+1) for i in range(days_ahead)]
        future_X = pd.DataFrame({
            'day_of_year': [d.timetuple().tm_yday for d in future_dates],
            'month': [d.month for d in future_dates]
        }).values
        
        # Fazer previsões
        pred_temp = model_temp.predict(future_X)
        pred_precip = model_precip.predict(future_X)
        pred_humidity = model_humidity.predict(future_X)
        pred_wind = model_wind.predict(future_X)
        
        # Formatar resultados
        predictions = []
        for i in range(days_ahead):
            predictions.append({
                'temperature': float(pred_temp[i]),
                'precipitation': max(0, float(pred_precip[i])),
                'humidity': min(100, max(0, float(pred_humidity[i]))),
                'wind_speed': max(0, float(pred_wind[i]))
            })
        
        return predictions
    
    except (FileNotFoundError, Exception) as e:
        print(f"Erro ao gerar previsão de clima: {e}")
        # Se o modelo não existir, treinar e tentar novamente
        if isinstance(e, FileNotFoundError):
            if train_weather_model():
                return predict_weather(weather_df, days_ahead)
        
        # Em caso de erro, retornar previsões simples
        predictions = []
        for i in range(days_ahead):
            predictions.append({
                'temperature': 20 + np.random.normal(0, 5),
                'precipitation': max(0, np.random.exponential(1)),
                'humidity': min(100, max(30, 60 + np.random.normal(0, 10))),
                'wind_speed': max(0, np.random.normal(10, 5))
            })
        
        return predictions