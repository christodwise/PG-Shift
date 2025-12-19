# PG Shift ⚡

**Drop. Dump. Restore. Done.**

A modern, agentic PostgreSQL database migration tool with a beautiful web interface.

## Features

- 🔐 **Secure Access** - Admin authentication required
- 🛡️ **Safe Mode** - Preflight checks & version validation
- ⚡ **Live Stats** - Real-time table & row analysis
- 🤖 **Agent Ready** - Structured logs & clear visual states
- 🔄 **Smart Workflow** - Guided 4-step wizard interface
- 💾 **Connection Manager** - Save & reuse database profiles
- ⚠️ **Safety First** - Explicit confirmations for destructive operations

## Quick Start

### Default Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Docker (Recommended)

```bash
# Using Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t pg-shift .
docker run -p 8501:8501 -v $(pwd)/data:/app/data pg-shift
```

Access the app at: http://localhost:8501

### Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Prerequisites

- **PostgreSQL Client Tools** (`pg_dump`, `pg_restore`)
  - macOS: `brew install postgresql`
  - Ubuntu/Debian: `apt-get install postgresql-client`
  - Docker: Already included in the image

## How It Works

1. **Login** - Authenticate with admin credentials
2. **Configure Source** - Connect to your source PostgreSQL database
3. **Configure Target** - Set up the destination database
4. **Review & Confirm** - Check preflight validations
5. **Execute Migration** - Watch live progress with structured logs
6. **Return Home** - Easy navigation back to start after completion

## Migration Process

- Uses `pg_dump` (custom format) for source backup
- Drops all existing public tables in target database
- Restores using `pg_restore`
- Live logging throughout the process

## Safety Features

- Password-protected admin access
- Version compatibility checking
- Connection validation before migration
- Explicit database name confirmation
- Force/bypass option for advanced users
- No password logging (uses `PGPASSWORD` environment variable)

## Security

- Admin credentials use SHA-256 password hashing
- Default password should be changed in production
- To change password, modify `ADMIN_PASSWORD_HASH` in `app.py`

## Configuration

Connection details are stored locally in `connections.db` (SQLite).

## Made with ❤️ by Lifetrenz DevOps Team
