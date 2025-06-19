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

    def calculate_macros(self, target_calories: float, weight_goal: str):
        """
        Calculate target macronutrient distribution
        
        Args:
            target_calories: Target daily calories
            weight_goal: Weight goal for macro optimization
        
        Returns:
            Dictionary with target grams of protein, carbs, fat
        """
        # Macro ratios based on goals (research-based)
        if weight_goal == 'loss':
            # Higher protein for muscle preservation during deficit
            protein_ratio, carb_ratio, fat_ratio = 0.35, 0.35, 0.30
        elif weight_goal == 'gain':
            # Higher carbs for energy and muscle building
            protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30
        else:  # maintain
            # Balanced approach
            protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30
        
        return {
            'protein': round((target_calories * protein_ratio) / 4, 1),  # 4 cal/gram
            'carbs': round((target_calories * carb_ratio) / 4, 1),       # 4 cal/gram
            'fat': round((target_calories * fat_ratio) / 9, 1)           # 9 cal/gram
        }
    
    def get_goal_based_weights(self, goal: str):
        """
        Returns weightings for calorie, protein, carbs, fat deviation
        based on user goal.

        Returns:
        Dict[str, float]
        """
        goal = goal.lower()
        if goal == 'loss':
            return {'calories': 0.5, 'protein': 0.3, 'carbs': 0.15, 'fat': 0.05}
        elif goal == 'gain':
            return {'calories': 0.3, 'protein': 0.4, 'carbs': 0.2, 'fat': 0.1}
        else:  # default to balanced
            return {'calories': 0.4, 'protein': 0.25, 'carbs': 0.2, 'fat': 0.15}
        