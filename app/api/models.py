from models.schemas import TeamMetaData, TeamMetaDataResponse 
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Union
import redis 
import uuid
import json 
    
router = APIRouter()
r = redis.Redis(host= "localhost", port = 6379, decode_responses= True)

class ObjectExistsResponse(BaseModel):
    id: str
    message: str 

@router.post("/teams/", response_model=Union[TeamMetaDataResponse, Object])
def create_team(team_data: TeamMetaData):

    existing_team_id = r.hget("team_names", team_data.team_name)
    if existing_team_id: 

        return ObjectExistsResponse(id = existing_team_id, message= "Team already exists")
    
    team_id = str(uuid.uuid4())

    if team_data.year_won: 
        team_data_dict.year_won = json.dumps(team_data.year_won)

    team_data_dict = team_data.model_dump()
    team_data_dict['team_id'] = team_id
    
    r.hset("team_names", team_data.team_name, team_id)
    
    return JSONResponse(content=team_data, status_code=200)
        'message': 'Team ID created successfully', 
            'data': team_data_dict
    }




    

    
