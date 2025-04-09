import argparse
import requests
import json
import pandas as pd
from tabulate import tabulate
from datetime import datetime

API_URL = "http://localhost:8000"
TOKEN = None

def login(args):
    """Autenticar usuário e obter token"""
    global TOKEN
    response = requests.post(
        f"{API_URL}/token",
        data={"username": args.username, "password": args.password}
    )
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data["access_token"]
        print("Login realizado com sucesso!")
        return True
    else:
        print(f"Erro ao fazer login: {response.status_code}")
        print(response.text)
        return False

def list_campsites(args):
    """Listar locais de acampamento"""
    response = requests.get(f"{API_URL}/campsites/")
    
    if response.status_code == 200:
        campsites = response.json()
        if not campsites:
            print("Nenhum local de acampamento encontrado.")
            return
        
        # Criar DataFrame para exibição formatada
        df = pd.DataFrame(campsites)
        print("\n=== LOCAIS DE ACAMPAMENTO ===")
        print(tabulate(
            df[['id', 'name', 'difficulty', 'has_water', 'has_electricity']], 
            headers=['ID', 'Nome', 'Dificuldade', 'Água', 'Eletricidade'],
            tablefmt='pretty'
        ))
    else:
        print(f"Erro ao listar locais: {response.status_code}")
        print(response.text)

def get_recommendations(args):
    """Obter recomendações de locais"""
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(
        f"{API_URL}/recommendations/?user_id={args.user_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        recommendations = response.json()
        if not recommendations:
            print("Nenhuma recomendação encontrada.")
            return
        
        # Criar DataFrame para exibição formatada
        df = pd.DataFrame(recommendations)
        print("\n=== RECOMENDAÇÕES DE LOCAIS ===")
        print(tabulate(
            df[['id', 'name', 'difficulty', 'has_water', 'has_electricity']], 
            headers=['ID', 'Nome', 'Dificuldade', 'Água', 'Eletricidade'],
            tablefmt='pretty'
        ))
    else:
        print(f"Erro ao obter recomendações: {response.status_code}")
        print(response.text)

def get_weather(args):
    """Obter previsão de clima para um local"""
    response = requests.get(
        f"{API_URL}/weather/{args.campsite_id}?days_ahead={args.days}"
    )
    
    if response.status_code == 200:
        weather_data = response.json()
        predictions = weather_data["predictions"]
        
        print(f"\n=== PREVISÃO DE CLIMA PARA LOCAL ID {args.campsite_id} ===")
        for pred in predictions:
            print(f"Data: {pred['date']}")
            print(f"Temperatura: {pred['temperature']:.1f}°C")
            print(f"Precipitação: {pred['precipitation']:.1f}mm")
            print(f"Umidade: {pred['humidity']:.1f}%")
            print(f"Vento: {pred['wind_speed']:.1f}km/h")
            print(f"Previsão: {pred['forecast']}")
            print("-" * 40)
    else:
        print(f"Erro ao obter previsão de clima: {response.status_code}")
        print(response.text)

def add_campsite(args):
    """Adicionar novo local de acampamento"""
    if not TOKEN:
        print("Você precisa fazer login primeiro!")
        return
    
    data = {
        "name": args.name,
        "description": args.description,
        "latitude": args.latitude,
        "longitude": args.longitude,
        "elevation": args.elevation,
        "has_water": args.has_water,
        "has_electricity": args.has_electricity,
        "difficulty": args.difficulty
    }
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(
        f"{API_URL}/campsites/",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        campsite = response.json()
        print(f"Local de acampamento '{campsite['name']}' adicionado com sucesso! ID: {campsite['id']}")
    else:
        print(f"Erro ao adicionar local: {response.status_code}")
        print(response.text)

def main():
    parser = argparse.ArgumentParser(description="Camp Kit - Sistema de Gestão de Acampamentos")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando de login
    login_parser = subparsers.add_parser("login", help="Fazer login no sistema")
    login_parser.add_argument("username", help="Nome de usuário")
    login_parser.add_argument("password", help="Senha")
    login_parser.set_defaults(func=login)
    
    # Comando para listar locais
    list_parser = subparsers.add_parser("list", help="Listar locais de acampamento")
    list_parser.set_defaults(func=list_campsites)
    
    # Comando para obter recomendações
    rec_parser = subparsers.add_parser("recommend", help="Obter recomendações de locais")
    rec_parser.add_argument("user_id", type=int, help="ID do usuário")
    rec_parser.set_defaults(func=get_recommendations)
    
    # Comando para obter previsão de clima
    weather_parser = subparsers.add_parser("weather", help="Obter previsão de clima")
    weather_parser.add_argument("campsite_id", type=int, help="ID do local")
    weather_parser.add_argument("--days", type=int, default=7, help="Número de dias para previsão")
    weather_parser.set_defaults(func=get_weather)
    
    # Comando para adicionar local
    add_parser = subparsers.add_parser("add", help="Adicionar novo local de acampamento")
    add_parser.add_argument("name", help="Nome do local")
    add_parser.add_argument("description", help="Descrição do local")
    add_parser.add_argument("latitude", type=float, help="Latitude")
    add_parser.add_argument("longitude", type=float, help="Longitude")
    add_parser.add_argument("elevation", type=float, help="Elevação (metros)")
    add_parser.add_argument("--has-water", action="store_true", help="Local possui água")
    add_parser.add_argument("--has-electricity", action="store_true", help="Local possui eletricidade")
    add_parser.add_argument("--difficulty", type=int, default=3, choices=range(1, 6), help="Dificuldade (1-5)")
    add_parser.set_defaults(func=add_campsite)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()