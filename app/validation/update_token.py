from app.models import UserModel
from app.validation.create_token import AcessTokenCreate, RefreshTokenCreate
from app.validation.validate_token import RefreshTokenValidate


class AccessTokenUpdate:
    def __init__(self, creater : AcessTokenCreate):
        self.creater = creater
        

    async def new_access_token(self, user : UserModel ):
        data = {
        "sub" : user.email,
        "role" : user.role,
        "id" : user.id
        }
        return self.creater.create_acess_token(data)
    
class RefreshTokenUpdate:
    def __init__(self, creater : RefreshTokenCreate):
        self.creater = creater
        

    async def new_refresh_token(self, user : UserModel):
        data = {
        "sub" : user.email,
        "role" : user.role,
        "id" : user.id
        }
        return self.creater.create_refresh_token(data)






    
     