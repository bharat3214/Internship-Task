from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import JWT_SECRET_KEY, init_postgres_table
from routes.auth import auth_bp
from routes.todos import todos_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

# Initialize JWT
jwt = JWTManager(app)

# Enable CORS
CORS(app)

# Initialize PostgreSQL table
try:
    init_postgres_table()
    print("PostgreSQL table initialized successfully")
except Exception as e:
    print(f"Error initializing PostgreSQL table: {e}")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(todos_bp, url_prefix='/api')

@app.route('/')
def home():
    return {'message': 'Todo App API is running'}

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
