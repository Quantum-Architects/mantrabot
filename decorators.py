import users

def verify_address_exists(func):
    def wrapper():
        func()

    return wrapper
