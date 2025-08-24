# Railway Deployment Guide for Suna

This guide will help you deploy your Suna AI agent platform to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your Suna code should be in a GitHub repository
3. **Required API Keys**: You'll need various API keys for the services Suna integrates with

## Deployment Options

### Option 1: Single Service Deployment (Recommended for Testing)

This deploys everything as a single service, which is simpler but less scalable.

1. **Connect Repository**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Suna repository

2. **Configure Environment Variables**
   - In your Railway project, go to the service settings
   - Add all variables from `.env.railway` file
   - **Required variables:**
     ```
     ENV_MODE=production
     SUPABASE_URL=your_supabase_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
     ANTHROPIC_API_KEY=your_anthropic_key
     OPENAI_API_KEY=your_openai_key
     MODEL_TO_USE=claude-3-5-sonnet-20241022
     API_KEY_SECRET=your_random_secret_key
     MCP_CREDENTIAL_ENCRYPTION_KEY=your_encryption_key
     ```

3. **Add Redis Service**
   - In your Railway project, click "New Service"
   - Select "Database" → "Redis"
   - Railway will automatically set up Redis and provide connection variables

4. **Deploy**
   - Railway will automatically deploy when you push to your main branch
   - Check the deployment logs for any issues

### Option 2: Multi-Service Deployment (Production Ready)

For production, deploy as separate services for better scalability and monitoring.

1. **Create Services**
   - **Backend API Service**: Deploy from `backend/` directory
   - **Frontend Service**: Deploy from `frontend/` directory  
   - **Worker Service**: Deploy from `backend/` directory with worker command
   - **Redis Service**: Add Redis database service

2. **Configure Each Service**
   
   **Backend Service:**
   - Source: `backend/`
   - Build Command: `uv sync --locked`
   - Start Command: `uv run gunicorn api:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   
   **Frontend Service:**
   - Source: `frontend/`
   - Build Command: `npm ci && npm run build`
   - Start Command: `node server.js`
   
   **Worker Service:**
   - Source: `backend/`
   - Build Command: `uv sync --locked`
   - Start Command: `uv run dramatiq --skip-logging --processes 2 --threads 2 run_agent_background`

3. **Environment Variables**
   - Add the same environment variables to all services
   - Use Railway's service references for internal communication:
     ```
     REDIS_HOST=${{Redis.RAILWAY_PRIVATE_DOMAIN}}
     REDIS_PORT=${{Redis.RAILWAY_TCP_PROXY_PORT}}
     ```

## Required External Services

### 1. Supabase (Database & Auth)
- Create a Supabase project at [supabase.com](https://supabase.com)
- Get your project URL and API keys
- Run the database migrations (check `backend/` for SQL files)

### 2. Daytona (Code Execution Sandbox)
- Sign up at [daytona.io](https://daytona.io)
- Create API key and get server URL
- This is required for code execution features

### 3. LLM Providers
- **Anthropic**: Get API key from [console.anthropic.com](https://console.anthropic.com)
- **OpenAI**: Get API key from [platform.openai.com](https://platform.openai.com)

### 4. Optional Services
- **Tavily**: Web search API ([tavily.com](https://tavily.com))
- **Firecrawl**: Web scraping API ([firecrawl.dev](https://firecrawl.dev))
- **Langfuse**: Observability ([langfuse.com](https://langfuse.com))

## Environment Variables Setup

1. Copy variables from `.env.railway` to your Railway project
2. Replace placeholder values with your actual API keys
3. **Critical variables to set:**
   - `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
   - `API_KEY_SECRET` (generate a random string)
   - `MCP_CREDENTIAL_ENCRYPTION_KEY` (generate a random string)
   - `DAYTONA_API_KEY`, `DAYTONA_SERVER_URL`, `DAYTONA_TARGET`

## Post-Deployment Steps

1. **Verify Services**
   - Check that all services are running in Railway dashboard
   - Test the frontend URL provided by Railway

2. **Database Setup**
   - Run any required database migrations
   - Set up initial data if needed

3. **Test Core Features**
   - Create a test account
   - Try basic chat functionality
   - Test code execution (requires Daytona)

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are properly specified
   - Verify Python version compatibility (requires 3.11+)
   - Check Node.js version (requires 22+)

2. **Runtime Errors**
   - Check environment variables are set correctly
   - Verify external service connectivity
   - Check Railway logs for detailed error messages

3. **Database Connection Issues**
   - Verify Supabase credentials
   - Check network connectivity
   - Ensure database schema is up to date

### Monitoring

- Use Railway's built-in monitoring
- Set up Langfuse for LLM call observability
- Monitor resource usage and scale as needed

## Scaling Considerations

- **CPU**: Backend and worker services are CPU intensive
- **Memory**: Increase memory for services handling large documents
- **Redis**: Consider Redis persistence for production
- **Database**: Monitor Supabase usage and upgrade plan as needed

## Security Notes

- All API keys should be set as environment variables, never hardcoded
- Use Railway's private networking between services
- Enable HTTPS (Railway provides this automatically)
- Regularly rotate API keys and secrets
- Monitor access logs and set up alerts

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Suna Issues: [GitHub Issues](https://github.com/kortix-ai/suna/issues)
- Discord: [Kortix Community](https://discord.gg/Py6pCBUUPw)
