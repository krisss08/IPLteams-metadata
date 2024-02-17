from fastapi import FastAPI, HTTPException
from typing import List, Optional, Union
from pydantic import BaseModel
import redis
import json
import uuid

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.flushall()

class TeamMetaData(BaseModel):
    team_name: str
    city: str
    owner: str
    coach: str
    captain: str

class TeamExistsResponse(BaseModel):
    team_id: str
    message: str


@app.post("/teams/", response_model=Union[TeamMetaData, TeamExistsResponse])
async def create_team(team_data: TeamMetaData):
    existing_team_id = r.hget("team_names", team_data.team_name)
    if existing_team_id:
        return TeamExistsResponse(team_id=existing_team_id, message="Team already exists")
    
    team_id = str(uuid.uuid4())
    team_data_dict = team_data.model_dump()
    team_data_dict["team_id"] = team_id
    
    r.hmset(team_id, team_data_dict)
    r.hset("team_names", team_data.team_name, team_id)
    
    return team_data

@app.get("/teams/{team_id}", response_model=TeamMetaData)
async def read_team(team_id: str):
    team_data = r.hgetall(team_id)
    if not team_data:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamMetaData(**team_data)

@app.put("/teams/{team_id}", response_model=TeamMetaData)
async def update_team(team_id: str, team_data: TeamMetaData):
    if not r.exists(team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    team_data.team_id = team_id
    r.hmset(team_id, team_data.dict())
    return team_data

@app.delete("/teams/{team_id}")
async def delete_team(team_id: str):
    team_data = r.hgetall(team_id)
    if not team_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    r.delete(team_id) 
    for team_name, stored_team_id in r.hscan_iter("team_names"):
        if stored_team_id == team_id:
            r.hdel("team_names", team_name)
            break
    
    return {"message": "Team deleted successfully"}

@app.get("/teams/", response_model=List[TeamMetaData])
async def list_teams():
    teams = []
    for key in r.scan_iter(match="*"):
        if key != "team_names":  
            team_data = r.hgetall(key)
            teams.append(TeamMetaData(**team_data))
    return teams

@app.get("/team_names/", response_model=List[dict])
async def list_team_names():
    team_names = []
    for team_name, team_id in r.hscan_iter("team_names"):
        team_names.append({"team_name": team_name, "team_id": team_id})
    return team_names
