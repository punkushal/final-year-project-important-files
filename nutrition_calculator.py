class NutritionCalculator:
    
    '''
    Calculates daily caloric and macronutrient needs based on user profile
    Uses scientifically validated formulas
    '''
    def calculate_bmr (self, weight:float, height:float, age:int, gender:str):
        '''
        Calculate basal metabolic rate using miffin-st jeor equation
        Most accurate for general population

        Args:
            weight: in kg
            height: in cm
            age: in years
            gender: 'male' or 'female'

        Returns:
            BMR in calories per day
        '''
        if gender.lower() =='male':
            bmr = 10 * weight + 6.25 * height - 5*age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return round(bmr,2)

    def calculate_tdee(self, bmr:float, activity_level:str):
        '''
        Calculate total daily energy expenditure

        Args:
            bmr: Basal metabolic rate
            activity_level : one of ['sedentary', 'lightly_active', 'moderately_active', 'very_active']
        Returns:
            TDEE in calories per day
        '''
        activity_multipliers = {
            'sedentary': 1.2,           # Little to no exercise
            'lightly_active': 1.375,    # Light exercise 1-3 days/week
            'moderately_active': 1.55,  # Moderate exercise 3-5 days/week
            'very_active': 1.725        # Heavy exercise 6-7 days/week
        }

        return round(bmr * activity_multipliers.get(activity_level, 1.2), 2)

    def calculate_target_calories(self, tdee:float, wt_goal:str):
        '''
        Calculate target daily calories based on weight goal

        Args:
            tdee: Total daily energy expenditure
            wt_goal: 'loss', 'maintain' or 'gain'

        Returns:
            Daily target calories
        '''
        if wt_goal == 'loss':
            # 500 calories deficit for ~1 pound/week loss
            return round(tdee - 500, 2)

        elif wt_goal == 'gain':
            # 500 calories surplus for ~1 pound/week loss
            return round(tdee + 500, 2)

        else:
            return tdee #maintain

    def calculate_macros(self, target_calories: float, weight_goal: str, body_weight:float, activity_level:str):
        """
        Calculate target macronutrient distribution
        
        Research basis:
            - Protein: 0.8-2.2/kg body weight depending on goals (Phillips & Van Loon, 2011)
            - Carbs : 3-12 g/kg for active individuals (Thomas et al., 2016)
            - Fat: 20-35% of total calories (AMDR recommendations)
        """
        # # Macro ratios based on goals (research-based)
        # if weight_goal == 'loss':
        #     # Higher protein for muscle preservation during deficit
        #     protein_ratio, carb_ratio, fat_ratio = 0.35, 0.35, 0.30
        # elif weight_goal == 'gain':
        #     # Higher carbs for energy and muscle building
        #     protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30
        # else:  # maintain
        #     # Balanced approach
        #     protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30
        # Body weight-based calculations (more accurate)
        if weight_goal == 'loss':
            protein_g_per_kg = 2.0  # High protein for muscle preservation
            activity_multiplier = {'sedentary': 0.8, 'lightly_active': 0.9, 
                                     'moderately_active': 1.0, 'very_active': 1.2}.get(activity_level, 1.0)
            carb_g_per_kg = 3.0 * activity_multiplier  # Lower carbs for fat loss
                
        elif weight_goal == 'gain':
            protein_g_per_kg = 1.6  # Adequate for muscle building
            activity_multiplier = {'sedentary': 1.0, 'lightly_active': 1.2, 
                                     'moderately_active': 1.4, 'very_active': 1.6}.get(activity_level, 1.4)
            carb_g_per_kg = 5.0 * activity_multiplier  # Higher carbs for energy
                
        else:  # maintain
            protein_g_per_kg = 1.4  # Balanced maintenance
            activity_multiplier = {'sedentary': 0.9, 'lightly_active': 1.1, 
                                     'moderately_active': 1.3, 'very_active': 1.5}.get(activity_level, 1.3)
            carb_g_per_kg = 4.0 * activity_multiplier

        # Calculate grams
        max_protein_per_kg = 2.2
        protein_grams = min(body_weight * protein_g_per_kg, max_protein_per_kg * body_weight)
        carb_grams = body_weight * carb_g_per_kg

        # Calculate calories from protein and carbs
        protein_calories = protein_grams * 4
        carb_calories = carb_grams * 4

        # Remaining calories from fat
        remaining_calories = target_calories - protein_calories - carb_calories
        fat_grams = max(remaining_calories / 9 , target_calories * 0.20 / 9) #Minimum 20% fat

        #Adjusting if total exceeds target
        total_calories = protein_calories + carb_calories + (fat_grams * 9)
        if total_calories > target_calories:
            #Reduce carbs first , then fat
            excess = total_calories - target_calories
            carb_reduction = min(excess / 4, carb_grams * 0.2) # max 20% reduction
            carb_grams -= carb_reduction

            #Recalculate
            carb_calories = carb_grams * 4
            remaining_calories = target_calories - protein_calories - carb_calories
            fat_grams  = remaining_calories / 9

        return {
             'protein': round(protein_grams, 1),
                'carbs': round(carb_grams, 1),
                'fat': round(fat_grams, 1)
        }
    
    def get_goal_based_weights(self, goal: str):
        """
        Returns weightings for calorie, protein, carbs, fat deviation
        based on user goal.

        Based on:
            - Weight loss: Calorie control most imp, then protein
            - Weight gain: calorie surplus most imp, then carbs for energey
            - Maintenacne: Balanced approach with slight protein emphasis
        """
        goal = goal.lower()
        if goal == 'loss':
            return {'calories': 0.35, 'protein': 0.30, 'carbs': 0.20, 'fat': 0.15}
        elif goal == 'gain':
            return {'calories': 0.30, 'protein': 0.25, 'carbs': 0.30, 'fat': 0.15}
        else:  # default to maintain
            return {'calories': 0.25, 'protein': 0.30, 'carbs': 0.25, 'fat': 0.20}
        