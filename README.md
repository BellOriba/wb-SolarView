# SolarView API

1. **Cálculo de Produção Solar**: Integração com a API [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) da Comissão Europeia para estimar a produção de energia de painéis solares com base em localização e características técnicas.

2. **Gerenciamento de Modelos de Painéis**: Sistema completo para cadastro, consulta, atualização e remoção de modelos de painéis solares.

3. **Autenticação e Autorização**: Sistema de usuários com diferentes níveis de permissão (usuários comuns e administradores).

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

2. Edite o arquivo `.env` com suas configurações.

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

### 5. Acesse a Documentação Interativa
A aplicação inclui documentação interativa gerada automaticamente:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Interface interativa para testar os endpoints diretamente do navegador
  - Permite autenticação direta na interface

- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  - Documentação mais limpa e focada na leitura
  - Útil para referência rápida

#### Autenticação na Documentação
1. Clique no botão "Authorize" no canto superior direito
2. Insira sua chave de API.
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

## Testes

O projeto inclui uma suíte abrangente de testes automatizados para garantir a qualidade e estabilidade do código.

### Estrutura de Testes

Os testes estão organizados nos seguintes arquivos:

- `tests/test_auth.py`: Testes para autenticação e gerenciamento de usuários
- `tests/test_panels.py`: Testes para gerenciamento de painéis solares
- `tests/test_calculations.py`: Testes para cálculos de produção solar
- `tests/conftest.py`: Configurações e fixtures para os testes
- `tests/test_utils.py`: Utilitários para auxiliar nos testes

### Como Executar os Testes

1. **Instalar as dependências de desenvolvimento**
   ```bash
   pip install pytest pytest-cov httpx aiosqlite
   ```

2. **Executar todos os testes**
   ```bash
   pytest
   ```

3. **Executar testes com cobertura**
   ```bash
   pytest --cov=src --cov-report=term-missing --cov-report=html
   ```
   Isso irá gerar:
   - Um relatório no terminal mostrando a cobertura de código
   - Uma pasta `htmlcov/` com um relatório HTML detalhado

4. **Executar um arquivo de teste específico**
   ```bash
   pytest tests/test_auth.py -v
   ```

5. **Executar um teste específico**
   ```bash
   pytest tests/test_auth.py::test_login_success -v
   ```

### Cobertura de Testes

O projeto utiliza o `pytest-cov` para medir a cobertura de código. O objetivo é manter uma cobertura alta, preferencialmente acima de 80%.

- Para ver a cobertura atual, execute:
  ```bash
  pytest --cov=src --cov-report=term-missing
  ```

- Para gerar um relatório HTML detalhado:
  ```bash
  pytest --cov=src --cov-report=html
  ```
  E então abra `htmlcov/index.html` em um navegador.

- Para ver a cobertura e relatório HTML detalhado:
  ```bash
  pytest --cov=src --cov-report=term-missing --cov-report=html -v
  ```
  E então abra `htmlcov/index.html` em um navegador.

### Testes de Integração

Os testes de integração verificam a interação entre diferentes componentes da aplicação, incluindo:

- Conexão com o banco de dados
- Autenticação e autorização
- Chamadas a APIs externas (mockadas)

### Testes de Aceitação

Os testes de aceitação verificam se os requisitos do usuário final estão sendo atendidos, simulando interações reais com a API.

### Mocking

Para evitar chamadas reais a serviços externos (como a API do PVGIS), utilizamos mocks nos testes.
