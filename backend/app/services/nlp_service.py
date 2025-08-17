import openai
import spacy
import re
from typing import List, Dict, Any, Optional
from ..schemas.food import ParsedFoodEntry, FoodItem, MealType
from ..core.config import settings
from datetime import datetime

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY

# Load spaCy model
try:
    nlp = spacy.load(settings.SPACY_MODEL)
except OSError:
    print(f"spaCy model '{settings.SPACY_MODEL}' not found. Please install it with:")
    print(f"python -m spacy download {settings.SPACY_MODEL}")
    nlp = None


class NLPService:
    """Service for parsing natural language food entries"""
    
    def __init__(self):
        self.indian_food_patterns = {
            'roti': ['roti', 'chapati', 'phulka', 'tortilla'],
            'dal': ['dal', 'lentils', 'pulses', 'daal'],
            'rice': ['rice', 'chawal', 'bhaat'],
            'curry': ['curry', 'sabzi', 'vegetables'],
            'bread': ['bread', 'naan', 'paratha', 'puri'],
            'yogurt': ['yogurt', 'curd', 'dahi'],
            'milk': ['milk', 'doodh'],
            'tea': ['tea', 'chai'],
            'coffee': ['coffee', 'kaffee']
        }
        
        self.unit_patterns = {
            'piece': ['piece', 'pieces', 'pc', 'pcs', 'slice', 'slices'],
            'bowl': ['bowl', 'bowls', 'katori'],
            'glass': ['glass', 'glasses', 'cup', 'cups'],
            'spoon': ['spoon', 'spoons', 'tbsp', 'tsp'],
            'gram': ['gram', 'grams', 'g', 'gm'],
            'kilogram': ['kilogram', 'kilograms', 'kg'],
            'milliliter': ['milliliter', 'milliliters', 'ml'],
            'liter': ['liter', 'liters', 'l']
        }
        
        self.quantity_patterns = {
            'half': 0.5,
            'quarter': 0.25,
            'third': 1/3,
            'two_thirds': 2/3,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5
        }
    
    async def parse_food_entry(self, text: str, meal_type: Optional[MealType] = None) -> ParsedFoodEntry:
        """
        Parse natural language food entry using GPT-4 and spaCy
        """
        try:
            # First try with GPT-4 for better accuracy
            if settings.OPENAI_API_KEY:
                return await self._parse_with_gpt(text, meal_type)
            else:
                # Fallback to spaCy
                return self._parse_with_spacy(text, meal_type)
        except Exception as e:
            print(f"Error parsing food entry: {e}")
            # Fallback to basic parsing
            return self._parse_basic(text, meal_type)
    
    async def _parse_with_gpt(self, text: str, meal_type: Optional[MealType] = None) -> ParsedFoodEntry:
        """Parse using OpenAI GPT-4"""
        
        prompt = f"""
        Parse the following food entry and extract food items with quantities and units.
        Return a JSON response in this exact format:
        {{
            "foods": [
                {{"item": "food_name", "quantity": number, "unit": "unit_name"}}
            ],
            "meal_type": "{meal_type.value if meal_type else 'unknown'}",
            "confidence": 0.95
        }}
        
        Food entry: "{text}"
        
        Rules:
        - Extract all food items mentioned
        - Convert quantities to numbers (e.g., "two" -> 2, "half" -> 0.5)
        - Use standard units (piece, bowl, glass, gram, ml, etc.)
        - For Indian foods, use appropriate units (roti -> piece, dal -> bowl, milk -> glass)
        - If no quantity mentioned, assume 1
        - If no unit mentioned, infer from context
        
        Examples:
        - "2 rotis and dal" -> {{"item": "roti", "quantity": 2, "unit": "piece"}}, {{"item": "dal", "quantity": 1, "unit": "bowl"}}
        - "milk and coffee" -> {{"item": "milk", "quantity": 1, "unit": "glass"}}, {{"item": "coffee", "quantity": 1, "unit": "cup"}}
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a food parsing assistant. Parse food entries accurately and return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                import json
                parsed_data = json.loads(json_match.group())
                
                foods = []
                for food in parsed_data.get('foods', []):
                    foods.append(FoodItem(
                        item=food['item'],
                        quantity=float(food['quantity']),
                        unit=food['unit']
                    ))
                
                return ParsedFoodEntry(
                    foods=foods,
                    meal_type=MealType(parsed_data.get('meal_type', 'other')),
                    confidence=parsed_data.get('confidence', 0.9)
                )
        
        except Exception as e:
            print(f"GPT-4 parsing failed: {e}")
        
        # Fallback to spaCy
        return self._parse_with_spacy(text, meal_type)
    
    def _parse_with_spacy(self, text: str, meal_type: Optional[MealType] = None) -> ParsedFoodEntry:
        """Parse using spaCy NLP"""
        if not nlp:
            return self._parse_basic(text, meal_type)
        
        doc = nlp(text.lower())
        foods = []
        
        # Extract numbers and quantities
        numbers = [token.text for token in doc if token.like_num]
        
        # Extract food items
        food_items = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop:
                food_items.append(token.text)
        
        # Simple parsing logic
        if not food_items:
            return self._parse_basic(text, meal_type)
        
        # Match with Indian food patterns
        for item in food_items:
            quantity = 1.0
            unit = self._infer_unit(item)
            
            # Check if there's a number before this item
            for i, num in enumerate(numbers):
                if num.isdigit():
                    quantity = float(num)
                    break
                elif num in self.quantity_patterns:
                    quantity = self.quantity_patterns[num]
                    break
            
            foods.append(FoodItem(
                item=item,
                quantity=quantity,
                unit=unit
            ))
        
        return ParsedFoodEntry(
            foods=foods,
            meal_type=meal_type or MealType.OTHER,
            confidence=0.7
        )
    
    def _parse_basic(self, text: str, meal_type: Optional[MealType] = None) -> ParsedFoodEntry:
        """Basic parsing fallback"""
        # Simple regex-based parsing
        foods = []
        
        # Look for patterns like "2 rotis", "dal", etc.
        patterns = [
            r'(\d+(?:\.\d+)?)\s+(\w+)',  # "2 rotis"
            r'(\w+)\s+(\d+(?:\.\d+)?)',  # "rotis 2"
            r'(\w+)',                     # "dal"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if len(match) == 2:
                    quantity, item = match
                    foods.append(FoodItem(
                        item=item,
                        quantity=float(quantity),
                        unit=self._infer_unit(item)
                    ))
                elif len(match) == 1:
                    item = match
                    foods.append(FoodItem(
                        item=item,
                        quantity=1.0,
                        unit=self._infer_unit(item)
                    ))
        
        # Remove duplicates
        unique_foods = []
        seen_items = set()
        for food in foods:
            if food.item not in seen_items:
                unique_foods.append(food)
                seen_items.add(food.item)
        
        return ParsedFoodEntry(
            foods=unique_foods,
            meal_type=meal_type or MealType.OTHER,
            confidence=0.5
        )
    
    def _infer_unit(self, food_item: str) -> str:
        """Infer appropriate unit for a food item"""
        # Check Indian food patterns
        for category, items in self.indian_food_patterns.items():
            if food_item in items:
                if category in ['roti', 'bread']:
                    return 'piece'
                elif category in ['dal', 'curry']:
                    return 'bowl'
                elif category in ['milk', 'tea', 'coffee']:
                    return 'glass'
                elif category in ['rice']:
                    return 'bowl'
                elif category in ['yogurt']:
                    return 'bowl'
        
        # Default units
        if food_item in ['apple', 'banana', 'orange']:
            return 'piece'
        elif food_item in ['water', 'juice']:
            return 'glass'
        else:
            return 'serving'
    
    def normalize_unit(self, unit: str) -> str:
        """Normalize units to standard format"""
        unit_lower = unit.lower()
        
        for standard_unit, variations in self.unit_patterns.items():
            if unit_lower in variations:
                return standard_unit
        
        return unit_lower
    
    def convert_to_grams(self, quantity: float, unit: str) -> float:
        """Convert various units to grams for nutrition calculation"""
        unit = self.normalize_unit(unit)
        
        conversion_factors = {
            'piece': 50,      # Average piece weight
            'bowl': 150,      # Standard bowl size
            'glass': 200,     # Standard glass size
            'cup': 240,       # Standard cup size
            'spoon': 15,      # Tablespoon
            'gram': 1,
            'kilogram': 1000,
            'milliliter': 1,  # Assuming 1g = 1ml for most foods
            'liter': 1000
        }
        
        return quantity * conversion_factors.get(unit, 100)  # Default to 100g


# Create service instance
nlp_service = NLPService()
