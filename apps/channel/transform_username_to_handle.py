import random

def username_to_handle(username: str):
    return username.title().replace(' ', '') + str(random.randint(111, 999))