# Authentication functions
valid_Db = {
    "web": "1234",
}

def authenticate_user(username, password):
    return valid_Db.get(username) == password