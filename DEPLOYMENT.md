# Deployment Guide

This guide covers how to deploy the Stock Analysis Tool to various platforms.

## Prerequisites

- Python 3.7+ installed locally
- Git installed
- Account on your chosen deployment platform

## Local Testing

Before deploying, test the application locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI app
python app.py
# Or use uvicorn directly:
# uvicorn app:app --reload
```

Visit `http://localhost:8000` to test the application.

**FastAPI Features:**
- Automatic API documentation at `http://localhost:8000/docs` (Swagger UI)
- Alternative API docs at `http://localhost:8000/redoc` (ReDoc)
- Type validation and automatic request/response models

## Deployment Options

### Option 1: Heroku (Recommended for beginners)

1. **Install Heroku CLI**
   - Download from https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push heroku main
   ```

5. **Open your app**
   ```bash
   heroku open
   ```

**Note**: Heroku free tier was discontinued. You'll need a paid plan or use alternatives.

### Option 2: Railway

1. **Sign up at Railway**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository

3. **Configure**
   - Railway will auto-detect Python
   - Add environment variables if needed
   - Deploy automatically on git push

4. **Get your URL**
   - Railway provides a URL automatically
   - You can add a custom domain

### Option 3: Render

1. **Sign up at Render**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
   - Set environment variables if needed

4. **Deploy**
   - Render will deploy automatically
   - Get your URL from the dashboard

### Option 4: PythonAnywhere

1. **Sign up at PythonAnywhere**
   - Go to https://www.pythonanywhere.com
   - Create a free account

2. **Upload your code**
   - Use the Files tab to upload your project
   - Or use Git to clone your repository

3. **Configure Web App**
   - Go to Web tab
   - Create a new web app
   - Select "Manual configuration" and Python 3.10
   - Point WSGI file to your `app.py` file
   - In the WSGI configuration file, use:
     ```python
     import sys
     path = '/home/yourusername/stock-trading'
     if path not in sys.path:
         sys.path.append(path)
     
     from app import app as application
     ```
   - Or use uvicorn in a scheduled task/always-on task

4. **Set up static files**
   - Configure static files mapping:
     - URL: `/static/`
     - Directory: `/home/yourusername/stock-trading/static/`

5. **Reload**
   - Click the green "Reload" button

### Option 5: Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Create app**
   ```bash
   fly launch
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

### Option 6: DigitalOcean App Platform

1. **Sign up at DigitalOcean**
   - Go to https://www.digitalocean.com

2. **Create App**
   - Go to App Platform
   - Connect GitHub repository
   - Auto-detect settings

3. **Configure**
   - Build command: `pip install -r requirements.txt`
   - Run command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Deploy**
   - DigitalOcean will deploy automatically

### Option 7: Replit

Replit is a cloud-based IDE that makes it easy to deploy Python applications.

1. **Sign up at Replit**
   - Go to https://replit.com
   - Sign up for a free account (or use GitHub to sign in)

2. **Create a new Repl**
   - Click "Create Repl" or "+" button
   - Select "Python" as the language
   - Name your Repl (e.g., "stock-analysis-tool")
   - Click "Create Repl"

3. **Import your code**
   - **Option A: Using Git**
     - In the Replit shell, run:
       ```bash
       git clone https://github.com/yourusername/stock-trading.git .
       ```
   - **Option B: Manual upload**
     - Click the "Files" icon in the sidebar
     - Click the three dots menu → "Upload folder"
     - Upload your project files
   - **Option C: Copy-paste files**
     - Create files manually in Replit and copy-paste your code

4. **Configure Replit**
   - Replit should auto-detect Python and install dependencies
   - If not, run in the shell:
     ```bash
     pip install -r requirements.txt
     ```

5. **Configure the run command**
   - The `.replit` file is already included in the project
   - It's configured to run: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Replit automatically sets the `$PORT` environment variable
   - If you need to customize, edit the `.replit` file or use Replit's "Run" button settings

6. **Set up the web server**
   - Click the "Run" button (or press `Ctrl+Enter`)
   - Replit will start your FastAPI server
   - You'll see a webview panel open with your app
   - The URL will be something like: `https://stock-analysis-tool.yourusername.repl.co`

7. **Make it always-on (optional)**
   - For free accounts, Repls sleep after inactivity
   - Upgrade to Hacker plan for always-on Repls
   - Or use a service like UptimeRobot to ping your Repl periodically

8. **Environment Variables (if needed)**
   - Click the "Secrets" tab (lock icon) in the sidebar
   - Add environment variables as key-value pairs
   - They'll be available as `os.environ.get("KEY")`

**Replit Tips:**
- Use the built-in terminal for debugging
- Files persist between sessions
- Free tier includes 0.5 GB RAM and 0.5-1 GB storage
- Upgrade for more resources and always-on hosting
- Replit automatically handles HTTPS/SSL certificates

## Environment Variables

If you need to set environment variables:

- **PORT**: Usually set automatically by the platform
- **ENVIRONMENT**: Set to `production` for production deployments (optional)

## Database Considerations

The application uses SQLite (`stock_cache.db`). For production:

1. **Ephemeral filesystems**: Some platforms (like Heroku) have ephemeral filesystems. The database will be reset on each deploy. Consider:
   - Using an external database (PostgreSQL, MySQL)
   - Using cloud storage for the database file
   - Accepting that cache will be rebuilt on each deploy

2. **Persistent storage**: Platforms like Railway, Render, and PythonAnywhere maintain files between deploys.

## Troubleshooting

### Application won't start
- Check logs: `heroku logs --tail` (Heroku) or platform-specific log commands
- Ensure `uvicorn` is in requirements.txt
- Verify `Procfile` is correct (should use `uvicorn app:app`)

### Database errors
- Ensure database file is writable
- Check file permissions
- Consider using external database for production

### Timeout issues
- Stock analysis can take several minutes
- Consider adding a background job queue (Celery, RQ)
- Increase timeout limits on your platform

### Static files not loading
- Verify static file paths in FastAPI (mounted at `/static`)
- Check platform-specific static file configuration
- Ensure `static/` directory exists and is accessible

## Performance Tips

1. **Caching**: The app already uses SQLite caching. For better performance:
   - Use Redis or Memcached
   - Implement request caching

2. **Background Jobs**: For long-running analysis:
   - Use Celery with Redis/RabbitMQ
   - Implement async processing
   - Show progress to users

3. **Database**: For production:
   - Migrate to PostgreSQL
   - Use connection pooling
   - Optimize queries

## Security Considerations

1. **Environment Variables**: Never commit secrets
2. **Rate Limiting**: Add rate limiting to prevent abuse
3. **Input Validation**: Validate all user inputs
4. **HTTPS**: Always use HTTPS in production

## Monitoring

Consider adding:
- Error tracking (Sentry)
- Analytics (Google Analytics)
- Uptime monitoring (UptimeRobot, Pingdom)
- Application monitoring (New Relic, Datadog)

