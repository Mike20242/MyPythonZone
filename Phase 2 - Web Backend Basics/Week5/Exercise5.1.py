from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Welcome to the Flask Sample App!</h1><p>This is the home page.</p>"

@app.route('/about')
def about():
    return "<h2>About Us</h2><p>This is a simple Flask application with 5 routes.</p>"

@app.route('/contact')
def contact():
    return "<h2>Contact</h2><p>Email us at: contact@example.com</p>"

@app.route('/api/info')
def api_info():
    # Returning JSON data
    return jsonify({
        "status": "success",
        "message": "Flask API is running",
        "version": "1.0"
    })

@app.route('/greet/<name>')
def greet(name):
    # Dynamic route accepting a parameter
    return f"<h2>Hello, {name.capitalize()}!</h2><p>Welcome to your personalized page.</p>"

if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, port=5000)
