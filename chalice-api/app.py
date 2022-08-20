from chalice import Chalice, Response
import boto3
from boto3.dynamodb.conditions import Key

app = Chalice(app_name='chalice-api')


def get_app_db():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table('my-demo-table')
    return table


@app.route('/book', methods=['POST'])
def add_book():
    data = app.current_request.json_body
    try:
        get_app_db().put_item(Item={
            'id': data['id'],
            "title": data['title'],
            "author": data['author']
        })
        return {'message': 'ok - CREATED', 'status': 201, "id": data['id'], "title": data['title'], "author": data['author']}
    except Exception as e:
        return {'message': error_msg_formatter(e, '010')}


@app.route('/', methods=['GET'])
def index():
    response = get_app_db().scan()
    data = response.get('Items', None)
    return {'data': data}


@app.route('/book/{id}', methods=['GET'])
def get_book(id):
    response = get_app_db().query(
        KeyConditionExpression=Key("id").eq(id)
    )
    data = response.get('Items', None)
    return {'data': data}


@app.route('/book/{id}', methods=['PUT'])
def update_book(id):
    data = app.current_request.json_body
    try:
        get_app_db().update_item(Key={
            "id": data['id'],
            "author": data['author']
        },
            UpdateExpression="set title=:r",
            ExpressionAttributeValues={
            ':r': data['title']
        },
            ReturnValues="UPDATED_NEW"
        )
        return {'message': 'ok - UPDATED', 'status': 201}
    except Exception as e:
        return {'message': error_msg_formatter(e, '020')}


@app.route('/book/{id}', methods=['DELETE'])
def delete_book(id):
    data = app.current_request.json_body
    try:
        response = get_app_db().delete_item(
            Key={
                "id": data['id'],
                "author": data['author']
            }
        )
        return {'message': 'ok - DELETED', 'status': 201}

    except Exception as e:
        return {'message': error_msg_formatter(e, '030')}


def error_msg_formatter(e, error_code):
    return 'ERROR: '+str(e)+ ' ['+error_code+']'
