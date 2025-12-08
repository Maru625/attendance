# Kada Commute System

Google Sheets based attendance management system.

## Setup

### 1. Prerequisites
- Python 3.11+
- `uv` package manager

### 2. Installation
Initialize the project and install dependencies:
```bash
uv init
uv add gspread google-auth
```

### 3. Google Sheets Configuration
Place your service account key file as `kada-admin.json` in the project root.
*Note: This file is ignored by git.*

## Git Setup
Commands to link to the remote repository:

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit"

# Rename branch to main
git branch -M main

# Add Remote
git remote add origin https://github.com/Maru625/attendance.git

# Push
git push -u origin main
```

## Usage

Run the application:
```bash
uv run main.py
```
