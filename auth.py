from dotenv import load_dotenv
from fastapi import Header,HTTPException,Depends
from jose import jwt, JWTError
from datetime import datetime,timedelta,timezone
import os
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["bcrypt"],deprecated = "auto")

def hash_password(password):
  return pwd_context.hash(password)
  
def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password
  )

load_dotenv()
SECRET_API_KEY = os.getenv("SECRET_API_KEY")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_current_user(token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(
    status_code = 401,
    detail = "Could not validate credentials"
  )
  try:
    payload = jwt.decode(token,SECRET_KEY,algorithms = [ALGORITHM])
    username = payload.get("sub")
    if username is None:
      raise credentials_exception  
  except JWTError:
    raise credentials_exception
  return username



def verify_api_key(api_key: str=Header()):
  if api_key != SECRET_API_KEY:
    raise HTTPException(status_code = 401,detail = "Invalid API Key")
  print (api_key)
  return api_key


def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + timedelta(minutes= 30)
  to_encode.update({"exp" : expire})
  encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
  return encoded_jwt