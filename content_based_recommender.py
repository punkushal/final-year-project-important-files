from typing import Dict, List
import pandas as pd
import numpy as np

from nutrition_calculator import NutritionCalculator

class ContentBasedRecommender:
    '''
    Core recommendation engine using content-based filtering
    It maches user nutritional needs with recipe attributes
    '''
    def __init__(self, recipes_df:pd.DataFrame):
        self.recipes_df = recipes_df
        self.nutrition_calc = NutritionCalculator()

    def filter_by_dietary_preferences(self, recipe:pd.DataFrame, user_profile:Dict):
        '''
        Filter recipes based on dietary preferences and allergies
        '''
        filtered_recipes = recipe.copy()

        #Filter by dietary preference
        dietary_pref:str = user_profile.get('dietary_pref', 'non-veg')
        if dietary_pref in ['vegan', 'vegetarian']:
            filtered_recipes = filtered_recipes[filtered_recipes['category'].str.lower() == dietary_pref.lower()]
        
        # Filter by allergies

        allergies = user_profile.get('allergies', [])
        

        # Converting user allergies to match the format in the column (e.g gluten-free, nuts-free etch)
        allergy_filters = [f"{a}-free" for a in allergies]

        # Filter recipes that are free from all user allergens
        filtered_recipes = recipe[recipe['allergies_free'].apply(
            lambda free_list: all(af in free_list for af in allergy_filters)
            )]
        return filtered_recipes

    def calculate_nutritional_score(self, recipe: pd.Series, target_calories:float, target_macros:Dict[str,float], meal_type:str):

        '''
        Score recipes based on how well they match nutritional targets
        '''
        #Meal-specific calorie distribution
        meal_calorie_ratios = {
            'breakfast': 0.25,
            'lunch':0.35,
            'dinner':0.30,
            'snack':0.10
        }
        meal_target_calories = target_calories * meal_calorie_ratios.get(meal_type, 0.25)

        #Calculate target macros for this specific meal
        meal_protein_target = target_macros['protein'] * meal_calorie_ratios.get(meal_type, 0.25)
        meal_carb_target = target_macros['carbs'] * meal_calorie_ratios.get(meal_type, 0.25)
        meal_fat_target = target_macros['fat'] * meal_calorie_ratios.get(meal_type, 0.25)

        #Calculate deviations (normalize to avoid division by zero)
        calorie_dev = abs(recipe['calories'] - meal_target_calories) / max(meal_target_calories , 1)
        protein_dev = abs(recipe['protein'] - meal_protein_target) / max(meal_protein_target , 1)
        carb_dev = abs(recipe['carbs'] - meal_carb_target) / max(meal_carb_target , 1)
        fat_dev = abs(recipe['fat'] - meal_fat_target) / max(meal_fat_target , 1)

        #weighted score calculation (lower deviation = higher score)
        #Calories are most imp, followed by protein, then carbs and fat
        total_deviation = (0.4 * calorie_dev + 0.25 * protein_dev + 0.2 * carb_dev + 0.15 * fat_dev)

        #Covert to score (higher is better)
        score = 1 / (1 + total_deviation)

        return min(score, 1.0) #cap at 1.0

    def add_variety_penalty(self, recipes: pd.DataFrame, recent_recipes:List[int]):
        '''
        Add penalty to recently used recipes to encourage variety

        Args:
            recipes: Dataframe with scores
            recent_recipes: List of recently used recipe IDs

        Returns:
            DataFrame with adjusted scores
            
        '''
        recipes = recipes.copy()

        #Reduce score for recently used recipes
        for recipe_id in recent_recipes:
            mask = recipes['recipe_id'] == recipe_id
            recipes.loc[mask, 'score'] *= 0.5 # 50% penalty
        return recipes
    
    #Yo sodnu xa ai lai like how it works
    def select_diverse_recipes(self, scored_recipes: pd.DataFrame, n_options:int = 3):
        '''
        Select recipe with some randomization to ensure variety

        Args:
            scored_recipes: DataFrame with nutritional scores
            n_options: Number of top recipes to randomly select from
        '''
        if len(scored_recipes) == 0:
            return None
        
        #Get top N recipes
        top_recipes = scored_recipes.nlargest(min(n_options, len(scored_recipes)), 'score')

        #Add some randomization weighted by score
        weights = top_recipes['score'].values
        weights = weights / weights.sum() #Normalize

        #Select based on weighted probability
        selected_idx = np.random.choice(len(top_recipes), p=weights)
        return top_recipes.iloc[selected_idx]
    
    def generate_meal_plan(self, user_profile: Dict, days: int = 7, 
                          recent_recipes: List[int] = None):
        """
        Generate a complete meal plan for specified number of days
        
        Args:
            user_profile: User profile dictionary
            days: Number of days to plan for
            recent_recipes: Recently used recipe IDs to avoid
        
        Returns:
            Tuple of (meal_plan_dict, nutrition_summary)
        """
        if recent_recipes is None:
            recent_recipes = []
        
        # Calculate user's nutritional needs
        bmr = self.nutrition_calc.calculate_bmr(
            user_profile['weight'], user_profile['height'], 
            user_profile['age'], user_profile['gender']
        )
        
        tdee = self.nutrition_calc.calculate_tdee(bmr, user_profile['activity_level'])
        target_calories = self.nutrition_calc.calculate_target_calories(tdee, user_profile['weight_goal'])
        target_macros = self.nutrition_calc.calculate_macros(target_calories, user_profile['weight_goal'])
        
        # Filter recipes based on dietary preferences
        suitable_recipes = self.filter_by_dietary_preferences(self.recipes_df, user_profile)
        
        meal_plan = {}
        used_recipes = recent_recipes.copy()
        
        # Meal types and their typical calorie distribution
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        
        for day in range(1, days + 1):
            daily_meals = {}
            daily_calories = 0
            daily_protein = 0
            daily_carbs = 0
            daily_fat = 0
            
            for meal_type in meal_types:
                # Get recipes for this meal type
                meal_recipes = suitable_recipes[
                    suitable_recipes['meal_type'].str.lower() == meal_type.lower()
                ].copy()
                
                if len(meal_recipes) > 0:
                    # Calculate nutritional scores
                    meal_recipes['score'] = meal_recipes.apply(
                        lambda x: self.calculate_nutritional_score(
                            x, target_calories, target_macros, meal_type
                        ), axis=1
                    )
                    
                    # Apply variety penalty
                    meal_recipes = self.add_variety_penalty(meal_recipes, used_recipes)
                    
                    # Select recipe with variety
                    selected_recipe = self.select_diverse_recipes(meal_recipes)
                    
                    if selected_recipe is not None:
                        daily_meals[meal_type] = {
                            'recipe_id': int(selected_recipe['recipe_id']),
                            'name': selected_recipe['name'],
                            'calories': float(selected_recipe['total_calories']),
                            'protein': float(selected_recipe['protein']),
                            'carbs': float(selected_recipe['carbs']),
                            'fat': float(selected_recipe['fat']),
                            'ingredients': selected_recipe.get('ingredients', ''),
                            'instructions': selected_recipe.get('instructions', '')
                        }
                        
                        # Track used recipes
                        used_recipes.append(int(selected_recipe['recipe_id']))
                        
                        # Accumulate daily totals
                        daily_calories += float(selected_recipe['total_calories'])
                        daily_protein += float(selected_recipe['protein'])
                        daily_carbs += float(selected_recipe['carbs'])
                        daily_fat += float(selected_recipe['fat'])
            
            # Add daily summary
            daily_meals['daily_summary'] = {
                'total_calories': round(daily_calories, 1),
                'total_protein': round(daily_protein, 1),
                'total_carbs': round(daily_carbs, 1),
                'total_fat': round(daily_fat, 1),
                'target_calories': target_calories,
                'calorie_variance': round(((daily_calories - target_calories) / target_calories) * 100, 1)
            }
            
            meal_plan[f'day_{day}'] = daily_meals
        
        # Overall nutrition summary
        nutrition_summary = {
            'user_profile': {
                'bmr': bmr,
                'tdee': tdee,
                'target_calories': target_calories,
                'target_macros': target_macros
            },
            'plan_duration': days,
            'total_recipes_used': len(set(used_recipes) - set(recent_recipes))
        }
        
        return meal_plan, nutrition_summary