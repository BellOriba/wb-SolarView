# SolarView API

A SolarView API é uma solução completa para gerenciamento e análise de painéis solares, desenvolvida em Python com o framework FastAPI. A aplicação oferece duas funcionalidades principais:

1. **Cálculo de Produção Solar**: Integração com a API [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) da Comissão Europeia para estimar a produção de energia de painéis solares com base em localização e características técnicas.

2. **Gerenciamento de Modelos de Painéis**: Sistema completo para cadastro, consulta, atualização e remoção de modelos de painéis solares, permitindo um catálogo personalizável de equipamentos.

## Arquitetura do Projeto

O projeto utiliza a **Arquitetura Hexagonal (ou Arquitetura de Portas e Adaptadores)** para separar a lógica de negócio principal das dependências externas, como o framework web e as APIs de terceiros.

Abaixo está a hierarquia de diretórios e a responsabilidade de cada componente:

```
.
├── src/
│   └── solar_api/
│       ├── __init__.py
│       ├── main.py             # Ponto de entrada da aplicação FastAPI
│       ├── config.py           # Carrega configurações do ambiente (.env)
│       │
│       ├── application/        # CORE DA APLICAÇÃO
│       │   ├── __init__.py
│       │   ├── ports/          # Define as interfaces (contratos) que o core usa
│       │   │   ├── pvgis_service.py
│       │   │   └── panel_repository.py
│       │   └── services/       # Contém a lógica de negócio principal
│       │       ├── solar_service.py
│       │       └── panel_service.py
│       │
│       ├── adapters/           # IMPLEMENTAÇÕES EXTERNAS
│       │   ├── __init__.py
│       │   ├── api/            # Adaptador para a API web (FastAPI)
│       │   │   ├── __init__.py
│       │   │   ├── dependencies.py  # Lógica de autenticação
│       │   │   ├── routes.py        # Endpoints da API (/calculate, /health)
│       │   │   └── panel_routes.py  # Endpoints para gerenciamento de painéis
│       │   ├── pvgis/          # Adaptador para a API externa do PVGIS
│       │   │   ├── __init__.py
│       │   │   └── pvgis_adapter.py
│       │   └── repositories/    # Implementações de repositórios de persistência
│       │       ├── __init__.py
│       │       └── json_panel_repository.py
│       │
│       └── domain/             # Modelos de dados e objetos de negócio
│           ├── __init__.py
│           ├── models.py       # Modelos da aplicação
│           └── panel_model.py  # Modelos específicos de painéis
│
├── storage/                # Armazenamento de dados da aplicação
│   ├── models.json         # Dados dos modelos de painéis (formato JSON)
│   └── docs.md             # Documentação adicional
│
├── .env.example           # Exemplo de configuração de ambiente
├── pyproject.toml         # Definições do projeto e dependências
├── README.md              # Este arquivo
└── uv.lock                # Arquivo de lock do uv
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

### 2. Instale as Dependências
Use o `uv` para instalar as bibliotecas listadas no `pyproject.toml`.
```bash
uv add -r requirements.txt 
# Ou se não tiver um requirements.txt, instale diretamente:
uv add fastapi uvicorn httpx python-dotenv
```
Ou use o `pip`:
```bash
# Crie o ambiente virtual
python -m venv .venv
# Ative o ambiente virtual
.\.venv\Scripts\activate
# Instale as dependências
pip install -r requirements.txt
```

### 3. Ative o Ambiente Virtual
```bash
.\.venv\Scripts\activate
```

### 4. Configure o Ambiente
Crie um arquivo chamado `.env` na raiz do projeto e atualize as credenciais para a API. Você pode copiar o exemplo abaixo:
```bash
cp .env.example .env
```

### 5. Execute a Aplicação
Você pode executar a aplicação de duas formas:

1. **Usando o módulo Python diretamente** (recomendado para desenvolvimento):
   ```bash
   python -m src.solar_api.main
   ```
   Este comando inicia o servidor com recarregamento automático quando arquivos são alterados.

2. **Usando o Uvicorn diretamente**:
   ```bash
   python -m uvicorn src.solar_api.main:app --reload
   ```

O servidor estará disponível em `http://127.0.0.1:8000`.

### 6. Acessando a Documentação da API
A aplicação inclui documentação interativa gerada automaticamente:
- **Swagger UI**: Acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: Acesse [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Endpoints da API

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

### Gerenciamento de Modelos de Painéis

#### Listar Modelos
- **GET** `/models`
  - Retorna a lista de todos os modelos de painéis cadastrados.
  - **Autenticação**: Basic Auth.

  **Exemplo de resposta (JSON):**
  ```json
  [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Painel Solar 400W",
      "capacity": 0.4,
      "efficiency": 20.5,
      "manufacturer": "SolarTech",
      "type": "Monocristalino"
    }
  ]
  ```

#### Obter um Modelo Específico
- **GET** `/models/{model_id}`
  - Retorna os detalhes de um modelo de painel específico.
  - **Parâmetros de URL**:
    - `model_id`: UUID do modelo
  - **Autenticação**: Basic Auth.

#### Criar um Novo Modelo
- **POST** `/models`
  - Cria um novo modelo de painel solar.
  - **Autenticação**: Basic Auth.
  - **Corpo da Requisição (JSON):**
    - `name`: Nome do modelo (obrigatório)
    - `capacity`: Capacidade em kWp (obrigatório, > 0)
    - `efficiency`: Eficiência em % (obrigatório, 0-100)
    - `manufacturer`: Fabricante (obrigatório)
    - `type`: Tipo do painel (ex: Monocristalino) (obrigatório)

#### Atualizar um Modelo
- **PUT** `/models/{model_id}`
  - Atualiza um modelo de painel existente. Aceita atualizações parciais.
  - **Autenticação**: Basic Auth.
  - **Parâmetros de URL**:
    - `model_id`: UUID do modelo a ser atualizado
  - **Corpo da Requisição (JSON)**: Pelo menos um dos campos abaixo:
    - `name`: Nome do modelo
    - `capacity`: Capacidade em kWp (> 0)
    - `efficiency`: Eficiência em % (0-100)
    - `manufacturer`: Fabricante
    - `type`: Tipo do painel

#### Excluir um Modelo
- **DELETE** `/models/{model_id}`
  - Remove um modelo de painel.
  - **Autenticação**: Basic Auth.
  - **Parâmetros de URL**:
    - `model_id`: UUID do modelo a ser removido
