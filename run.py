"""
Entry point to run the ALTO application.
Usage:
    python run.py
"""
import os
from app import create_app

# Get configuration name from environment variable, default to 'development'
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # Default host 127.0.0.1, port 5000 with interactive debugger enabled
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
