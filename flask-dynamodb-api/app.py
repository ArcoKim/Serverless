import os

import boto3
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)

dynamodb_client = boto3.resource('dynamodb')

if os.environ.get('IS_OFFLINE'):
    dynamodb_client = boto3.client(
        'dynamodb', region_name='localhost', endpoint_url='http://localhost:8000'
    )

USERS_TABLE = os.environ['USERS_TABLE']
table = dynamodb_client.Table(USERS_TABLE)

@app.route('/users', methods=['POST', 'PUT'])
def create_user():
    user_id = request.json.get('userId')
    name = request.json.get('name')
    if not user_id or not name:
        return jsonify({'error': 'Please provide both "userId" and "name"'}), 400

    table.put_item(
        Item={'userId': user_id, 'name':  name}
    )

    return jsonify({'userId': user_id, 'name': name})

@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    result = table.get_item(
        Key={'userId': user_id}
    )
    item = result.get('Item')
    if not item:
        return jsonify({'error': 'Could not find user with provided "userId"'}), 404

    return jsonify(
        {'userId': item.get('userId'), 'name': item.get('name')}
    )

@app.route('/users/<string:user_id>', methods=['PATCH'])
def update_user(user_id):
    name = request.json.get('name')
    if not name:
        return jsonify({'error': 'Please provide "name"'}), 400
    
    result = table.update_item(
        Key={'userId':  user_id},
        UpdateExpression='SET #attr1 = :val1',
        ExpressionAttributeNames={
            "#attr1": "name"
        },
        ExpressionAttributeValues={
            ':val1': name
        }
    )
    if not result:
        return jsonify({'error': 'User update failed'}), 500

    return jsonify(
        {'userId': user_id, 'name': name}
    )

@app.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = table.delete_item(
        Key={'userId': user_id}
    )
    if not result:
        return jsonify({'error': 'Failed to delete user'}), 500

    return jsonify(
        {'userId': user_id}
    )

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
