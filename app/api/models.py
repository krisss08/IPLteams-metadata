from app.model.schemas import TeamMetaData, TeamMetaDataResponse 
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Union
import redis 
import uuid
import json 
 
router = APIRouter()
r = redis.Redis(host= "localhost", port = 6379, decode_responses= True)
r.flushall()

class ObjectExistsResponse(BaseModel):
    id: str
    message: str 

@router.post("/teams/", response_model=Union[TeamMetaDataResponse, ObjectExistsResponse])
async def create_team(team_data: TeamMetaData):

    existing_team_id = r.hget("team_names", team_data.team_name)
    if existing_team_id: 

        return ObjectExistsResponse(id = existing_team_id, message= "Team already exists")
    
    team_id = str(uuid.uuid4())

    team_data_dict = team_data.model_dump()
    team_data_dict["team_id"] = team_id

    if team_data.year_won: 
        team_data_dict["year_won"] = json.dumps(team_data.year_won)

    r.hset("team_names", team_data.team_name, team_id)
    
    return JSONResponse(content=team_data_dict, status_code=200)

@router.get("/teams/{team_id}", response_model= TeamMetaDataResponse)
async def get_team(team_id: str):

    team_data = r.hgetall(team_id)
    if not team_data:

        raise HTTPException(status_code=404, detail = "Team Not Found")
    
    return JSONResponse(status_code=200,content= TeamMetaDataResponse(**team_data))

@router.patch("/teams/update/{team_id}")
async def update_team(team_id: str, team_data: TeamMetaData):

    existing_team_data = r.hgetall(team_id)
    if not existing_team_data:

        raise HTTPException(status_code=400, detail = "No Team Exists")
    
    existing_team_data = {key.decode('utf-8'): value.decode('utf-8') for key, value in existing_team_data.items()}

    for field, value in team_data.model_dump().items():
        if value is not None:
            existing_team_data[field] = value

    if existing_team_data.get('year_won'):
        existing_team_data['year_won'] = json.dumps(existing_team_data['year_won'])

    r.hmset(team_id, existing_team_data)

    return JSONResponse(status_code=200, content=existing_team_data)

@router.delete("/teams/delete/{team_id}")
async def delete_team(team_id: str):

    team_data = r.hgetall(team_id)
    if not team_data:
        raise HTTPException(status_code=404, detail="Team not found")
    
    r.delete(team_id) 
    for team_name, stored_team_id in r.hscan_iter("team_names"):
        if stored_team_id == team_id:
            r.hdel("team_names", team_name)
            break
    return JSONResponse(status_code=200, content="Team deleted successfully")

@router.get("/teams/}")
def list_teams():

    teams = []
    for key in r.scan_iter('*'):
        if key!= "team_names":

            team_data = r.hgetall(key)
            teams.append(TeamMetaDataResponse(**team_data))
    return JSONResponse(status_code=200, content = teams)

@router.get("/teams/list/", response_model= List[dict])
def list_team_names():

    team_names = []
    for team_name, team_id in r.hscan_iter("team_names"):
        team_names.append({"team_name": team_name, "team_id": team_id})
    return JSONResponse(status_code= 200, content = team_names)














    

    
