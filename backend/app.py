from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Read RDS config from environment variables
db_config = {
    'host': os.environ.get('RDS_HOST', 'localhost'),
    'user': os.environ.get('RDS_USER', 'root'),
    'password': os.environ.get('RDS_PASSWORD', 'password'),
    'database': os.environ.get('RDS_DB', 'todo_app')
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Initialize DB (create table if not exists)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            text VARCHAR(255) NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Routes
@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM todos ORDER BY created_at DESC')
    todos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    text = data.get('text')
    completed = data.get('completed', False)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO todos (text, completed) VALUES (%s, %s)', (text, completed))
    conn.commit()
    todo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({'id': todo_id, 'text': text, 'completed': completed})

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    completed = data.get('completed')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE todos SET completed=%s WHERE id=%s', (completed, todo_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': todo_id, 'completed': completed})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE id=%s', (todo_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    # Listen on all interfaces so frontend EC2 can reach it
    app.run(host='0.0.0.0', port=5000)
