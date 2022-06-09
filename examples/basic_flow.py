"""Basic example of what a developper would do to start a flow."""

from multiauth import MultiAuth, User

schemas = {
    'manual_headers': {
        'tech': 'manual',
    },
}
users = {
    'user_lambda': User({
        'auth_schema': 'manual_headers',
        'headers': {
            'Authorization': 'Bearer 12345',
        }
    }),
}

instance = MultiAuth(schemas, users)

instance.authenticate_users()

assert instance.headers['user_lambda']['Authorization'] == 'Bearer 12345'
