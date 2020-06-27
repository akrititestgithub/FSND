import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-exp.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'CapstoneApisId'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    #print("check permission***********1",flush=True)
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'header_missing',
            'description': 'Auth header is missing.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Auth header must start with "Bearer"'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description':'No token found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Auth header must be bearer + token.'
        }, 401)

    token = parts[1]
    return token


def check_permissions(permission, payload):
    # print("check permission***********2",flush=True)
    # print(permission,flush=True)
    # print(payload,flush=True)
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)
    return True


def verify_decode_jwt(token):
    #print("check permission***********3",flush=True)
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Invalid Header'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience '
                               'and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
