from fastapi import FastAPI, HTTPException
from typing import List, Dict
import json
#from .models import User, MatchResult
#from .matching.algorithm import calculate_matches, get_compatibility_score

from pydantic import BaseModel


#models.py User and MatchResult classes copied in main due to import error "attempted relative import with no known parent package"

class User(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    interested_in: str
    location: str
    hobbies: List[str]
    interests: List[str]
    occupation: str
    education_level: str
    personality_traits: List[str]

class MatchResult(BaseModel):
    user_id: str
    name: str
    compatibility_score: float
    common_interests: List[str]
    common_hobbies: List[str]
    
    
    #algorithm.py calculate_matches() and get_compatibility_score() functions copied in main due to import error "attempted relative import with no known parent package"


#  Calculate and return matches for a given user.
def calculate_matches(user: Dict, all_users: List[Dict]) -> List[MatchResult]: # Returns: - List of MatchResult objects sorted by compatibility score in descending order
    match_results = []

    for other_user in all_users:
        if other_user["id"] == user["id"]:  # Skip self comparison
            continue
        
        score = get_compatibility_score(user, other_user)
        common_hobbies = list(set(user["hobbies"]).intersection(other_user["hobbies"]))
        common_interests = list(set(user["interests"]).intersection(other_user["interests"]))

        match_results.append(MatchResult(
            user_id=other_user["id"],
            name=other_user["name"],
            compatibility_score=score,
            common_interests=common_interests,
            common_hobbies=common_hobbies
        ))

        # Sort the results by compatibility score in descending order
    return sorted(match_results, key=lambda x: x.compatibility_score, reverse=True)
    
    
      # Calculate compatibility score between two users.
def get_compatibility_score(user1: Dict, user2: Dict) -> float: #Returns:- Float representing compatibility score (0-1)

    score = 0.0
    common_hobbies=set(user1["hobbies"]).intersection(user2["hobbies"])
    common_interests = set(user1["interests"]).intersection(user2["interests"])

    # Age compatibility: score based on age difference
    age_diff = abs(user1["age"] - user2["age"])
    age_score = max(0, 1 - age_diff / 20)  # Normalize the score, assuming a max difference of 20  years
    score += 0.2 * age_score

    # Gender compatibility: check if both are interested in each other
    gender_score = 1.0 if user1["interested_in"] == user2["gender"] and user2["interested_in"] == user1["gender"] else 0.0
    score += 0.2 * gender_score

    # Location compatibility: 1 if same location
    location_score = 1.0 if user1["location"] == user2["location"] else 0.0
    score += 0.2 * location_score

    # Common hobbies and interests
    hobbies_score = len(common_hobbies) / max(len(user1["hobbies"]), len(user2["hobbies"])) if user1["hobbies"] and user2["hobbies"] else 0.0
    score += 0.2 * hobbies_score

    interests_score = len(common_interests) / max(len(user1["interests"]), len(user2["interests"])) if user1["interests"] and user2["interests"] else 0.0
    score += 0.2 * interests_score

    return score
    
    
app = FastAPI(title="Dating App Matchmaking API")

with open("../mock_data/users.json", "r") as f:
    USER_DATA = json.load(f)["users"]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Dating App Matchmaking API"}

@app.post("/api/v1/match/{user_id}")
async def generate_matches(user_id: str) -> List[MatchResult]:
    """
    Generate matches for a given user.
    Returns a list of potential matches sorted by compatibility score.
    """

    user = next((u for u in USER_DATA if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    matches = calculate_matches(user, USER_DATA)
    return matches

@app.get("/api/v1/compatibility/{user_id1}/{user_id2}")
async def get_compatibility(user_id1: str, user_id2: str) -> Dict:
    """
    Calculate compatibility score between two specific users
    """
    user1 = next((u for u in USER_DATA if u["id"] == user_id1), None)
    user2 = next((u for u in USER_DATA if u["id"] == user_id2), None)
    
    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="One or both users not found")
    
    score = get_compatibility_score(user1, user2)
    
    return {
        "user1_id": user_id1,
        "user2_id": user_id2,
        "compatibility_score": score
    }
