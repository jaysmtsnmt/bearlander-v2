from app.common.paths import *
from app.query.query import *

def get_admin_login():
    results = query(
        table = Tables.ADMIN,
        operation = Query.SELECT,
    )

    return (results[0].get("email"), results[0].get("password"))