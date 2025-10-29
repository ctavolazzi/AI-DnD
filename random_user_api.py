"""
Random User Generator API Client
Integrates with https://randomuser.me/ API for generating realistic character data
"""

import requests
import logging
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RandomUser:
    """Data class for Random User API response"""
    gender: str
    name: Dict[str, str]  # {"title": "Mr", "first": "John", "last": "Doe"}
    location: Dict[str, Union[str, int, Dict]]
    email: str
    phone: str
    cell: str
    picture: Dict[str, str]  # {"large": "url", "medium": "url", "thumbnail": "url"}
    nationality: str
    age: int
    dob: Dict[str, Union[str, int]]

    @property
    def full_name(self) -> str:
        """Get full name as a single string"""
        return f"{self.name['first']} {self.name['last']}"

    @property
    def title_name(self) -> str:
        """Get name with title"""
        return f"{self.name['title']} {self.name['first']} {self.name['last']}"

    @property
    def location_string(self) -> str:
        """Get location as a readable string"""
        loc = self.location
        return f"{loc['city']}, {loc['state']}, {loc['country']}"

    @property
    def profile_picture_url(self) -> str:
        """Get medium-sized profile picture URL"""
        return self.picture.get('medium', self.picture.get('large', ''))

class RandomUserAPI:
    """Client for Random User Generator API"""

    BASE_URL = "https://randomuser.me/api/"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-DnD-Game/1.0'
        })

    def _make_request(self, params: Dict[str, Union[str, int]]) -> Dict:
        """Make API request with error handling"""
        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise APIError(f"Failed to fetch random user data: {e}")
        except ValueError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise APIError(f"Invalid response format: {e}")

    def get_random_user(self,
                       gender: Optional[str] = None,
                       nationality: Optional[Union[str, List[str]]] = None,
                       seed: Optional[str] = None,
                       include_fields: Optional[List[str]] = None,
                       exclude_fields: Optional[List[str]] = None) -> RandomUser:
        """
        Get a single random user

        Args:
            gender: "male", "female", or None for random
            nationality: Country code(s) - "US", "GB", ["US", "GB"], etc.
            seed: Seed for reproducible results
            include_fields: List of fields to include only
            exclude_fields: List of fields to exclude

        Returns:
            RandomUser object with user data
        """
        params = {}

        if gender:
            params['gender'] = gender

        if nationality:
            if isinstance(nationality, list):
                params['nat'] = ','.join(nationality)
            else:
                params['nat'] = nationality

        if seed:
            params['seed'] = seed

        if include_fields:
            params['inc'] = ','.join(include_fields)

        if exclude_fields:
            params['exc'] = ','.join(exclude_fields)

        data = self._make_request(params)

        if 'error' in data:
            raise APIError(f"API returned error: {data['error']}")

        if not data.get('results'):
            raise APIError("No results returned from API")

        user_data = data['results'][0]
        return self._parse_user_data(user_data)

    def get_multiple_users(self,
                          count: int = 5,
                          gender: Optional[str] = None,
                          nationality: Optional[Union[str, List[str]]] = None,
                          seed: Optional[str] = None) -> List[RandomUser]:
        """
        Get multiple random users

        Args:
            count: Number of users to fetch (max 5000)
            gender: "male", "female", or None for random
            nationality: Country code(s)
            seed: Seed for reproducible results

        Returns:
            List of RandomUser objects
        """
        if count > 5000:
            raise ValueError("Maximum 5000 users per request")

        params = {'results': count}

        if gender:
            params['gender'] = gender

        if nationality:
            if isinstance(nationality, list):
                params['nat'] = ','.join(nationality)
            else:
                params['nat'] = nationality

        if seed:
            params['seed'] = seed

        data = self._make_request(params)

        if 'error' in data:
            raise APIError(f"API returned error: {data['error']}")

        if not data.get('results'):
            raise APIError("No results returned from API")

        return [self._parse_user_data(user_data) for user_data in data['results']]

    def _parse_user_data(self, user_data: Dict) -> RandomUser:
        """Parse API response data into RandomUser object"""
        return RandomUser(
            gender=user_data.get('gender', ''),
            name=user_data.get('name', {}),
            location=user_data.get('location', {}),
            email=user_data.get('email', ''),
            phone=user_data.get('phone', ''),
            cell=user_data.get('cell', ''),
            picture=user_data.get('picture', {}),
            nationality=user_data.get('nat', ''),
            age=user_data.get('dob', {}).get('age', 0),
            dob=user_data.get('dob', {})
        )

    def get_dnd_npc(self,
                   npc_type: str = "villager",
                   nationality: Optional[str] = None) -> RandomUser:
        """
        Get a random user optimized for D&D NPC generation

        Args:
            npc_type: Type of NPC ("villager", "merchant", "noble", "commoner")
            nationality: Country code for nationality

        Returns:
            RandomUser object suitable for D&D NPC
        """
        # Default to fantasy-appropriate nationalities
        if not nationality:
            fantasy_nationalities = ["US", "GB", "FR", "DE", "ES", "IT"]
            nationality = fantasy_nationalities

        # Get user with relevant fields only
        include_fields = ["gender", "name", "location", "email", "picture", "nat", "dob"]

        return self.get_random_user(
            nationality=nationality,
            include_fields=include_fields
        )

    def get_character_name(self,
                          gender: Optional[str] = None,
                          nationality: Optional[str] = None) -> str:
        """
        Get just a character name (lightweight request)

        Args:
            gender: "male", "female", or None for random
            nationality: Country code

        Returns:
            Full name string
        """
        user = self.get_random_user(
            gender=gender,
            nationality=nationality,
            include_fields=["name"]
        )
        return user.full_name

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

# Convenience functions for easy integration
def get_random_npc(npc_type: str = "villager") -> RandomUser:
    """Get a random NPC for D&D games"""
    api = RandomUserAPI()
    return api.get_dnd_npc(npc_type)

def get_random_name(gender: Optional[str] = None) -> str:
    """Get a random character name"""
    api = RandomUserAPI()
    return api.get_character_name(gender)

def get_multiple_npcs(count: int = 3) -> List[RandomUser]:
    """Get multiple NPCs for D&D games"""
    api = RandomUserAPI()
    return api.get_multiple_users(count)

if __name__ == "__main__":
    # Test the API
    api = RandomUserAPI()

    try:
        print("Testing Random User API...")

        # Test single user
        user = api.get_random_user()
        print(f"Random User: {user.full_name}")
        print(f"Location: {user.location_string}")
        print(f"Email: {user.email}")
        print(f"Profile Picture: {user.profile_picture_url}")

        # Test D&D NPC
        npc = api.get_dnd_npc("merchant")
        print(f"\nD&D NPC: {npc.title_name}")
        print(f"NPC Location: {npc.location_string}")

        # Test multiple users
        users = api.get_multiple_users(3)
        print(f"\nMultiple Users:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.full_name} ({user.gender})")

    except APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
