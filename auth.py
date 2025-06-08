import firebase_admin
from firebase_admin import credentials, auth

# Correct path to your firebase key
cred = credentials.Certificate("ai-document-summerize-firebase-adminsdk-fbsvc-4db17133d2.json")
firebase_admin.initialize_app(cred)

# Function to register user
def register_user(email, password, username):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        return user.uid
    except Exception as e:
        print('Error registering user:', e)
        return None
