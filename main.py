from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import redis
import json
import uuid

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


class TeamMetaData(BaseModel):
    team_id: str
    team_name: str
    city: str
    owner: Optional[str]
    coach: Optional[str]
    captain: str
    home_ground: str
    established_year: Optional[int]
    squad_size: int
    overseas_players: Optional[List[str]]
    social_media_handles: Optional[dict]
    team_id: int

@app.get("/")
async def hello(): 
    return {"message": "CRUDL operations for IPL teams meta data"}

@app.post("/teams/", response_model=TeamMetaData)
async def create_team(team_data: TeamMetaData):
    team_data.team_id = str(uuid.uuid4())
    redis = await get_redis()
    await redis.hmset_dict(team_data.team_id, team_data.dict())
    redis.close()
    await redis.wait_closed()
    return team_data