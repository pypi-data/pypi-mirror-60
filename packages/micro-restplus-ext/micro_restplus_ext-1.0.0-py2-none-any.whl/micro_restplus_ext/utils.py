import random
import uuid


def uuid_random():
    _random = random.Random()
    return uuid.UUID(int=_random.getrandbits(128)).__str__()
