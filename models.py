from pydantic import BaseModel



class LoginRequest(BaseModel):
  username : str
  password : str

class Token(BaseModel):
  access_token: str
  token_type: str

class DashboardEntry(BaseModel):
  temperature: float
  ethereum_price : float
  joke: str

class DashboardResponse(BaseModel):
  id : int
  timestamp : str
  temperature : float
  ethereum_price : float
  joke : str

class DashboardStats(BaseModel):
  total_entries : int
  min_temperature : float
  max_temperature : float
  avg_temperature : float





