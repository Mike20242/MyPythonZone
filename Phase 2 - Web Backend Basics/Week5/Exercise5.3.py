from flask import Flask, request, render_template
app = Flask(__name__)
# Route to display the form
@app.route('/', methods=['GET'])
def display_form():
   return render_template('form.html')
# Route to process form data
@app.route('/process', methods=['POST'])
def process_form():
   name = request.form['name']
   email = request.form['email']
   return f"Name: {name}, Email: {email}"
if __name__ == '__main__':
   app.run(debug=True)