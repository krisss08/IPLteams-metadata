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
    team_id: Optional[str] = None
    team_name: str
    city: str
    owner: str
    coach: str
    captain: str
    established_year: int

class TeamExistsResponse(BaseModel):
    team_id: str
    message: str

@app.post("/teams/", response_model=Union[TeamMetaData, TeamExistsResponse])
async def create_team(team_data: TeamMetaData):
    """
    Creates a new team with the provided metadata.

    Args:
        team_data (TeamMetaData): The metadata of the team to be created.

    Returns:
        Union[TeamMetaData, TeamExistsResponse]: Returns the metadata of the newly created team if successful.
        If a team with the same name already exists, returns a `TeamExistsResponse` indicating the existing team's ID.
        If an error occurs during the creation process, returns None.

    Explanation:
        - The function attempts to retrieve the team ID associated with the provided team name from the Redis hash 'team_names'.
        - If an existing team ID is found, indicating that a team with the same name already exists, a `TeamExistsResponse` 
        is returned with the existing team ID and a message indicating that the team already exists.
        - If no existing team ID is found, a new UUID is generated as the team ID.
        - The metadata provided in `team_data` is converted to a dictionary using `team_data.model_dump()` and then augmented
        with the newly generated team ID.
        - The team metadata dictionary is stored in Redis using the newly generated team ID as the key.
        - The team name and its associated team ID are stored in the 'team_names' Redis hash.
        - Finally, the function returns the team metadata dictionary if successful.
    """

    existing_team_id = r.hget("team_names", team_data.team_name)
    if existing_team_id:
        return TeamExistsResponse(team_id=existing_team_id, message="Team already exists")
    
    team_id = str(uuid.uuid4())
    team_data_dict = team_data.model_dump()
    team_data_dict["team_id"] = team_id
    
    r.hmset(team_id, team_data_dict)
    r.hset("team_names", team_data.team_name, team_id)
    
    return team_data_dict

@app.get("/teams/{team_id}", response_model=TeamMetaData)
async def read_team(team_id: str):
    """
    Retrieves the metadata of a team with the specified team ID.

    Args:
        team_id (str): The unique identifier of the team.

    Returns:
        TeamMetaData: The metadata of the team.

    Raises:
        HTTPException: If the team with the specified team ID is not found, raises a 404 error.

    Explanation:
        - Retrieves the metadata of the team associated with the provided team ID from Redis using 'hgetall'.
        - If no team metadata is found for the given team ID, raises a 404 error indicating that the team was not found.
        - Returns the metadata of the team as a 'TeamMetaData' object.
    """
    team_data = r.hgetall(team_id)
    if not team_data:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamMetaData(**team_data)

@app.put("/teams/{team_id}", response_model=TeamMetaData)
async def update_team(team_id: str, team_data: TeamMetaData):
    """
    Updates the metadata of a team with the specified team ID.

    Args:
        team_id (str): The unique identifier of the team.
        team_data (TeamMetaData): The updated metadata of the team.

    Returns:
        TeamMetaData: The updated metadata of the team.

    Raises:
        HTTPException: If the team with the specified team ID is not found, raises a 404 error.

    Explanation:
        - Checks if the team with the provided team ID exists in Redis using 'exists'.
        - If the team does not exist, raises a 404 error indicating that the team was not found.
        - Assigns the provided team ID to the 'team_data' object.
        - Converts the 'team_data' object to a dictionary using 'dict' and stores it in Redis using 'hmset'.
        - Returns the updated metadata of the team as a 'TeamMetaData' object.
    """

    if not r.exists(team_id):
        raise HTTPException(status_code=404, detail="Team not found")
    team_data.team_id = team_id
    r.hmset(team_id, team_data.dict())
    return team_data

@app.delete("/teams/{team_id}")
async def delete_team(team_id: str):
    """
    Deletes the metadata of a team with the specified team ID.

    Args:
        team_id (str): The unique identifier of the team.

    Returns:
        dict: A message indicating that the team was deleted successfully.

    Raises:
        HTTPException: If the team with the specified team ID is not found, raises a 404 error.

    Explanation:
        - Retrieves the metadata of the team associated with the provided team ID from Redis using 'hgetall'.
        - If no team metadata is found for the given team ID, raises a 404 error indicating that the team was not found.
        - Deletes the team metadata from Redis using 'delete'.
        - Removes the team name and its associated team ID from the 'team_names' Redis hash using 'hdel'.
        - Returns a message indicating that the team was deleted successfully.
    """
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

    """
    Lists the metadata of all teams.

    Returns:
        List[TeamMetaData]: A list containing the metadata of all teams.

    Explanation:
        - Initializes an empty list to store the metadata of all teams.
        - Iterates over all keys in Redis using 'scan_iter'.
        - For each key that is not 'team_names', retrieves the metadata of the team associated with the key from Redis using 'hgetall'.
        - Converts the retrieved metadata to a 'TeamMetaData' object and appends it to the list.
        - Returns the list containing the metadata of all teams.
    """
    teams = []
    for key in r.scan_iter(match="*"):
        if key != "team_names":  
            team_data = r.hgetall(key)
            teams.append(TeamMetaData(**team_data))
    return teams

@app.get("/team_names/", response_model=List[dict])
async def list_team_names():
    """
    Lists the names and IDs of all teams.

    Returns:
        List[dict]: A list containing dictionaries with 'team_name' and 'team_id' keys.

    Explanation:
        - Initializes an empty list to store the names and IDs of all teams.
        - Iterates over all items in the 'team_names' Redis hash using 'hscan_iter'.
        - Appends dictionaries containing 'team_name' and 'team_id' keys to the list.
        - Returns the list containing the names and IDs of all teams.
    """
    team_names = []
    for team_name, team_id in r.hscan_iter("team_names"):
        team_names.append({"team_name": team_name, "team_id": team_id})
    return team_names
