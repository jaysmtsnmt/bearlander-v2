from app.auth.handler import *
from app.common import administrator as Admin 

email, password = Admin.get_admin_login()

handler = Handler(email, password)
handler.login()

# new = Handler(email, password)
# new.delete_account()
