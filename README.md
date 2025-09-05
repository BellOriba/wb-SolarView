# SolarView API

Esta é uma API de backend desenvolvida em Python com o framework FastAPI. Ela serve como um proxy para a API [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) da Comissão Europeia, permitindo que um aplicativo móvel estime a produção de energia de painéis solares com base em dados fornecidos pelo usuário.

A API inclui um endpoint de cálculo protegido por autenticação e um endpoint de verificação de saúde (`/health`).

## Arquitetura do Projeto

O projeto utiliza a **Arquitetura Hexagonal (ou Arquitetura de Portas e Adaptadores)** para separar a lógica de negócio principal das dependências externas, como o framework web e as APIs de terceiros. Isso torna o código mais limpo, testável e fácil de manter.

Abaixo está a hierarquia de diretórios e a responsabilidade de cada componente:

```
.
├── .venv/                  # Ambiente virtual do Python
├── src/
│   └── solar_api/
│       ├── __init__.py
│       ├── main.py             # Ponto de entrada da aplicação FastAPI
│       ├── config.py           # Carrega configurações do ambiente (.env)
│       │
│       ├── application/        # CORE DA APLICAÇÃO (O HEXÁGONO)
│       │   ├── __init__.py
│       │   ├── ports/          # Define as interfaces (contratos) que o core usa
│       │   │   └── pvgis_service.py
│       │   └── services/       # Contém a lógica de negócio principal
│       │       └── solar_service.py
│       │
│       ├── adapters/           # IMPLEMENTAÇÕES EXTERNAS
│       │   ├── __init__.py
│       │   ├── api/            # Adaptador para a API web (FastAPI)
│       │   │   ├── __init__.py
│       │   │   ├── dependencies.py # Lógica de autenticação
│       │   │   └── routes.py       # Endpoints da API (/calculate, /health)
│       │   └── pvgis/          # Adaptador para a API externa do PVGIS
│       │       ├── __init__.py
│       │       └── pvgis_adapter.py
│       │
│       └── domain/             # Modelos de dados e objetos de negócio
│           ├── __init__.py
│           └── models.py
│
├── .env                    # Arquivo de configuração de ambiente (NÃO VERSIONADO)
├── pyproject.toml          # Definições do projeto e dependências
├── README.md               # Este arquivo
└── uv.lock                 # Arquivo de lock do gerenciador de pacotes uv
```

- **`domain`**: Contém os modelos de dados puros da aplicação (ex: `PVGISRequest`). Não depende de nenhuma outra camada.
- **`application/ports`**: Define as "portas" (interfaces) que a lógica de negócio precisa para se comunicar com o mundo exterior. Por exemplo, `PVGISServicePort` define *o que* é necessário para obter dados solares, mas não *como*.
- **`application/services`**: Contém a lógica de negócio central. Utiliza as portas para realizar seu trabalho, sem conhecer os detalhes da implementação externa.
- **`adapters`**: Contém as implementações concretas das portas.
  - **`adapters/api`**: É um "Driving Adapter". Ele recebe comandos do usuário (via HTTP) e os envia para a camada de aplicação. Aqui ficam os endpoints, a validação de entrada e a autenticação.
  - **`adapters/pvgis`**: É um "Driven Adapter". Ele implementa uma porta da aplicação (`PVGISServicePort`) para se comunicar com um serviço externo (a API do PVGIS).

## Guia de Instalação e Execução

### Pré-requisitos
- Python 3.10+
- `uv` (ou `pip`) para gerenciamento de pacotes

### 1. Clone o Repositório (Opcional)
```bash
git clone <url-do-repositorio>
cd wb-solarView
```

### 2. Crie e Ative o Ambiente Virtual
```bash
# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente (Windows)
.\.venv\Scripts\activate
```

### 3. Instale as Dependências
Use o `uv` para instalar as bibliotecas listadas no `pyproject.toml`.
```bash
uv pip install -r requirements.txt 
# Ou se não tiver um requirements.txt, instale diretamente:
uv pip install fastapi uvicorn httpx python-dotenv
```

### 4. Configure o Ambiente
Crie um arquivo chamado `.env` na raiz do projeto e adicione as credenciais para a API. Você pode copiar o exemplo abaixo:
```ini
# .env
API_USERNAME=user
API_PASSWORD=password
```

### 5. Execute a Aplicação
Use o `uvicorn` para iniciar o servidor. A flag `--reload` reinicia o servidor automaticamente após qualquer alteração no código.
```bash
python -m uvicorn src.solar_api.main:app --reload
```
O servidor estará disponível em `http://127.0.0.1:8000`.

## Endpoints da API

Você pode acessar a documentação interativa gerada pelo Swagger UI em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Health Check
- **GET** `/health`
  - Retorna o status da API. Não requer autenticação.

### Cálculo de Produção Solar
- **POST** `/calculate`
  - Recebe os dados para o cálculo, faz a requisição à API do PVGIS e retorna o resultado.
  - **Autenticação**: Basic Auth. Use as credenciais definidas no arquivo `.env`.

  **Exemplo de corpo da requisição (JSON):**
  ```json
  {
    "lat": -23.531138,
    "lon": -46.762038,
    "peakpower": 5,
    "loss": 14
  }
  ```

  **Exemplo de chamada com `curl`:**
  ```bash
  curl -X POST "http://127.0.0.1:8000/calculate" \
  -u "user:password" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": -23.531138,
    "lon": -46.762038,
    "peakpower": 5,
    "loss": 14
  }'
  ```
