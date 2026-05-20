from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, MethodNotAllowed

app = Flask(__name__)

# Mock database of books
books = [
    {
        "id": 1,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "published_year": 1960,
        "genre": "Fiction"
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "published_year": 1949,
        "genre": "Dystopian"
    },
    {
        "id": 3,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "published_year": 1925,
        "genre": "Classic"
    }
]

# --- Custom Error Handlers ---

@app.errorhandler(400)
def bad_request(error):
    message = error.description if hasattr(error, 'description') else "Bad request"
    return jsonify({"error": "Bad Request", "message": message}), 400

@app.errorhandler(404)
def not_found(error):
    message = error.description if hasattr(error, 'description') else "Resource not found"
    return jsonify({"error": "Not Found", "message": message}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "The method is not allowed for the requested URL."}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred on the server."}), 500


# --- API Routes ---

# GET /books - Retrieve all books (with optional filtering)
@app.route('/books', methods=['GET'])
def get_books():
    genre = request.args.get('genre')
    author = request.args.get('author')
    
    filtered_books = books
    if genre:
        filtered_books = [b for b in filtered_books if b['genre'].lower() == genre.lower()]
    if author:
        filtered_books = [b for b in filtered_books if author.lower() in b['author'].lower()]
        
    return jsonify(filtered_books), 200


# GET /books/<int:book_id> - Retrieve a single book by ID
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        raise NotFound(f"Book with ID {book_id} not found.")
    return jsonify(book), 200


# POST /books - Add a new book (with validation)
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")
        
    # Check for required fields
    required_fields = ['title', 'author', 'published_year']
    for field in required_fields:
        if field not in data:
            raise BadRequest(f"Field '{field}' is required.")
            
    title = data['title']
    author = data['author']
    published_year = data['published_year']
    genre = data.get('genre', 'Unknown') # Optional field, defaults to 'Unknown'
    
    # DataType and content validation
    if not isinstance(title, str) or not title.strip():
        raise BadRequest("Field 'title' must be a non-empty string.")
    if not isinstance(author, str) or not author.strip():
        raise BadRequest("Field 'author' must be a non-empty string.")
    if not isinstance(published_year, int) or published_year < 0:
        raise BadRequest("Field 'published_year' must be a positive integer.")
    if not isinstance(genre, str):
        raise BadRequest("Field 'genre' must be a string.")
        
    # Generate new ID
    new_id = max(b['id'] for b in books) + 1 if books else 1
    
    new_book = {
        "id": new_id,
        "title": title.strip(),
        "author": author.strip(),
        "published_year": published_year,
        "genre": genre.strip()
    }
    books.append(new_book)
    return jsonify(new_book), 201


# PUT /books/<int:book_id> - Update an existing book (with validation)
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        raise NotFound(f"Book with ID {book_id} not found.")
        
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON format or missing Request Body.")
        
    # Verify that at least one field is provided for updating
    modifiable_fields = ['title', 'author', 'published_year', 'genre']
    if not any(field in data for field in modifiable_fields):
        raise BadRequest("At least one field ('title', 'author', 'published_year', 'genre') must be provided to update.")
        
    # Validate and update title if provided
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str) or not title.strip():
            raise BadRequest("Field 'title' must be a non-empty string.")
        book['title'] = title.strip()
        
    # Validate and update author if provided
    if 'author' in data:
        author = data['author']
        if not isinstance(author, str) or not author.strip():
            raise BadRequest("Field 'author' must be a non-empty string.")
        book['author'] = author.strip()
        
    # Validate and update published_year if provided
    if 'published_year' in data:
        published_year = data['published_year']
        if not isinstance(published_year, int) or published_year < 0:
            raise BadRequest("Field 'published_year' must be a positive integer.")
        book['published_year'] = published_year
        
    # Validate and update genre if provided
    if 'genre' in data:
        genre = data['genre']
        if not isinstance(genre, str):
            raise BadRequest("Field 'genre' must be a string.")
        book['genre'] = genre.strip()
        
    return jsonify(book), 200


# DELETE /books/<int:book_id> - Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if book is None:
        raise NotFound(f"Book with ID {book_id} not found.")
        
    books = [b for b in books if b['id'] != book_id]
    return jsonify({"message": "Book deleted successfully", "id": book_id}), 200


if __name__ == '__main__':
    # Running on port 5001 to avoid conflicts with port 5000
    app.run(debug=True, port=5001)
