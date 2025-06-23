from activity_assessment import ActivityAssessment
from content_based_recommender import ContentBasedRecommender
import pandas as pd

df = pd.read_csv('updated_recipes.csv')

recommender = ContentBasedRecommender(df)
#Asking user for their info such as age, height, weight and so on...
def get_valid_integer(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Please enter a valid number.")

def get_valid_gender():
    while True:
        gender = input("Enter your gender (male/female): ").strip().lower()
        if gender in ['male', 'female']:
            return gender
        else:
            print("Please enter 'male' or 'female'.")

def get_weight_goal():
    print("\nGoals:")
    print("1. Weight loss")
    print("2. Weight gain") 
    print("3. Maintain weight")
    goal_choice = int(input("Choose your goal (1-3): "))
            
    goal_map = {1: 'loss', 2: 'gain', 3: 'maintain'}
    goal = goal_map.get(goal_choice, 'maintain')
    return goal

def get_prefs():
    print('\nDietary preferences:')
    print('1. Vegan')
    print('2. Vegetarian')
    print('3. Non-veg')
    pref_choice = get_valid_integer('Choose your dietary preferences(1-3): ', 1, 3)
    pref_map = {1: 'vegan', 2: 'vegetarian', 3: 'non-veg'}
    pref = pref_map.get(pref_choice, 'vegetarian')
    return pref

def get_allergies():
    print('\nFood allergies:')
    print('1. gluten')
    print('2. nuts')
    print('3. dairy')
    print('4. gluten, nuts')
    print('5. nuts, dairy')
    print('6. gluten, dairy')
    print('7. all')
    print('8. none')
    choice = get_valid_integer('Choose your allergies(1-3): ', 1, 8)
    allergies_map = {1: 'gluten', 2: 'nuts', 3: 'dairy', 4: ['gluten', 'nuts'], 5: ['nuts', 'dairy'], 6:['gluten', 'dairy'], 7:['gluten', 'nuts', 'dairy'], 8:[]}
    allergies = allergies_map.get(choice, [])
    return allergies
    

def display_meal_plan(meal_plan):
    for day_key in sorted(meal_plan.keys(), key=lambda x: int(x.split('_')[1])):
        print(f"\n🗓️ {day_key.replace('_', ' ').title()}")
        daily_meals = meal_plan[day_key]
        
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            if meal_type in daily_meals:
                meal = daily_meals[meal_type]
                print(f"\n 🍽️ {meal_type.title()}: {meal['name']}")
                print(f"   - Calories: {meal['calories']} kcal")
                print(f"   - Protein: {meal['protein']} g")
                print(f"   - Carbs:   {meal['carbs']} g")
                print(f"   - Fat:     {meal['fats']} g")

                # Optional: allergens & category if present
                if 'allergens' in meal:
                    print(f"   - Allergens Free: {', '.join(meal['allergies_free']) if meal['allergies_free'] else 'None'}")
                if 'category' in meal:
                    print(f"   - Category: {meal['category'].title()}")
        
        # Daily summary
        summary = daily_meals.get('daily_summary', {})
        if summary:
            print("\n 📊 Daily Summary:")
            print(f"   - Total Calories: {summary['total_calories']} kcal")
            print(f"   - Total Protein:  {summary['total_protein']} g")
            print(f"   - Total Carbs:    {summary['total_carbs']} g")
            print(f"   - Total Fat:      {summary['total_fat']} g")
            print(f"   - Target Calories: {summary['target_calories']} kcal")
            print(f"   - Calorie Variance: {summary['calorie_variance']} %")


# Collect user input
age = get_valid_integer("Enter your age: ", 15, 100)
height = get_valid_integer("Enter your height in cm: ", 50, 300)
weight = get_valid_integer("Enter your weight in kg: ", 10, 500)
gender = get_valid_gender()

assessment = ActivityAssessment()
responses = assessment.ask_user_questions()
activity_level = assessment.calculate_activity_level(responses)

user_wt_goal = get_weight_goal()
user_pref = get_prefs()
user_allergies = get_allergies()
# Creating user profile
user_profile = {
        'age': age,
        'gender': gender,
        'height': height,
        'weight': weight,
        'activity_level': activity_level,
        'weight_goal': user_wt_goal,
        'dietary_pref':user_pref,
        'allergies': user_allergies,
        }
print("Your final information after assessing the inputs\n")
print(f"Age:{age}")
print(f"Gender:{gender}")
print(f"Height:{height}")
print(f"Weight:{weight}")
print(f"Activity Level:{activity_level}")
print(f"Weight goal:{user_wt_goal}")

meal_plan, nutrition_summary = recommender.generate_meal_plan(user_profile)
display_meal_plan(meal_plan)

