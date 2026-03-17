import pickle
import os

token_path = 'c:/Users/Yuto/Desktop/app/python_scripts/token.pickle'
if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
        print(f"Scopes: {creds.scopes}")
        print(f"Valid: {creds.valid}")
        print(f"Expired: {creds.expired}")
else:
    print("No token found.")
