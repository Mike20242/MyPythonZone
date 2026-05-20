from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database for todos
todos = [
    {"id": 1, "title": "Buy groceries", "completed": False},
    {"id": 2, "title": "Learn Flask REST API", "completed": True},
    {"id": 3, "title": "Finish homework", "completed": False}
]

# Route to get all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200

# Route to get a single todo by ID
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo), 200

# Route to create a new todo
@app.route('/todos', methods=['POST'])
def create_todo():
    # Get JSON data from the request body
    data = request.get_json()
    
    # If no data is passed or it is not JSON
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
        
    title = data.get('title')
    if not title:
        return jsonify({"error": "Title is required"}), 400
        
    # Generate a new unique ID
    new_id = max(t['id'] for t in todos) + 1 if todos else 1
    
    # Create the new todo item
    new_todo = {
        "id": new_id,
        "title": title,
        "completed": data.get('completed', False) # Default to False if not provided
    }
    
    # Add to our in-memory list
    todos.append(new_todo)
    
    # Return the created todo with 201 Created status
    return jsonify(new_todo), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
