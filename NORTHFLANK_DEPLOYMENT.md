# Northflank Deployment Guide for Suna (No Auth)

This guide deploys Suna to Northflank with authentication disabled for immediate access.

## Prerequisites

1. **Northflank Account**: Sign up at [northflank.com](https://northflank.com)
2. **GitHub Repository**: Your Suna code should be in a GitHub repository
3. **API Keys**: Basic LLM provider keys (Anthropic/OpenAI)

## Quick Deployment

### Option 1: Using Northflank CLI

1. **Install Northflank CLI**
   ```bash
   npm install -g @northflank/cli
   northflank login
   ```

2. **Deploy from configuration**
   ```bash
   northflank deploy --file northflank.json
   ```

### Option 2: Manual Setup

1. **Create Project**
   - Go to Northflank dashboard
   - Create new project
   - Connect your GitHub repository

2. **Add Redis Service**
   - Add Redis addon
   - Version: 7.0
   - Storage: 1GB

3. **Deploy Backend Service**
   - Source: `backend/` directory
   - Dockerfile: `backend/Dockerfile`
   - Port: 8000
   - Environment variables from `.env.northflank`

4. **Deploy Worker Service**
   - Source: `backend/` directory  
   - Dockerfile: `backend/Dockerfile`
   - Command: `uv run dramatiq --skip-logging --processes 2 --threads 2 run_agent_background`
   - Same environment variables as backend

5. **Deploy Frontend Service**
   - Source: `frontend/` directory
   - Dockerfile: `frontend/Dockerfile`
   - Port: 3000
   - Environment variables:
     - `NEXT_PUBLIC_DISABLE_AUTH=true`
     - `NEXT_PUBLIC_API_URL=<backend-service-url>`

## Required Environment Variables

Copy variables from `.env.northflank` and set:
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (required)
- `API_KEY_SECRET` (generate random string)
- `MCP_CREDENTIAL_ENCRYPTION_KEY` (generate random string)

## Post-Deployment

1. **Access Application**
   - Frontend URL will be provided by Northflank
   - Should redirect directly to dashboard (no login required)

2. **Test Basic Features**
   - Dashboard loads without authentication
   - Can create and interact with agents
   - Basic chat functionality works

## Re-enabling Authentication Later

To restore authentication:
1. Set `DISABLE_AUTH=false` and `NEXT_PUBLIC_DISABLE_AUTH=false`
2. Add Supabase environment variables
3. Redeploy services

## Troubleshooting

- Check service logs in Northflank dashboard
- Verify environment variables are set correctly
- Ensure Redis service is running and connected
