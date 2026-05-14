from flask import Flask, jsonify
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)

class Hello(Resource):
    def get(self):
        return jsonify({'data': 'Hello World!'})

class Disp(Resource):
    def get(self, num):
        return jsonify({'data': num ** 2})


api.add_resource(Hello, '/')
api.add_resource(Disp, '/disp/<int:num>')

if __name__ == '__main__':
    app.run(debug=True)