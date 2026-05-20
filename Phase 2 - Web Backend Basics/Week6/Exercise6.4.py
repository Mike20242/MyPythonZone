from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest, MethodNotAllowed, NotFound

app = Flask(__name__)

# In-memory database for todos
todos = [
    {"id": 1, "title": "Buy groceries", "completed": False},
    {"id": 2, "title": "Learn Flask REST API", "completed": True},
    {"id": 3, "title": "Finish homework", "completed": False}
]

# --- Custom Error Handlers ---

@app.errorhandler(400)
def bad_request(error):
    # Returns JSON instead of HTML for 400 errors
    message = error.description if hasattr(error, 'description') else "Bad request"
    return jsonify({"error": "Bad Request", "message": message}), 400

@app.errorhandler(404)
def not_found(error):
    # Returns JSON instead of HTML for 404 errors
    message = error.description if hasattr(error, 'description') else "Resource not found"
    return jsonify({"error": "Not Found", "message": message}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "The method is not allowed for the requested URL."}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred on the server."}), 500


# --- API Routes ---

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo is None:
        # Use abort/NotFound or return directly with JSON
        raise NotFound(f"Todo with ID {todo_id} does not exist.")
    return jsonify(todo), 200


@app.route('/todos', methods=['POST'])
def create_todo():
    # Force JSON parsing, return 400 if parsing fails
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")
        
    # Validation: check if title exists and is not empty
    if 'title' not in data:
        raise BadRequest("Field 'title' is required.")
        
    title = data['title']
    if not isinstance(title, str) or not title.strip():
        raise BadRequest("Field 'title' must be a non-empty string.")
        
    # Validation: check completed if provided
    completed = data.get('completed', False)
    if not isinstance(completed, bool):
        raise BadRequest("Field 'completed' must be a boolean value.")
        
    new_id = max(t['id'] for t in todos) + 1 if todos else 1
    new_todo = {
        "id": new_id,
        "title": title.strip(),
        "completed": completed
    }
    todos.append(new_todo)
    return jsonify(new_todo), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo is None:
        raise NotFound(f"Todo with ID {todo_id} does not exist.")
        
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")
        
    # Check if they passed nothing
    if 'title' not in data and 'completed' not in data:
        raise BadRequest("At least one field ('title' or 'completed') must be provided to update.")
        
    # Validation: title (if provided)
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str) or not title.strip():
            raise BadRequest("Field 'title' must be a non-empty string.")
        todo['title'] = title.strip()
        
    # Validation: completed (if provided)
    if 'completed' in data:
        completed = data['completed']
        if not isinstance(completed, bool):
            raise BadRequest("Field 'completed' must be a boolean value.")
        todo['completed'] = completed
        
    return jsonify(todo), 200


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo is None:
        raise NotFound(f"Todo with ID {todo_id} does not exist.")
        
    todos = [t for t in todos if t['id'] != todo_id]
    return jsonify({"message": "Todo deleted successfully", "id": todo_id}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
