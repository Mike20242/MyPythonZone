from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Home Page</h1><p>Welcome to our website!</p>"

@app.route('/about')
def about():
    return "<h1>About Us</h1><p>This is the about page.</p>"

@app.route('/contact')
def contact():
    return "<h1>Contact Us</h1><p>You can reach us at contact@example.com.</p>"

if __name__ == '__main__':
    app.run(debug=True)
