# E-commerce con Chat IA 🛍️🤖

API REST de e-commerce de zapatos con asistente de ventas inteligente, construida con **Clean Architecture** y **Google Gemini AI**.

## Descripción

Sistema que permite a los clientes consultar un catálogo de zapatos y conversar con un asistente de IA que les ayuda a encontrar el producto ideal. El asistente recuerda el contexto de la conversación para dar respuestas coherentes.

## Características Principales

- **Catálogo de productos**: Listado, búsqueda por marca y categoría.
- **Chat con IA**: Asistente conversacional powered by Google Gemini.
- **Memoria conversacional**: Historial persistido para contexto coherente.
- **Clean Architecture**: 3 capas bien separadas (Domain, Application, Infrastructure).
- **Documentación automática**: Swagger UI disponible en `/docs`.
- **Containerización**: Docker y docker-compose listos para producción.

## Arquitectura del Sistema

```
CLIENTE (Postman, Frontend)
         ↓ HTTP
INFRASTRUCTURE LAYER
  ├── FastAPI (main.py)          → Endpoints HTTP
  ├── Repositories (SQLAlchemy) → Acceso a datos
  └── GeminiService             → Google Gemini AI
         ↓
APPLICATION LAYER
  ├── ProductService             → Casos de uso de productos
  ├── ChatService               → Caso de uso de chat con IA
  └── DTOs (Pydantic)           → Validación de datos
         ↓
DOMAIN LAYER
  ├── Entities (Product, ChatMessage, ChatContext)
  ├── Interfaces (IProductRepository, IChatRepository)
  └── Exceptions (ProductNotFoundError, ChatServiceError)
```

## Tecnologías

| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| Python | 3.11+ | Lenguaje base |
| FastAPI | 0.104+ | Framework web |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.5+ | Validación |
| SQLite | — | Base de datos |
| Google Gemini | gemini-2.5-flash | IA conversacional |
| Docker | — | Containerización |
| Pytest | 7.4+ | Testing |

## Estructura del Proyecto

```
e-commerce-chat-ai/
├── src/
│   ├── domain/               # Capa de Dominio
│   │   ├── entities.py       # Product, ChatMessage, ChatContext
│   │   ├── repositories.py   # IProductRepository, IChatRepository
│   │   └── exceptions.py     # Excepciones del dominio
│   ├── application/          # Capa de Aplicación
│   │   ├── dtos.py           # DTOs con validación Pydantic
│   │   ├── product_service.py
│   │   └── chat_service.py
│   └── infrastructure/       # Capa de Infraestructura
│       ├── api/main.py       # FastAPI endpoints
│       ├── db/               # SQLAlchemy models y configuración
│       ├── repositories/     # Implementaciones SQL
│       └── llm_providers/    # Google Gemini
├── tests/
│   ├── test_entities.py
│   └── test_services.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

## Instalación

### Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- API Key de Google Gemini ([obtener aquí](https://aistudio.google.com/app/apikey))

### Pasos de Instalación Local

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd e-commerce-chat-ai
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY
```

5. **Ejecutar la aplicación**
```bash
cd src
uvicorn infrastructure.api.main:app --reload
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto:

```env
GEMINI_API_KEY=AIzaSy...tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

## Uso con Docker

```bash
# Primera vez (construye la imagen)
docker-compose up --build

# Ejecuciones siguientes
docker-compose up

# En segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/products` | Listar todos los productos |
| GET | `/products/{id}` | Obtener producto por ID |
| POST | `/chat` | Enviar mensaje al asistente IA |
| GET | `/chat/history/{session_id}` | Obtener historial de sesión |
| DELETE | `/chat/history/{session_id}` | Eliminar historial de sesión |
| GET | `/health` | Estado de la API |

### Ejemplo de uso del chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "usuario_001",
    "message": "Busco zapatillas Nike para correr, talla 42"
  }'
```

**Respuesta:**
```json
{
  "session_id": "usuario_001",
  "user_message": "Busco zapatillas Nike para correr, talla 42",
  "assistant_message": "¡Hola! Tengo el Air Max 90 de Nike en talla 42 por $150. ¿Te interesa?",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Ejemplo de consulta de productos

```bash
curl http://localhost:8000/products
```

## Documentación Interactiva

Con la aplicación corriendo, acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio

# Correr todos los tests
pytest

# Con reporte de cobertura
pip install pytest-cov
pytest --cov=src --cov-report=term-missing

# Solo tests de entidades
pytest tests/test_entities.py -v

# Solo tests de servicios
pytest tests/test_services.py -v
```

## Patrones de Diseño Implementados

- **Clean Architecture**: Separación estricta en 3 capas independientes.
- **Repository Pattern**: Abstracción del acceso a datos mediante interfaces.
- **Dependency Injection**: Los servicios reciben sus dependencias, no las crean.
- **Service Layer**: Servicios de aplicación que orquestan los casos de uso.
- **DTO Pattern**: Objetos de transferencia de datos para comunicación entre capas.

## Autor

Universidad EAFIT — Construcción de Software

## Licencia

Proyecto académico — Universidad EAFIT
