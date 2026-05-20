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
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
        
    title = data.get('title')
    if not title:
        return jsonify({"error": "Title is required"}), 400
        
    new_id = max(t['id'] for t in todos) + 1 if todos else 1
    new_todo = {
        "id": new_id,
        "title": title,
        "completed": data.get('completed', False)
    }
    todos.append(new_todo)
    return jsonify(new_todo), 201

# Route to update a todo (PUT)
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
        
    # Update fields if provided in request
    if 'title' in data:
        todo['title'] = data['title']
    if 'completed' in data:
        todo['completed'] = data['completed']
        
    return jsonify(todo), 200

# Route to delete a todo (DELETE)
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
        
    # Remove the todo from the list
    todos = [t for t in todos if t['id'] != todo_id]
    
    return jsonify({"message": "Todo deleted successfully", "id": todo_id}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
