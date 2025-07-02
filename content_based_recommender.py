from typing import Dict, List
import pandas as pd
import numpy as np
from scipy.special import softmax

from nutrition_calculator import NutritionCalculator

class ContentBasedRecommender:
    '''
    Core recommendation engine using content-based filtering
    It maches user nutritional needs with recipe attributes
    '''
    def __init__(self, recipes_df:pd.DataFrame):
        self.recipes_df = recipes_df
        self.nutrition_calc = NutritionCalculator()

    def get_meal_distribution(self, goal:str, activity_level:str):
        '''
        Research-based meal calorie distribution that adapts to user goals and activity

        Based on:
            - Sports nutrition research for active individuals
            - Weight management studies for calorie distribution
            - Metabolic research on meal timing
        '''

        base_distribution = {
            'loss': {
                'breakfast': 0.30, # Higher breakfast for metabolism boost
                'lunch': 0.35, # Larger lunch when most active
                'dinner': 0.25, # Smaller dinner for weight loss
                'snack': 0.10 # Controlled snacking
            },
            'gain':{
                'breakfast': 0.25, # moderate breakfast
                'lunch': 0.30, # sustantial lunch
                'dinner': 0.35, # larger dinner for recovery
                'snack': 0.10 # strategic snacking
            },
            'maintain': {
                'breakfast': 0.25,
                'lunch': 0.35, 
                'dinner': 0.30, 
                'snack': 0.10 
            }
        }
        distribution = base_distribution.get(goal, base_distribution['maintain'])

        #Adjust for high acitivity levels (need more fuel)
        if activity_level in ['very_active', 'moderately_active']:
            distribution['snack'] += 0.05
            distribution['dinner'] -= 0.05
        return distribution

    def get_macro_distribution(self, goal: str, meal_type: str):
        """
        Research-based macro distribution by meal type and goal
        
        Based on:
        - Protein timing research for muscle protein synthesis
        - Carbohydrate timing for energy and recovery
        - Fat distribution for hormone production and satiety
        """
        base_macros = {
            'loss': {
                'breakfast': {'protein': 0.35, 'carbs': 0.40, 'fat': 0.25},  # High protein start
                'lunch': {'protein': 0.30, 'carbs': 0.45, 'fat': 0.25},     # Balanced energy
                'dinner': {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30},    # Protein-focused
                'snack': {'protein': 0.25, 'carbs': 0.35, 'fat': 0.40}      # Satisfying fats
            },
            'gain': {
                'breakfast': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25},  # Energy focus
                'lunch': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25},     # Fuel for activity
                'dinner': {'protein': 0.30, 'carbs': 0.45, 'fat': 0.25},    # Recovery focus
                'snack': {'protein': 0.20, 'carbs': 0.55, 'fat': 0.25}      # Quick energy
            },
            'maintain': {
                'breakfast': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25},
                'lunch': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25},
                'dinner': {'protein': 0.30, 'carbs': 0.40, 'fat': 0.30},
                'snack': {'protein': 0.20, 'carbs': 0.45, 'fat': 0.35}
            }
        }
        macros = base_macros.get(goal, base_macros['maintain'])
        return macros[meal_type]

    def filter_by_dietary_preferences(self, recipe:pd.DataFrame, user_profile:Dict):
        '''
        Filter recipes based on dietary preferences and allergies
        '''
        filtered_recipes = recipe.copy()

        #Filter by dietary preference
        dietary_pref:str = user_profile.get('dietary_pref', 'non-veg')

        if dietary_pref == 'vegan':
            filtered_recipes = filtered_recipes[filtered_recipes['category'].str.lower() == dietary_pref.lower()]
        elif dietary_pref == 'vegetarian':
            filtered_recipes = filtered_recipes[filtered_recipes['category'].str.lower().isin(['vegan', 'vegetarian'])]
        
        # Filter by allergies
        allergies = user_profile.get('allergies', [])

        
        if allergies and allergies !=[]:
            # Converting user allergies to match the format in the column (e.g gluten-free, nuts-free etch)
            allergy_filters = [f"{a}-free" for a in allergies]
            strict_filtered = filtered_recipes[filtered_recipes['allergies_free'].apply(
                        lambda free_list: all(af in free_list for af in allergy_filters)
                        )]
            if len(strict_filtered) >=20:
                return strict_filtered
            
            relaxed_filtered = filtered_recipes[filtered_recipes['allergies_free'].apply(
                                    lambda free_list: any(af in free_list for af in allergy_filters)
                                    )]
            if len(relaxed_filtered) >0:
                print(f"Relaxed allergy filtering applied due to limited options")
                return relaxed_filtered

        # # Filter recipes that are free from all user allergens
        # filtered_recipes = filtered_recipes[filtered_recipes['allergies_free'].apply(
        #     lambda free_list: all(af in free_list for af in allergy_filters)
        #     )]
        return filtered_recipes


    def calculate_nutritional_score(self, recipe: pd.Series, target_calories: float, activity_level: str, meal_type: str, goal: str = 'maintain'):
        '''
        Scoring algorithm using Gaussian decay to match nutritional targets smoothly.
        Rewards closeness and punishes large mismatches softly.
        '''
    
        def gaussian_decay(actual, target, tolerance=0.05):
            """
            Compute a score between 0 and 1 based on closeness to target using Gaussian decay.
            Higher score = closer to target.
            """
            return np.exp(-((actual - target) ** 2) / (2 * (tolerance * target) ** 2))
    
        # Get meal and macro distributions
        meal_distribution = self.get_meal_distribution(goal, activity_level)
        macro_distribution = self.get_macro_distribution(goal=goal, meal_type=meal_type)
    
        meal_target_calories = round(target_calories * meal_distribution[meal_type], 2) 
        meal_protein_target = round((meal_target_calories * macro_distribution['protein']) / 4, 2)
        meal_carb_target = round((meal_target_calories * macro_distribution['carbs']) / 4,2)
        meal_fat_target = round((meal_target_calories * macro_distribution['fat']) / 9,2)

        meal_fiber_target = 6.0 if meal_type in ['breakfast', 'lunch', 'dinner'] else 3.0
    
        # Compute individual scores using Gaussian decay
        calorie_score = round(gaussian_decay(recipe['calories'], meal_target_calories, tolerance=0.05),2)
        protein_score = round(gaussian_decay(recipe['protein'], meal_protein_target, ),2)
        carb_score = round(gaussian_decay(recipe['carbs'], meal_carb_target,),2)
        fat_score = round(gaussian_decay(recipe['fats'], meal_fat_target, ),2)
        fiber_score = round(gaussian_decay(recipe.get('fiber', 0), meal_fiber_target, ), 2)

        # Goal-based weightings
        if goal == 'loss':
            weights = {'calories': 0.40, 'protein': 0.30, 'carbs': 0.15, 'fat': 0.10, 'fiber':0.10}
        elif goal == 'gain':
            weights = {'calories': 0.40, 'protein': 0.25, 'carbs': 0.25, 'fat': 0.10, 'fiber':0.10}
        else:
            weights = {'calories': 0.40, 'protein': 0.25, 'carbs': 0.25, 'fat': 0.10, 'fiber':0.10}

        # Meal-specific adjustments
        if meal_type == 'breakfast':
            weights['protein'] *= 1.2
        elif meal_type == 'dinner' and goal == 'loss':
            weights['calories'] *= 1.3
        elif meal_type == 'snack':
            weights['fat'] *= 1.2

        # Weighted total score
        total_score = (
        weights['calories'] * calorie_score +
        weights['protein'] * protein_score +
        weights['carbs'] * carb_score +
        weights['fat'] * fat_score + 
        weights['fiber'] * fiber_score 
    )

        # Bonus scoring
        bonus = 0
        calorie_diff = abs(recipe['calories'] - meal_target_calories) / meal_target_calories
        if calorie_diff <= 0.02:
            bonus += 0.05
        elif calorie_diff <=0.05:
            bonus +=0.03
        elif recipe['protein'] >= meal_protein_target * 0.8:
            bonus += 0.03

    # Bonus for balanced macro profile (especially protein ratio)
        recipe_protein_ratio = (recipe['protein'] * 4) / recipe['calories']
        target_protein_ratio = macro_distribution['protein']
        if abs(recipe_protein_ratio - target_protein_ratio) <= 0.05:
            bonus += 0.02

        final_score = min(total_score + bonus, 1.0)
        return final_score


    def add_variety_penalty(self, recipes: pd.DataFrame, recent_recipes:List[str], penalty_factor: float = 0.6):
        '''
        Add penalty to recently used recipes to encourage variety

        Args:
            recipes: Dataframe with scores
            recent_recipes: List of recently used recipe names

        Returns:
            DataFrame with adjusted scores
            
        '''
        recipes = recipes.copy()

        #Reduce score for recently used recipes
        for i, recipe_name in enumerate(recent_recipes):
            #Decay penality for older recipes
            decay_factor = penalty_factor * (0.8 ** i) # Exponential decay
            mask = recipes['name'] == recipe_name
            recipes.loc[mask, 'score'] *= decay_factor
        return recipes
    
    def select_diverse_recipes(self, scored_recipes: pd.DataFrame, n_options:int = 3, used_recipes_count:dict = None):
        '''
        Select recipe with improved diversity control

        Args:
            scored_recipes: DataFrame with nutritional scores
            n_options: Number of top recipes to randomly select from
        '''
        if len(scored_recipes) == 0:
            return None
        
        if used_recipes_count:
            scored_recipes = scored_recipes.copy()
            for recipe_name, count in used_recipes_count.items():
                if count >=2:
                    mask = scored_recipes['name'] == recipe_name
                    scored_recipes.loc[mask, 'score'] *= (0.1 ** count)

        #Get top N recipes
        top_recipes = scored_recipes.nlargest(n_options, 'score')

        # Temperature-based selection (higher temperature = more exploration)
        temperature = 0.3
        scores = top_recipes['score'].values
        
        # Apply temperature scaling
        scaled_scores = scores / temperature
        probabilities = softmax(scaled_scores)
        
        # Select based on weighted probability
        selected_idx = np.random.choice(len(top_recipes), p=probabilities)
        return top_recipes.iloc[0]
    
    def filter_recipes_by_calorie_window(self, recipes_df: pd.DataFrame, meal_target_calories:float, window:float = 0.05):
        '''
        Filters recipes to only those within ±2% window of target calories
        '''
        lower_bound = meal_target_calories * (1 - window)
        upper_bound = meal_target_calories * (1 + window)
        filtered = recipes_df[(recipes_df['calories'] >= lower_bound) & (recipes_df['calories'] <= upper_bound)]
        return filtered
    def generate_meal_plan(self, user_profile: Dict, days: int = 7, 
                          recent_recipes: List[str] = None, max_recipe_repeats: int = 3):
        """
        Generate optimized meal plan with improved algorithm
        """
        if recent_recipes is None:
            recent_recipes = []
        
        # Calculate nutritional needs
        bmr = self.nutrition_calc.calculate_bmr(
            user_profile['weight'], user_profile['height'], 
            user_profile['age'], user_profile['gender']
        )
        
        tdee = self.nutrition_calc.calculate_tdee(bmr, user_profile['activity_level'])
        target_calories = self.nutrition_calc.calculate_target_calories(tdee, user_profile['weight_goal'])
        target_macros = self.nutrition_calc.calculate_macros(target_calories= target_calories, weight_goal=user_profile['weight_goal'], body_weight=user_profile['weight'], activity_level=user_profile['activity_level'])
        
        # Filter recipes
        suitable_recipes = self.filter_by_dietary_preferences(self.recipes_df, user_profile)
        
        meal_plan = {}
        used_recipes = recent_recipes.copy()
        # Track how many times each recipe is used
        recipe_usage_count = {}
        goal = user_profile.get('weight_goal', 'maintain')
        activity_level = user_profile.get('activity_level', 'lightly_active')
        
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        # Pre calulating available recipes per meal type
        meal_type_recipes = {}
        for meal_type in meal_types:
            meal_type_recipes[meal_type] = suitable_recipes[suitable_recipes['meal_type'].str.lower() == meal_type.lower()].copy()
            print(f"Available {meal_type} recipes: {len(meal_type_recipes[meal_type])}")
        for day in range(1, days + 1):
            daily_meals = {}
            daily_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
            
            print(f"\n---Planning Day {day} ---")
            for meal_type in meal_types:
                # Get meal-specific recipes
                meal_recipes = suitable_recipes[
                    suitable_recipes['meal_type'].str.lower() == meal_type.lower()
                ].copy()

                # Calculating target calories for this meal
                meal_distribution = self.get_meal_distribution(goal, activity_level)
                meal_target_calories = round(target_calories * meal_distribution[meal_type],2)

                meal_recipes = self.filter_recipes_by_calorie_window(
                    meal_recipes,
                    meal_target_calories=meal_target_calories,
                    window=0.05
                )

                if meal_recipes.empty:
                    print(f"No recipes found within ±2% window for {meal_type}, using full set.")
                    meal_recipes = suitable_recipes[suitable_recipes['meal_type'].str.lower() == meal_type.lower()].copy()
                
                if len(meal_recipes) > 0:
                    # Calculate advanced nutritional scores
                    meal_recipes['score'] = meal_recipes.apply(
                        lambda x: self.calculate_nutritional_score(
                            x, target_calories, meal_type= meal_type, goal= goal, activity_level= activity_level
                        ), axis=1
                    )

                    # Penalizing very low-protein breakfast
                    if meal_type =='breakfast':
                        meal_recipes.loc[meal_recipes['protein'] < 10, 'score'] *= 0.9
                    
                    # Apply variety penalty
                    meal_recipes = self.add_variety_penalty(meal_recipes, used_recipes)
                    
                    # Select recipe
                    selected_recipe = self.select_diverse_recipes(meal_recipes, n_options=min(5, len(meal_recipes)), used_recipes_count=recipe_usage_count)

                    
                    if selected_recipe is not None:
                        recipe_name:str = selected_recipe['name']

                        #Checking if recipe exceeds max repeats
                        current_usage = recipe_usage_count.get(recipe_name, 0)

                        # if recipe is overused, try to fine the alternative
                        attempts = 0
                        while current_usage >= max_recipe_repeats and attempts <3:
                            print(f"Recipe '{recipe_name}' used {current_usage} times, finding alternative...")

                            # Removing overused recipe and try again
                            meal_recipes_filtered = meal_recipes[meal_recipes['name'].str != recipe_name].copy()
                            if len(meal_recipes_filtered) > 0:
                                selected_recipe = self.select_diverse_recipes(meal_recipes_filtered, n_options=min(5, len(meal_recipes_filtered)), used_recipes_count=recipe_usage_count)
                                recipe_name = selected_recipe['name']
                                current_usage = recipe_usage_count.get(recipe_name, 0)

                            else:
                                break
                            attempts +=1
                        daily_meals[meal_type] = {
                            'name': selected_recipe['name'],
                            'calories': float(selected_recipe['calories']),
                            'protein': float(selected_recipe['protein']),
                            'carbs': float(selected_recipe['carbs']),
                            'fats': float(selected_recipe['fats']),
                            'ingredients': selected_recipe.get('ingredients', ''),
                            'instructions': selected_recipe.get('instructions', ''),
                            'score': float(selected_recipe['score'])
                        }
                        
                        # Track usage
                        used_recipes.insert(0, recipe_name)  # Most recent first
                        used_recipes = used_recipes[:15]  # Keep only recent 15
                        recipe_usage_count[recipe_name] = recipe_usage_count.get(recipe_name, 0) + 1

                        print(f"{meal_type.title()}: {recipe_name} (used {recipe_usage_count[recipe_name]} times)")
                        
                        # Update daily totals
                        daily_totals['calories'] += float(selected_recipe['calories'])
                        daily_totals['protein'] += float(selected_recipe['protein'])
                        daily_totals['carbs'] += float(selected_recipe['carbs'])
                        daily_totals['fat'] += float(selected_recipe['fats'])
            
            # Add daily summary
            daily_meals['daily_summary'] = {
                'total_calories': round(daily_totals['calories'], 1),
                'total_protein': round(daily_totals['protein'], 1),
                'total_carbs': round(daily_totals['carbs'], 1),
                'total_fat': round(daily_totals['fat'], 1),
                'target_calories': round(target_calories, 2),
                'calorie_variance': round(((daily_totals['calories'] - target_calories) / target_calories) * 100, 1),
                'protein_target': round(target_macros['protein'], 1),
                'carbs_target': round(target_macros['carbs'], 1),
                'fat_target': round(target_macros['fat'], 1)
            }
            
            meal_plan[f'day_{day}'] = daily_meals
        # Nutrition summary
        nutrition_summary = {
            'user_profile': {
                'bmr': round(bmr, 1),
                'tdee': round(tdee, 1),
                'target_calories': round(target_calories, 1),
                'target_macros': target_macros,
                'meal_distribution': self.get_meal_distribution(goal, activity_level)
            },
            'plan_duration': days,
            'avg_calorie_variance': round(np.mean([
                meal_plan[f'day_{i}']['daily_summary']['calorie_variance'] 
                for i in range(1, days + 1)
            ]), 1)
        }
        
        return meal_plan, nutrition_summary