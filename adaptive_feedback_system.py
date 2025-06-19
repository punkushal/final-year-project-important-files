from typing import Dict
from content_based_recommender import ContentBasedRecommender
from nutrition_calculator import NutritionCalculator


class AdaptiveFeedbackSystem:
    """
    Analyzes user feedback and adjusts recommendations accordingly
    """
    
    def __init__(self, recommender: ContentBasedRecommender):
        self.recommender = recommender
        self.nutrition_calc = NutritionCalculator()
    
    def analyze_weight_progress(self, user_profile: Dict, feedback: Dict):
        """
        Analyze weight progress and calculate needed adjustments
        
        Args:
            user_profile: Current user profile
            feedback: User feedback data
        
        Returns:
            Dictionary with adjustment recommendations
        """
        weight_change = feedback.get('weight_change', 0)
        weeks_elapsed = feedback.get('weeks_elapsed', 2)
        target_rate = self.get_target_weight_change_rate(user_profile['weight_goal'])
        
        # Calculate expected vs actual progress
        expected_change = target_rate * weeks_elapsed
        deviation = weight_change - expected_change
        
        # Determine calorie adjustment needed
        # 1 pound = ~3500 calories, so 500 cal/day = 1 lb/week
        calorie_adjustment = 0
        
        if user_profile['weight_goal'] == 'loss':
            if deviation > 0.5:  # Lost less than expected
                calorie_adjustment = -200  # Increase deficit
            elif deviation < -1:  # Lost too much
                calorie_adjustment = 150   # Reduce deficit
        
        elif user_profile['weight_goal'] == 'gain':
            if deviation < -0.5:  # Gained less than expected
                calorie_adjustment = 200   # Increase surplus
            elif deviation > 1:   # Gained too much
                calorie_adjustment = -150  # Reduce surplus
        
        return {
            'calorie_adjustment': calorie_adjustment,
            'weight_deviation': deviation,
            'progress_rating': self.rate_progress(deviation, user_profile['weight_goal'])
        }
    
    def get_target_weight_change_rate(self, weight_goal: str) -> float:
        """Get target weight change per week based on goal"""
        targets = {
            'loss': -1.0,    # 1 lb loss per week
            'gain': 1.0,     # 1 lb gain per week
            'maintain': 0.0  # No change
        }
        return targets.get(weight_goal, 0.0)
    
    def rate_progress(self, deviation: float, weight_goal: str) -> str:
        """Rate user's progress"""
        if weight_goal == 'maintain':
            if abs(deviation) <= 0.5:
                return 'excellent'
            elif abs(deviation) <= 1.0:
                return 'good'
            else:
                return 'needs_adjustment'
        else:
            if abs(deviation) <= 0.5:
                return 'excellent'
            elif abs(deviation) <= 1.0:
                return 'good'
            else:
                return 'needs_adjustment'
    
    def process_satisfaction_feedback(self, feedback: Dict):
        """
        Process user satisfaction feedback
        
        Args:
            feedback: Feedback dictionary
        
        Returns:
            Processed feedback insights
        """
        satisfaction_score = feedback.get('satisfaction_score', 5)
        meal_preferences = feedback.get('meal_preferences', {})
        suggestions = feedback.get('suggestions', '')
        
        adjustments = {
            'increase_variety': False,
            'adjust_portion_sizes': False,
            'change_meal_types': [],
            'dietary_adjustments': []
        }
        
        # Analyze satisfaction score
        if satisfaction_score < 3:
            adjustments['increase_variety'] = True
        
        # Process text suggestions
        suggestions_lower = suggestions.lower()
        if 'more protein' in suggestions_lower:
            adjustments['dietary_adjustments'].append('increase_protein')
        if 'less carbs' in suggestions_lower or 'fewer carbs' in suggestions_lower:
            adjustments['dietary_adjustments'].append('reduce_carbs')
        if 'more variety' in suggestions_lower or 'different' in suggestions_lower:
            adjustments['increase_variety'] = True
        if 'portion' in suggestions_lower:
            adjustments['adjust_portion_sizes'] = True
        
        return adjustments
    
    def generate_updated_meal_plan(self, user_id: int, feedback: Dict, 
                                 user_profile: Dict):
        """
        Generate updated meal plan based on feedback
        
        Args:
            user_id: User ID
            feedback: User feedback data
            user_profile: Current user profile
        
        Returns:
            Tuple of (updated_meal_plan, adjustment_message)
        """
        # Analyze weight progress
        weight_analysis = self.analyze_weight_progress(user_profile, feedback)
        
        # Process satisfaction feedback
        satisfaction_analysis = self.process_satisfaction_feedback(feedback)
        
        # Update user profile with adjustments
        updated_profile = user_profile.copy()
        
        # Adjust calories if needed
        if weight_analysis['calorie_adjustment'] != 0:
            current_target = updated_profile.get('target_calories', 
                self.nutrition_calc.calculate_target_calories(
                    self.nutrition_calc.calculate_tdee(
                        updated_profile.get('bmr', 1500), 
                        updated_profile['activity_level']
                    ), 
                    updated_profile['weight_goal']
                )
            )
            updated_profile['target_calories'] = current_target + weight_analysis['calorie_adjustment']
        
        # Get recent recipes to avoid repetition
        recent_recipes = self.get_recent_recipes(user_id, days=14)
        
        # Generate new meal plan
        updated_meal_plan, nutrition_summary = self.recommender.generate_meal_plan(
            updated_profile, days=7, recent_recipes=recent_recipes
        )
        
        # Create adjustment message
        message_parts = []
        if weight_analysis['calorie_adjustment'] != 0:
            direction = "increased" if weight_analysis['calorie_adjustment'] > 0 else "decreased"
            message_parts.append(f"Daily calories {direction} by {abs(weight_analysis['calorie_adjustment'])}")
        
        if satisfaction_analysis['increase_variety']:
            message_parts.append("Increased recipe variety")
        
        if satisfaction_analysis['dietary_adjustments']:
            message_parts.append(f"Adjusted macronutrients: {', '.join(satisfaction_analysis['dietary_adjustments'])}")
        
        adjustment_message = "; ".join(message_parts) if message_parts else "Plan optimized based on your feedback"
        
        return updated_meal_plan, adjustment_message
    
    def get_recent_recipes(self, user_id: int, days: int = 14):
        """
        Get recently used recipe IDs for a user
        
        Args:
            user_id: User ID
            days: Number of days to look back
        
        Returns:
            List of recent recipe IDs
        """
        # This would typically query the database
        # For now, return empty list - implement based on your database structure
        return []