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
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host=host, port=port, debug=debug)
