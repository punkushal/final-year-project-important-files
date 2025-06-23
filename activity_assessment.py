class ActivityAssessment:
    '''
    Determines user's activity level through research-based questionnaire
    '''
    def __init__(self):
        self.questions = [
            {
                'id': 1,
                'question': 'How many days per week do you engage in planned exercise or sports?',
                'options': {
                    'a': '0 days (None)',
                    'b': '1-2 days (Light)', 
                    'c': '3-4 days (Moderate)',
                    'd': '5+ days (High)'
                },
               'weight': 3 #Most important factor 
            },
            {
                'id': 2,
                'question': 'How would you describe your typical work day?',
                'options': {
                    'a': 'Mostly sitting (desk job, driving)',
                    'b': 'Some walking, mostly sitting',
                    'c': 'Regular walking, some physical tasks',
                    'd': 'Mostly standing, walking, or physical labor'
                },
                'weight': 2
            },
            {
                'id': 3,
                'question': 'On average, how many hours of moderate to vigorous exercise do you do per week?',
                'options': {
                    'a': 'Less than 1 hour',
                    'b': '1-3 hours',
                    'c': '4-6 hours', 
                    'd': 'More than 6 hours'
                },
                'weight': 3  
            },
            {

                'id': 4,
                'question': 'How many flights of stairs do you climb per day on average?',
                'options': {
                    'a': '0-2 flights',
                    'b': '3-5 flights',
                    'c': '6-10 flights',
                    'd': 'More than 10 flights'
                },
                'weight': 1
            },
            {
                'id': 5,
                'question': 'How do you usually commute or travel for daily activities?',
                'options': {
                    'a': 'Car, bus, or other transport (mostly sitting)',
                    'b': 'Mix of transport and walking',
                    'c': 'Walking or cycling for short distances',
                    'd': 'Mostly walking or cycling'
                },
                'weight': 1
            },
            {
                'id': 6,
                'question': 'During leisure time, you typically prefer:',
                'options': {
                    'a': 'Sedentary activities (TV, reading, computer)',
                    'b': 'Light activities (shopping, cooking, casual walks)',
                    'c': 'Active hobbies (gardening, dancing, recreational sports)',
                    'd': 'Intense activities (competitive sports, hiking, gym)'
                },
                'weight': 2 
            },
            {
                'id': 7,
                'question': 'How often do you feel physically tired at the end of the day due to physical activity?',
                'options': {
                    'a': 'Rarely (mostly sedentary)',
                    'b': 'Sometimes (light activity)',
                    'c': 'Often (moderate activity)',
                    'd': 'Very often (high activity level)'
                },
                'weight': 1 
            }
        ]

    def calculate_activity_level(self, responses:list[str]):
        '''
        Calculate activity level based on weighted questionnaire responses
        '''
        score_map = {
                'a':1,
                'b':2,
                'c':3,
                'd':4
                }
        total_score = 0
        total_wt = 0

        for i, response in enumerate(responses):
            if i < len(self.questions):
                question_wt = self.questions[i]['weight']
                score = score_map.get(response, 1) * question_wt
                total_score += score
                total_wt += question_wt

        weighted_average = total_score / total_wt if total_wt > 0 else 1

        #Classify activity level based on weighted average
        if weighted_average <=1.5:
            return 'sedentary'
        elif weighted_average <=2.5:
            return 'lightly_active'

        elif weighted_average <=3.2:
            return 'moderately_active'
        else:
            return 'very_active'

    def ask_user_questions(self):
        '''
        Ask the user questions and collect responses
        '''
        responses = []

        print("Please answer the following questions to assess your activity level.\n")

        for q in self.questions:
            print(f"Q{q['id']}. {q['question']}")
            for key, option in q['options'].items():
                print(f"   {key}) {option}")

            while True:
                user_input = input("Your answer (a/b/c/d): ").strip().lower()
                if user_input in q['options']:
                    responses.append(user_input)
                    break
                else:
                    print("Invalid choice. Please enter a, b, c, or d.")

        return responses