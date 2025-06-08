import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
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
