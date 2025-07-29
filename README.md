# AI CRM Multi-Agent System

AI-Powered CRM Multi-Agent System for Pre-Settlement Funding with intelligent document processing, communication management, and automated workflows.

## Overview

This system provides a comprehensive CRM solution with:
- Multi-agent AI workflows for case management
- Document intelligence and automated processing
- Pipedrive integration and synchronization
- Real-time communication tracking
- Automated plaintiff and law firm management
- Risk assessment and compliance monitoring

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup

1. **Clone and navigate to the repository**:
   ```bash
   git clone <repository-url>
   cd roncrm1
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/crm_db
   REDIS_URL=redis://localhost:6379
   JWT_SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**:
   ```bash
   uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## How to Sign In

The system uses JWT-based authentication. For development/demo purposes, use these credentials:

### Admin User
- **Email**: `admin@example.com`
- **Password**: `admin123`
- **Permissions**: Full system access including agent management

### Regular User  
- **Email**: `user@example.com`
- **Password**: `user123`
- **Permissions**: Read-only access to most resources

### Sign-in Process

1. Navigate to the login page at http://localhost:5173
2. Enter your email and password
3. Click "Sign in" to authenticate
4. You'll be redirected to the dashboard upon successful login

The system will:
- Validate your credentials against the backend API
- Issue JWT access and refresh tokens
- Store the access token in localStorage
- Set up API authorization headers automatically
- Redirect you to the main dashboard

### Authentication Features

- **JWT Token Management**: Automatic token refresh and secure storage
- **Role-based Access Control**: Different permission levels for admin/user roles
- **Protected Routes**: Automatic redirection for unauthenticated users
- **Session Management**: Persistent login across browser sessions

## Development

### Running Tests

Backend tests:
```bash
pytest
```

Frontend tests:
```bash
cd frontend && npm test
```

### Code Quality

Format code:
```bash
black src/
ruff check src/ --fix
```

Type checking:
```bash
mypy src/
```

## Architecture

- **Backend**: FastAPI with async/await, SQLAlchemy ORM, Alembic migrations
- **Frontend**: React with TypeScript, Vite, Tailwind CSS
- **Database**: PostgreSQL with async connections
- **Cache**: Redis for session management and caching
- **AI Integration**: OpenAI and Anthropic APIs for intelligent processing
- **Authentication**: JWT tokens with role-based permissions

## Key Features

- **Multi-Agent System**: Specialized AI agents for different business functions
- **Document Intelligence**: Automated document classification and extraction
- **Communication Management**: Email, SMS, and notification services
- **Pipedrive Integration**: Bi-directional sync with Pipedrive CRM
- **Real-time Updates**: WebSocket connections for live updates
- **Audit Logging**: Comprehensive activity tracking and compliance

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Support

For issues and questions, please check the documentation or create an issue in the repository.