# 🌲 Camp Kit

Sistema completo para **gestão de acampamentos**, com funcionalidades de **Machine Learning** para **recomendar locais** e **prever o clima**. Ideal para quem quer planejar aventuras ao ar livre com segurança e praticidade.

---

## ✨ Funcionalidades

- ✅ Autenticação e gerenciamento de usuários  
- 🏟️ Cadastro e listagem de locais para acampamento  
- ⭐ Sistema de avaliações e comentários  
- 🤖 Recomendação inteligente de locais com base no histórico e preferências  
- 🌦️ Previsão climática para os próximos dias  
- 🔌 API RESTful completa  
- 💻 Interface de linha de comando (CLI)

---

## ⚙️ Requisitos

- Python 3.8 ou superior  
- Dependências listadas em `requirements.txt`

---

## 🚀 Instalação

Siga os passos abaixo para rodar o Camp Kit localmente:

```bash
# 1. Clone o repositório
git clone https://github.com/clerdomy/camp-kit.git
cd camp-kit

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env-example .env
# Depois edite o arquivo .env com suas informações
```

---

## 🧠 Treinamento dos Modelos de Machine Learning

Antes de rodar o sistema, é necessário treinar os modelos de ML:

```bash
python main.py train
```

---

## 🧪 Como Usar

### 🧱 Iniciar o servidor

```bash
python main.py
```

O servidor ficará disponível em `http://localhost:8000`.

### 💾 Interface de Linha de Comando (CLI)

```bash
# Criar um usuário
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario1", "email":"usuario1@exemplo.com", "password":"senha123"}'

# Login via CLI
python cli.py login usuario1 senha123

# Adicionar local
python cli.py add "Cachoeira do Sol" "Linda cachoeira com área para camping" -22.9068 -43.1729 850 --has-water --difficulty 3

# Listar locais
python cli.py list

# Recomendações
python cli.py recommend 1

# Previsão do tempo
python cli.py weather 1 --days 5
```

---

## 📁 Estrutura do Projeto

```
camp-kit/
├── main.py            # Servidor principal da API
├── database.py        # Configuração do banco de dados
├── models.py          # Modelos com SQLAlchemy
├── schemas.py         # Validação com Pydantic
├── ml_models.py       # Modelos de Machine Learning
├── auth.py            # Autenticação e segurança
└── cli.py             # Interface de linha de comando
```

---

## 🤖 Modelos de Machine Learning

### 🔍 Recomendacão de Locais

- Algoritmo: **K-Nearest Neighbors (KNN)**
- Critérios: histórico do usuário + avaliações

### 🌦️ Previsão do Clima

- Algoritmo: **Random Forest Regression**
- Prevê: temperatura, precipitação, umidade e vento

---

## 🌐 API Endpoints

### 🔐 Autenticação

- `POST /token` — Obter token de acesso

### 👤 Usuários

- `POST /users/` — Criar novo usuário  
- `GET /users/me` — Dados do usuário logado

### 🏟️ Locais de Acampamento

- `GET /campsites/` — Listar todos  
- `POST /campsites/` — Adicionar novo  
- `GET /campsites/{id}` — Ver detalhes

### 🧱 Recomendações

- `GET /recommendations/?user_id={id}` — Recomendação personalizada

### 🌦️ Previsão do Clima

- `GET /weather/{campsite_id}?days_ahead={dias}` — Previsão climática

---

## 🤝 Contribuindo

Contribuições são bem-vindas!  

1. Faça um fork  
2. Crie uma nova branch: `git checkout -b feature/sua-feature`  
3. Commit suas mudanças: `git commit -am 'Minha nova feature'`  
4. Envie para o GitHub: `git push origin feature/sua-feature`  
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

