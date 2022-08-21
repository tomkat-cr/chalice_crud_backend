
from urllib.request import urlopen
from chalice import Chalice, Response
import boto3
from boto3.dynamodb.conditions import Key

from functools import wraps
import json
import jwt
from os import environ as env
from dotenv import find_dotenv, load_dotenv


app = Chalice(app_name='chalice-api')
app.secret_key = env.get("APP_SECRET_KEY")


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


# ---------- General use functions ----------


def error_msg_formatter(e, error_code):
    return 'ERROR: '+str(e)+ ' ['+error_code+']'


# https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
def jsonify(*args, **kwargs):
    return app.response_class(json.dumps(dict(*args, **kwargs),
        indent=None if app.current_request.is_xhr else 2), mimetype='application/json')


# ---------- OAUTH0 for the API ----------


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    request = app.current_request
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if env.get("AUTH0_ENABLED", "0") == "0":
            return f(*args, **kwargs)
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+env.get("AUTH0_DOMAIN")+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        print('jwks', jwks)
        print('unverified_header', unverified_header)
        rsa_key = {}
        for key in jwks["keys"]:
            # if key["kid"] == unverified_header["kid"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[env.get("ALGORITHMS")],
                    audience=env.get("API_AUDIENCE"),
                    issuer="https://"+env.get("AUTH0_DOMAIN")+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            # except jwt.JWTClaimsError:
            # AttributeError: module 'jwt' has no attribute 'JWTClaimsError'
            # https://githubmemory.com/repo/mpdavis/python-jose/issues/197
            #
            # except jwt.MissingRequiredClaimError :
            # https://pyjwt.readthedocs.io/en/stable/api.html?highlight=MissingRequiredClaimError#jwt.exceptions.MissingRequiredClaimError
            except jwt.MissingRequiredClaimError :
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                 "incorrect claims,"
                                 "please check the audience and issuer"}, 401)
            except Exception as e:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                 "Unable to parse authentication"
                                 " token: " + str(e)}, 401)

            app.current_request.context.update(payload)
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return decorated


# ---------- Chalice app ----------


def get_app_db():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table('my-demo-table')
    return table


@app.route('/book', methods=['POST'])
@requires_auth
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
@requires_auth
def index():
    response = get_app_db().scan()
    data = response.get('Items', None)
    return {'data': data}


@app.route('/book/{id}', methods=['GET'])
@requires_auth
def get_book(id):
    response = get_app_db().query(
        KeyConditionExpression=Key("id").eq(id)
    )
    data = response.get('Items', None)
    return {'data': data}


@app.route('/book/{id}', methods=['PUT'])
@requires_auth
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
@requires_auth
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
