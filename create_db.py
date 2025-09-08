import os
# Set dummy env var before importing app to prevent SDK error
os.environ['MERCADOPAGO_ACCESS_TOKEN'] = 'dummy-token-for-scripts'

from app import app, db

# Ensure the instance folder exists
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_path, exist_ok=True)

print(f"Ensuring database is created at: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    db.create_all()

print("Database tables created successfully in the instance folder.")
