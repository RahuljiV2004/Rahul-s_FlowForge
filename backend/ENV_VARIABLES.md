# Backend Environment Variables

This document lists all environment variables required for the backend application.

## Required Variables

### 1. `DATABASE_URL`
- **Description**: PostgreSQL database connection string
- **Format**: `postgresql://username:password@host:port/database_name`
- **Default**: `postgresql://postgres:postgres@localhost:5432/workflow_db`
- **Example**: 
  ```
  DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflow_db
  ```
- **When using Docker Compose**: `postgresql://postgres:postgres@postgres:5432/workflow_db`
- **Required**: Yes (but has a default for local development)

### 2. `OPENAI_API_KEY` OR `GOOGLE_API_KEY` (at least one required)
- **Description**: You need at least ONE of these API keys to use the application
- **Required**: At least one API key must be configured

#### Option A: `OPENAI_API_KEY`
- **Description**: API key for OpenAI services (for embeddings and LLM)
- **Where to get**: https://platform.openai.com/api-keys
- **Format**: `sk-...` (starts with "sk-")
- **Example**: 
  ```
  OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```
- **Required**: Yes (if using OpenAI for embeddings or LLM)

#### Option B: `GOOGLE_API_KEY`
- **Description**: API key for Google Gemini services (for embeddings and LLM)
- **Where to get**: https://makersuite.google.com/app/apikey
- **Format**: String (no specific prefix)
- **Example**: 
  ```
  GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  ```
- **Required**: Yes (if using Google Gemini instead of OpenAI)

## Optional Variables

### 3. `GOOGLE_API_KEY`
- **Description**: API key for Google Gemini services (for embeddings and LLM)
- **Where to get**: https://makersuite.google.com/app/apikey
- **Format**: String (no specific prefix)
- **Example**: 
  ```
  GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
  ```
- **Required**: No (only if you want to use Gemini - you need either this OR OPENAI_API_KEY)
- **Note**: If you provide this instead of OPENAI_API_KEY, make sure to configure your workflows to use "gemini" as the LLM provider and embedding model

### 4. `SERPAPI_API_KEY`
- **Description**: API key for SerpAPI (web search service)
- **Where to get**: https://serpapi.com/users/sign_up
- **Format**: String
- **Example**: 
  ```
  SERPAPI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```
- **Required**: No (only needed if using SerpAPI for web search in LLM Engine component)

### 5. `BRAVE_API_KEY`
- **Description**: API key for Brave Search API (alternative web search service)
- **Where to get**: https://brave.com/search/api/
- **Format**: String
- **Example**: 
  ```
  BRAVE_API_KEY=BSA_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  ```
- **Required**: No (only needed if using Brave Search instead of SerpAPI)
- **Note**: You need either SerpAPI or Brave API key if you want web search functionality

### 6. `SECRET_KEY`
- **Description**: Secret key for application security (for session management, etc.)
- **Format**: Random string
- **Example**: 
  ```
  SECRET_KEY=your-secret-key-here-change-this-in-production
  ```
- **Required**: No (not currently used, but good practice to set)
- **Generate**: You can generate a secure key with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 7. `ENVIRONMENT`
- **Description**: Application environment (development, production, etc.)
- **Format**: String
- **Example**: 
  ```
  ENVIRONMENT=development
  ```
- **Required**: No (optional, for logging/debugging purposes)
- **Values**: `development`, `production`, `staging`

## Setup Instructions

### 1. Create `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

### 2. Edit `.env` file and add your values:

```env
# Database (use default for local, or update for Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflow_db

# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional: Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here

# Optional: Web Search APIs (need at least one if using web search)
SERPAPI_API_KEY=your-serpapi-key-here
BRAVE_API_KEY=your-brave-api-key-here

# Optional: Application settings
SECRET_KEY=generate-a-random-secret-key
ENVIRONMENT=development
```

### 3. For Docker Compose:

If using `docker-compose.yml`, update the `DATABASE_URL` to:
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/workflow_db
```

## Minimum Configuration

**Option 1: Using OpenAI only**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflow_db
OPENAI_API_KEY=sk-your-openai-key-here
```

**Option 2: Using Google Gemini only**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflow_db
GOOGLE_API_KEY=your-google-api-key-here
```

**Option 3: Using both (most flexible)**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/workflow_db
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

### Important Notes:
- **You MUST configure at least ONE of OPENAI_API_KEY or GOOGLE_API_KEY**
- If using only Google API key, make sure to:
  - Set "gemini" as the LLM provider in your LLM Engine component
  - Set "gemini" as the embedding model in your Knowledge Base component
- If using only OpenAI API key, the default settings will work automatically

## Feature-Specific Requirements

| Feature | Required Variables |
|---------|-------------------|
| Basic Workflows | `DATABASE_URL`, `OPENAI_API_KEY` |
| Document Processing | `DATABASE_URL`, `OPENAI_API_KEY` |
| OpenAI LLM | `OPENAI_API_KEY` |
| Gemini LLM | `GOOGLE_API_KEY` |
| OpenAI Embeddings | `OPENAI_API_KEY` |
| Gemini Embeddings | `GOOGLE_API_KEY` |
| Web Search (SerpAPI) | `SERPAPI_API_KEY` |
| Web Search (Brave) | `BRAVE_API_KEY` |

## Security Best Practices

1. **Never commit `.env` file** to version control (it's in `.gitignore`)
2. **Use strong API keys** and rotate them periodically
3. **Restrict API key permissions** when possible
4. **Use different keys** for development and production
5. **Set up API usage limits** in your API provider dashboards

## Troubleshooting

### Error: "OPENAI_API_KEY not found"
- Make sure `.env` file exists in `backend/` directory
- Check that the variable name is exactly `OPENAI_API_KEY` (case-sensitive)
- Restart the backend server after changing `.env`

### Error: "Database connection failed"
- Verify PostgreSQL is running
- Check `DATABASE_URL` format is correct
- Ensure database exists: `createdb workflow_db`

### Error: "API key invalid"
- Verify the API key is correct (no extra spaces)
- Check the API key hasn't expired
- Ensure you have credits/quota available
