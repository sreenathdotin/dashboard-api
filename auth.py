from dotenv import load_dotenv
from fastapi import Header,HTTPException

import os

load_dotenv()

SECRET_API_KEY = os.getenv("SECRET_API_KEY")



def verify_api_key(api_key: str=Header()):
  if api_key != SECRET_API_KEY:
    raise HTTPException(
      status_code = 401,
      detail = "Invalid API Key"
    )
  print (api_key)
  return api_key