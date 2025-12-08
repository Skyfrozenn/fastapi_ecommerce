import jwt


from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta,timezone
 



oath2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")
 




 
class AcessTokenCreate:
    def __init__(self, algorithm, secret_key, acces_token_expire_minutes) :
        self.algorithm = algorithm
        self.__secret_key = secret_key
        self.acces_token_expire_minutes = acces_token_expire_minutes 
     
    def create_acess_token(self, data : dict):
        to_encody = data.copy() #копируем словарь с данными чтобы не испортить оригинал
        exprire = datetime.now(timezone.utc) + timedelta(minutes=self.acces_token_expire_minutes) #текущее время + 30 минут
        to_encody.update(
            {
            "exp" : exprire,
            "token_types" : "acess"
        }
        )
        return jwt.encode(to_encody, self.__secret_key, algorithm = self.algorithm)
    
     
    
    


class RefreshTokenCreate:
    def __init__(self,algorithm, secret_key, refresh_token_expire_days ):
        self.algorithm = algorithm
        self.__secret_key = secret_key
        self.refresh_token_expire_days = refresh_token_expire_days


    def create_refresh_token(self, data : dict):
        to_encody = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days = self.refresh_token_expire_days)
        to_encody.update(
            {
            "exp" : expire,
            "token_types" : "refresh"
            }
        )
         
        refresh_token = jwt.encode(to_encody, self.__secret_key, algorithm = self.algorithm)
        return refresh_token
    
    


 



 
