"""Manual flow example."""
import os

from multiauth import MultiAuth

FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
FIREBASE_USER_EMAIL = os.getenv('FIREBASE_USER_EMAIL')
FIREBASE_USER_PASSWORD = os.getenv('FIREBASE_USER_PASSWORD')

schemas = {
    'firebase-email': {
        'tech': 'rest',
        'url': f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}',
        'method': 'POST',
        'options': {
            'refresh_url': f'https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}',
            'refresh_token_name': 'idToken',
            'token_name': 'idToken',
        },
    },
    'firebase-anonymous': {
        'tech': 'rest',
        'url': f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}',
        'method': 'POST',
        'options': {
            'refresh_url': f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}',
            'refresh_token_name': 'idToken',
            'token_name': 'idToken',
        },
    },
}
users = {
    'email_provider': {
        'auth': 'firebase-email',
        'returnSecureToken': 'true',
        'email': FIREBASE_USER_EMAIL,
        'password': FIREBASE_USER_PASSWORD,
    },
    'anonymous_provider': {
        'auth': 'firebase-anonymous',
        'returnSecureToken': 'true',
    },
}

instance = MultiAuth(schemas, users)
instance.authenticate_users()
