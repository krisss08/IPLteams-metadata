from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse 
from typing import List, Optional, Union
from pydantic import BaseModel, Field
import redis
import json
import uuid 

class PlayersMetaData(BaseModel):

    player_id: Optional[str] = Field(
        None,
        description="This field is a the unique identifier for the model artifact.",
    )
    team_id: str = Field(
        ..., 
        description="This contains the unique ID for the team"
    )
    player_name: str = Field(
        ..., 
        description = "This contains the name of the players"
    )
    player_cost: int = Field(
        ...,
        description = "This contains the cost of the players in the IPL auction"
    )
    

class TeamMetaData(BaseModel):

    team_id: Optional[str] = Field(
        None, 
        description="This contains the unique ID for the team"
    )
    team_name: str = Field(
        None, 
        description="This contains the unique ID for the team"
    )
    city: str = Field(
        ..., 
        description="This contains the city of the IPL Team"
    )
    owner: Optional[str] = Field(
        None, 
        description="This contains the owner details of the IPL team"
    )
    coach: Optional[str] = Field(
        None, 
        description="This contains the coach details of the IPL team"
    )
    captain: str = Field(
        ..., 
        description="This contains the captain's details of the IPL team"
    )
    established_year: Optional[int] = Field(
        None,
        description= "This contains the IPL's team establishment year"
    )
    year_won: Optional[List[int]] = Field(
        list(),
        description= "This contains the list of years in which the IPL team won"
    )
    
class PlayersTeamResponse(BaseModel):

    player_id: str
    team_id: str
    player_name: str
    player_cost: int 

class TeamMetaDataResponse(BaseModel):

    team_id: str
    team_name: str
    city: str
    owner: Optional[str]
    coach: Optional[str]
    captain: str 
    established_year: Optional[int]
    year_won: Optional[List[int]]



    









