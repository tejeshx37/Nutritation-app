import httpx
import json
from typing import List, Dict, Any, Optional
from ..core.config import settings
from ..schemas.food import FoodResponse
import base64
import hashlib
import time
import hmac


class FatSecretService:
    """Service for interacting with FatSecret API"""
    
    def __init__(self):
        self.client_id = settings.FATSECRET_CLIENT_ID
        self.client_secret = settings.FATSECRET_CLIENT_SECRET
        self.redirect_uri = settings.FATSECRET_REDIRECT_URI
        self.base_url = "https://platform.fatsecret.com/rest/server.api"
        self.auth_url = "https://oauth.fatsecret.com/connect/authorize"
        self.token_url = "https://oauth.fatsecret.com/connect/token"
        
        # OAuth 2.0 PKCE parameters
        self.code_verifier = None
        self.code_challenge = None
        self.access_token = None
        self.refresh_token = None
    
    def _generate_pkce_params(self):
        """Generate PKCE code verifier and challenge"""
        import secrets
        import base64
        
        # Generate random code verifier
        self.code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        # Generate code challenge
        code_challenge_bytes = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
        self.code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode('utf-8').rstrip('=')
        
        return self.code_verifier, self.code_challenge
    
    def get_authorization_url(self) -> str:
        """Get OAuth 2.0 authorization URL"""
        self._generate_pkce_params()
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'basic',
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': authorization_code,
            'code_verifier': self.code_verifier
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            
            return token_data
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token', self.refresh_token)
            
            return token_data
    
    async def search_foods(self, query: str, max_results: int = 20) -> List[FoodResponse]:
        """Search for foods in FatSecret database"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        params = {
            'method': 'foods.search',
            'search_expression': query,
            'max_results': max_results,
            'format': 'json'
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            foods = data.get('foods', {}).get('food', [])
            
            # Convert to list if single food item
            if not isinstance(foods, list):
                foods = [foods]
            
            return [self._convert_fatsecret_food(food) for food in foods]
    
    async def get_food_details(self, food_id: str) -> Optional[FoodResponse]:
        """Get detailed nutrition information for a specific food"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        params = {
            'method': 'food.get.v2',
            'food_id': food_id,
            'format': 'json'
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            food = data.get('food', {})
            
            return self._convert_fatsecret_food(food)
    
    async def get_food_by_barcode(self, barcode: str) -> Optional[FoodResponse]:
        """Get food information by barcode"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        params = {
            'method': 'food.find_id_for_barcode',
            'barcode': barcode,
            'format': 'json'
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            food_id = data.get('food_id')
            
            if food_id:
                return await self.get_food_details(food_id)
            
            return None
    
    def _convert_fatsecret_food(self, fatsecret_food: Dict[str, Any]) -> FoodResponse:
        """Convert FatSecret food data to our FoodResponse schema"""
        
        # Extract nutrition information
        servings = fatsecret_food.get('servings', {}).get('serving', [])
        if not isinstance(servings, list):
            servings = [servings]
        
        # Get the first serving for nutrition per 100g
        first_serving = servings[0] if servings else {}
        
        # Calculate nutrition per 100g
        serving_size = first_serving.get('metric_serving_amount', 0)
        if serving_size == 0:
            serving_size = 100
        
        calories_per_100g = None
        protein_per_100g = None
        carbs_per_100g = None
        fat_per_100g = None
        fiber_per_100g = None
        sugar_per_100g = None
        sodium_per_100g = None
        
        if first_serving:
            # Calculate per 100g values
            multiplier = 100 / serving_size
            
            calories = float(first_serving.get('calories', 0))
            calories_per_100g = calories * multiplier
            
            protein = float(first_serving.get('protein', 0))
            protein_per_100g = protein * multiplier
            
            carbs = float(first_serving.get('carbohydrate', 0))
            carbs_per_100g = carbs * multiplier
            
            fat = float(first_serving.get('fat', 0))
            fat_per_100g = fat * multiplier
            
            fiber = float(first_serving.get('fiber', 0))
            fiber_per_100g = fiber * multiplier
            
            sugar = float(first_serving.get('sugar', 0))
            sugar_per_100g = sugar * multiplier
            
            sodium = float(first_serving.get('sodium', 0))
            sodium_per_100g = sodium * multiplier
        
        # Determine if it's Indian food based on name
        food_name = fatsecret_food.get('food_name', '').lower()
        indian_food_keywords = [
            'roti', 'chapati', 'dal', 'lentil', 'curry', 'naan', 'paratha',
            'puri', 'biryani', 'pulao', 'samosa', 'pakora', 'gulab jamun',
            'rasgulla', 'jalebi', 'lassi', 'chai', 'masala', 'tandoori'
        ]
        
        is_indian_food = any(keyword in food_name for keyword in indian_food_keywords)
        
        return FoodResponse(
            id=int(fatsecret_food.get('food_id', 0)),
            name=fatsecret_food.get('food_name', ''),
            brand=fatsecret_food.get('brand_name'),
            calories_per_100g=calories_per_100g,
            protein_per_100g=protein_per_100g,
            carbs_per_100g=carbs_per_100g,
            fat_per_100g=fat_per_100g,
            fiber_per_100g=fiber_per_100g,
            sugar_per_100g=sugar_per_100g,
            sodium_per_100g=sodium_per_100g,
            serving_size=first_serving.get('metric_serving_unit'),
            serving_weight_grams=serving_size,
            category=fatsecret_food.get('food_type'),
            subcategory=None,
            is_indian_food=is_indian_food
        )
    
    async def get_daily_summary(self, date: str) -> Dict[str, Any]:
        """Get user's daily food summary"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        params = {
            'method': 'food_entries.get_month',
            'date': date,
            'format': 'json'
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            return response.json()


# Create service instance
fatsecret_service = FatSecretService()
