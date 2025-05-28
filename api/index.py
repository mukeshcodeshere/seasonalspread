# api/index.py

from dash_launcher import app

# Vercel expects the server to be exposed as `application`
application = app.server
