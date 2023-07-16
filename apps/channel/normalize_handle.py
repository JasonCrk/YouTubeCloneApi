import random

def normalize_handle(username: str):
    return username.title().replace(' ', '') + str(random.randint(111, 999))