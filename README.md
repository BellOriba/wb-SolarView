# SolarView API

1. **Cálculo de Produção Solar**: Integração com a API [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) da Comissão Europeia para estimar a produção de energia de painéis solares com base em localização e características técnicas.

2. **Gerenciamento de Modelos de Painéis**: Sistema completo para cadastro, consulta, atualização e remoção de modelos de painéis solares.

3. **Autenticação e Autorização**: Sistema de usuários com diferentes níveis de permissão (usuários comuns e administradores).

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
│       ├── adapters/           # Adaptadores que conectam a aplicação ao mundo externo
│       │   ├── __init__.py
│       │   │
│       │   ├── api/            # Adaptadores de API (HTTP)
│       │   │   ├── auth_routes.py     # Rotas de autenticação
│       │   │   ├── panel_routes.py    # Rotas de painéis solares
│       │   │   ├── user_routes.py     # Rotas de usuários
│       │   │   ├── routes.py          # Rotas principais
│       │   │   └── dependencies.py    # Dependências e injeção de dependências
│       │   │
│       │   ├── pvgis/          # Adaptador para a API PVGIS
│       │   │   └── pvgis_adapter.py
│       │   │
│       │   └── repositories/    # Implementações concretas dos repositórios
│       │       ├── postgres_panel_repository.py  # Repositório de painéis
│       │       └── postgres_user_repository.py   # Repositório de usuários
│       │
│       └── application/        # CORE DA APLICAÇÃO (regras de negócio)
│           ├── __init__.py
│           │
│           ├── ports/          # Portas (interfaces) que definem os contratos
│           │   ├── pvgis_service.py      # Contrato para serviços PVGIS
│           │   ├── panel_repository.py   # Contrato para repositório de painéis
│           │   └── user_repository.py    # Contrato para repositório de usuários
│           │
│           └── services/       # Serviços de aplicação (lógica de negócio)
│               ├── solar_service.py     # Serviço para cálculos solares
│               ├── panel_service.py     # Serviço para gerenciamento de painéis
│               └── user_service.py      # Serviço para gerenciamento de usuários
│
├── storage/                # Armazenamento de dados da aplicação
│   └── data/               # Dados da aplicação (se aplicável)
│
├── tests/                  # Testes automatizados
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   └── test_services/
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

## Autenticação e Gerenciamento de Usuários

A SolarView API inclui um sistema completo de gerenciamento de usuários com autenticação baseada em chave de API (API Key).

### Funcionalidades

- Gerenciamento de usuários (operações CRUD)
- Autenticação via chave de API (API Key)
- Controle de acesso baseado em funções (usuários comuns e administradores)
- Hash de senhas com bcrypt
- Rotas protegidas com verificação de permissões

### Fluxo de Autenticação

1. **Login para obter a chave de API**
   ```
   POST /auth/login
   Content-Type: application/x-www-form-urlencoded
   
   email=usuario@exemplo.com&password=senhasegura123
   ```
   
   Resposta:
   ```json
   {
     "id": 1,
     "email": "usuario@exemplo.com",
     "is_active": true,
     "is_admin": false,
     "api_key": "sua-chave-de-api-aqui"
   }
   ```

2. **Usar a chave de API** em requisições subsequentes
   ```
   X-API-Key: sua-chave-de-api-aqui
   ```

### Endpoints Protegidos

- `GET /auth/me` - Retorna informações do usuário autenticado
- `POST /auth/rotate-key` - Gera uma nova chave de API
- `POST /auth/admin/rotate-key/{user_id}` - Gera nova chave para um usuário (apenas admin)
- `GET /users/` - Lista usuários (apenas admin)
- `GET /users/{user_id}` - Busca usuário por ID
- `PUT /users/{user_id}` - Atualiza usuário
- `DELETE /users/{user_id}` - Remove usuário (apenas admin)

## Guia de Instalação e Execução

### Pré-requisitos
- Python 3.10+
- `uv` (ou `pip`) para gerenciamento de pacotes

### 1. Clone o Repositório
```bash
git clone https://github.com/BellOriba/wb-solarView.git
cd wb-solarView
```

### 2. Configure o Ambiente
1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   # No Windows
   copy .env.example .env
   
   # No Linux/Mac
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas configurações:
   ```env
   # Configuração do banco de dados
   DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost:5432/solarview
   
   # Configurações de segurança
   SECRET_KEY=sua_chave_secreta_aqui
   
   # Credenciais do administrador inicial
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=senha_segura
   ```
   
   Substitua os valores conforme necessário para seu ambiente.

### 3. Instale as Dependências
Recomendamos o uso de um ambiente virtual para isolar as dependências do projeto.

#### Com pip (recomendado):
```bash
# Crie e ative o ambiente virtual
python -m venv .venv

# No Windows
.venv\Scripts\activate

# No Linux/Mac
# source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 4. Execute a Aplicação

#### Desenvolvimento
Para desenvolvimento, use o Uvicorn com recarregamento automático:

```bash
# Com recarregamento automático (desenvolvimento)
uvicorn src.solar_api.main:app --reload
```

#### Produção
Para ambiente de produção, use um servidor ASGI como o Uvicorn com múltiplos workers:

```bash
uvicorn src.solar_api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Variáveis de ambiente úteis
- `PORT`: Porta para executar o servidor (padrão: 8000)
- `HOST`: Endereço para vincular o servidor (padrão: 127.0.0.1)
- `ENVIRONMENT`: Ambiente de execução (development, production)

O servidor estará disponível em `http://localhost:8000` por padrão.

