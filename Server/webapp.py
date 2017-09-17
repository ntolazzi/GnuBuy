import json
from flask import Flask, jsonify, make_response, request, abort

app = Flask(__name__)

shopping_list = []
list_locked = False

try:
    with open('shoppinglist.json', 'r') as json_file:
        shopping_list = json.load(json_file)
except IOError:
    pass

def write_list():
    with open('shoppinglist.json', 'w') as json_file:
        json.dump(shopping_list, json_file)

@app.route('/list/reset', methods=['GET'])
def reset_lock():
    global list_locked
    list_locked = False
    return make_response(jsonify({'Lock': False}), 200)

@app.route('/list', methods=['GET'])
def get_list():
    return jsonify(shopping_list)

@app.route('/list/update', methods=['POST'])
def update_list():
    if list_locked:
        return make_response(jsonify({'error': 'List locked'}), 423)
    else:
        if not request.json:
            abort(400)
        global shopping_list
        shopping_list = request.json
        write_list()
        return jsonify(shopping_list)

@app.route('/list/lock', methods=['POST'])
def lock_list():
    global list_locked
    if not request.json:
        abort(400)
    if 'Lock' not in request.json:
        abort(400)
    lock_request = request.json['Lock']
    if lock_request:
        if list_locked:
            return make_response(jsonify({'error': 'List already locked'}), 423)
        else:
            list_locked = True
            return make_response(jsonify({'Lock': True}), 200)
    else:
        if list_locked:
            list_locked = False
            return make_response(jsonify({'Lock': False}), 200)
        else:
            return make_response(jsonify({'error': 'List already released'}), 423)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
