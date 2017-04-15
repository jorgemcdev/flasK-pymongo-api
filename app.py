import os
from flask import Flask, jsonify, request, abort, make_response, render_template
from flask_pymongo import PyMongo, ObjectId # flask.ext.pymongo deprecated

app = Flask(__name__)

# Load Config File for DB
app.config.from_pyfile('config.cfg')
mongo = PyMongo(app)

# App Root
APP_ROOT = os.path.dirname(os.path.abspath(__file__));

# Allowed files
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route('/')
def home():
    return 'Home route!'

@app.route('/fixtures', methods=['GET'])
def add():
    user = mongo.db.users
    user.insert({'name': 'Anthony', 'language' : 'ruby'})
    user.insert({'name': 'Kelly', 'language' : 'C'})
    user.insert({'name': 'John', 'language' : 'Java'})
    user.insert({'name': 'Cedric', 'language' : 'Javascript'})
    return jsonify({'message':'users added'})

# Route to Uploade Page
@app.route("/upload-page")
def main():
    return render_template('upload-file.html')

def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload File
@app.route('/upload', methods=['POST'])
def upload():
    result = {'errors': [] }

    # Set the target Folder
    target = os.path.join(APP_ROOT, 'images/')

    # Get sure the folder exists
    if not os.path.isdir(target):
        os.mkdir(target)

    # Loop file to get the images names
    for file in request.files.getlist("file"):
        filename = file.filename
        destination = "/".join([target, filename])
        if file and allowed_file(file.filename):
            file.save(destination)
        else:
            if not file.filename:
                file.filename = "empty"
            result["errors"].append({file.filename:'not allowed'})

    return jsonify(result)

# List All Users
@app.route('/users', methods=['GET'])
def get_all_users():
    user = mongo.db.users

    output = []
    for q in user.find():
        output.append({'_id': str(q['_id']), 'name': q['name'], 'language': q['language']})

    return jsonify({'users' : output})

# List user by name
@app.route('/users/<user_id>', methods=['GET'])
def get_one_user(user_id):
    user = mongo.db.users
    q = user.find_one({'_id': ObjectId(user_id)})
    if q:
        output = {'user': {'_id': str(q['_id']), 'name': q['name'], 'language': q['language']}}
    else:
        output = {'error' : 'user not found'}
    return jsonify(output)

# Post user
@app.route('/users', methods=['POST'])
def post_user():
    user = mongo.db.users

    name = request.form['name']
    language = request.form['language']

    inserted_id = user.insert({'name': name, 'language': language})
    new_user = user.find_one({'_id' : inserted_id})

    output = {'_id': str(q['_id']),'name': new_user['name'], 'language': new_user['language']}

    return jsonify({'user' : output})

# Update a user
@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = mongo.db.users
    q = user.find_one({'_id': ObjectId(user_id)})
    if q:
        if request.form['name']:
            q['name'] = request.form['name']
        if request.form['language']:
            q['language'] = request.form['language']

        user.save(q);
        output = {'message' : 'user updated'}
    else:
        output = {'error' : 'user not found'}
    return jsonify(output)

# Delete a user
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = mongo.db.users
    q = user.find_one({'_id': ObjectId(user_id)})
    if q:
        id = q["_id"]
        user.remove(id)
        output = {'message' : 'user deleted'}
    else:
        output = {'error' : 'user not found'}

    return jsonify(output)

# Error Handler 404
@app.errorhandler(404)
def not_found(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'Not found'}), 404)

# Error Handler 405
@app.errorhandler(405)
def not_found(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'Method is not allowed'}), 405)

# Error Handler 500
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'Internal Error'}), 500)

# Exception
@app.errorhandler(Exception)
def unhandled_exception(error):
    app.logger.error('Unhandled Exception: %s', (error))
    return make_response(jsonify({'error': 'Unhandled Exception'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