### 5. Acesse a Documentação Interativa
A aplicação inclui documentação interativa gerada automaticamente:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Interface interativa para testar os endpoints diretamente do navegador
  - Inclui exemplos de requisições e respostas
  - Permite autenticação direta na interface

- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  - Documentação mais limpa e focada na leitura
  - Útil para referência rápida

#### Autenticação na Documentação
1. Clique no botão "Authorize" no canto superior direito
2. Insira sua chave de API no formato: `Bearer sua-chave-aqui`
3. Clique em "Authorize" para ativar a autenticação

### Testes

#### Executar todos os testes
```bash
pytest
```

#### Executar testes com cobertura
```bash
pytest --cov=src/solar_api tests/
```

## Endpoints da API

### Autenticação
- **POST** `/auth/login`
  - Realiza login e retorna a chave de API do usuário
  - Formato: `email=usuario@exemplo.com&password=senha` (form-urlencoded)
  - Retorna: 
  ```json
  {
    "id": 1,
    "email": "usuario@exemplo.com",
    "is_active": true,
    "is_admin": false,
    "api_key": "sua-chave-de-api-aqui"
  }
  ```

- **POST** `/auth/rotate-key`
  - Gera uma nova chave de API para o usuário autenticado
  - Cabeçalho: `X-API-Key: sua-chave-atual`
  - Retorna: Nova chave de API

- **POST** `/auth/admin/rotate-key/{user_id}`
  - Gera uma nova chave de API para um usuário específico (apenas admin)
  - Cabeçalho: `X-API-Key: sua-chave-de-admin`
  - Retorna: Nova chave de API para o usuário

### Usuários
- **POST** `/users/`
  - Cria um novo usuário (apenas administradores)
  - Cabeçalho: `X-API-Key: sua-chave-de-admin`
  - Corpo:
  ```json
  {
    "email": "usuario@exemplo.com",
    "password": "senha_segura",
    "is_admin": false
  }
  ```
  - Retorna: Dados do usuário criado

- **GET** `/auth/me`
  - Retorna os dados do usuário autenticado
  - Cabeçalho: `X-API-Key: sua-chave-de-api`

- **GET** `/users/`
  - Lista todos os usuários (apenas administradores)
  - Cabeçalho: `X-API-Key: sua-chave-de-admin`
  - Parâmetros opcionais: 
    - `skip`: Número de registros para pular
    - `limit`: Limite de registros por página

- **GET** `/users/{user_id}`
  - Retorna um usuário específico
  - Cabeçalho: `X-API-Key: sua-chave-de-api`
  - Apenas o próprio usuário ou administrador pode acessar

- **PUT** `/users/{user_id}`
  - Atualiza um usuário
  - Cabeçalho: `X-API-Key: sua-chave-de-api`
  - Aceita atualizações parciais
  - Apenas o próprio usuário ou administrador pode atualizar
  - Exemplo de corpo:
  ```json
  {
    "email": "novo@email.com",
    "is_admin": true
  }
  ```

- **DELETE** `/users/{user_id}`
  - Remove um usuário (apenas administradores)
  - Cabeçalho: `X-API-Key: sua-chave-de-admin`

- **POST** `/users/{user_id}/change-password`
  - Altera a senha do usuário
  - Cabeçalho: `X-API-Key: sua-chave-de-api`
  - Corpo:
  ```json
  {
    "current_password": "senha_atual",
    "new_password": "nova_senha"
  }
  ```
  - Apenas o próprio usuário ou administrador pode alterar a senha

### Health Check
- **GET** `/health`
  - Retorna o status da API
  - Não requer autenticação
  - Resposta: `{"status": "ok"}`

### Cálculo de Produção Solar
- **POST** `/calculate`
  - Recebe os dados para o cálculo, faz a requisição à API do PVGIS e retorna o resultado.
  - **Autenticação**: Chave de API no cabeçalho `X-API-Key`
  - **Cabeçalho obrigatório**: `X-API-Key: sua-chave-de-api`

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
  -H "X-API-Key: sua-chave-de-api" \
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
  - **Autenticação**: Chave de API no cabeçalho `X-API-Key`
  - **Cabeçalho obrigatório**: `X-API-Key: sua-chave-de-api`

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
  - **Autenticação**: Chave de API no cabeçalho `X-API-Key`
  - **Cabeçalho obrigatório**: `X-API-Key: sua-chave-de-api`
  - **Parâmetros de URL**:
    - `model_id`: UUID do modelo

#### Criar um Novo Modelo
- **POST** `/models`
  - Cria um novo modelo de painel solar.
  - **Autenticação**: Chave de API no cabeçalho `X-API-Key`
  - **Cabeçalho obrigatório**: `X-API-Key: sua-chave-de-api`
  - **Corpo da Requisição (JSON)**:
    - `name`: Nome do modelo (obrigatório)
    - `capacity`: Capacidade em kWp (obrigatório, > 0)
    - `efficiency`: Eficiência em % (obrigatório, 0-100)
    - `manufacturer`: Fabricante (obrigatório)
    - `type`: Tipo do painel (ex: Monocristalino) (obrigatório)

#### Atualizar um Modelo
- **PUT** `/models/{model_id}`
  - Atualiza um modelo de painel existente. Aceita atualizações parciais.
  - **Autenticação**: Chave de API no cabeçalho `X-API-Key`
  - **Cabeçalho obrigatório**: `X-API-Key: sua-chave-de-api`
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
  - **Autenticação**: Chave de API no cabeçalho `X-API-Key`
  - **Cabeçalho obrigatório**: `X-API-Key: sua-chave-de-api`
  - **Parâmetros de URL**:
    - `model_id`: UUID do modelo a ser removido
