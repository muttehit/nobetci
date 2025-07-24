from app.db import tls_db
from app.utils.crypto import generate_certificate


def get_tls_certificate():
    tls = tls_db.get(True)

    if tls is None:
        tls_db.add(generate_certificate())

    return tls_db.get(True)
