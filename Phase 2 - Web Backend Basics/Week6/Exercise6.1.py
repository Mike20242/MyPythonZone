from flask import Flask, jsonify

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
    # Search for the todo with the matching ID
    todo = next((t for t in todos if t['id'] == todo_id), None)
    
    if todo is None:
        # Return a 404 error if todo is not found
        return jsonify({"error": "Todo not found"}), 404
        
    return jsonify(todo), 200

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, port=5000)
