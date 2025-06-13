def get_score(prompt, options):
    print(prompt)
    for i, (label, _) in enumerate(options, 1):
        print(f"{i}. {label}")
    while True:
        try:
            choice = int(input("Enter your choice (1-{}): ".format(len(options))))
            if 1 <= choice <= len(options):
                return options[choice - 1][1]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")

def main():
    total_score = 0

    print("\n--- Section 1: Daily Lifestyle ---")

    total_score += get_score(
        "\n1. What best describes your daily routine?",
        [("Sit most of the day", 0),
         ("Move a bit (light walking, standing work)", 1),
         ("On my feet most of the day", 2),
         ("Physically demanding work", 3)]
    )

    total_score += get_score(
        "\n2. How often do you take the stairs or walk (outside of workouts)?",
        [("Rarely or never", 0),
         ("A few times a week", 1),
         ("Daily for short distances", 2),
         ("Daily and regularly (15+ minutes)", 3)]
    )

    print("\n--- Section 2: Exercise Habits ---")

    total_score += get_score(
        "\n3. How many days per week do you exercise?",
        [("None", 0),
         ("1–2 days", 1),
         ("3–5 days", 2),
         ("6–7 days", 3)]
    )

    total_score += get_score(
        "\n4. What is the usual intensity of your workouts?",
        [("Light (e.g., walking, stretching)", 0),
         ("Moderate (brisk walk, casual biking)", 1),
         ("Vigorous (running, lifting, sports)", 2),
         ("Mixed (some moderate & vigorous)", 2)]
    )

    total_score += get_score(
        "\n5. On a typical workout day, how long do you exercise?",
        [("Less than 30 minutes", 0),
         ("30–60 minutes", 1),
         ("More than 60 minutes", 2)]
    )

    print("\n--- Section 3: IPAQ Questions ---")

    total_score += get_score(
        "\n6. Days with vigorous physical activity (e.g., running, HIIT)?",
        [("0 days", 0),
         ("1–2 days", 1),
         ("3–4 days", 2),
         ("5+ days", 3)]
    )

    total_score += get_score(
        "\n7. Duration of vigorous activity on those days?",
        [("None", 0),
         ("<30 minutes", 1),
         ("30–60 minutes", 2),
         ("60+ minutes", 3)]
    )

    total_score += get_score(
        "\n8. Days with moderate activity (e.g., brisk walking)?",
        [("0 days", 0),
         ("1–2 days", 1),
         ("3–4 days", 2),
         ("5+ days", 3)]
    )

    total_score += get_score(
        "\n9. Duration of moderate activity on those days?",
        [("None", 0),
         ("<30 minutes", 1),
         ("30–60 minutes", 2),
         ("60+ minutes", 3)]
    )

    total_score += get_score(
        "\n10. How many days did you walk at least 10 minutes at a time?",
        [("0 days", 0),
         ("1–2 days", 1),
         ("3–5 days", 2),
         ("6–7 days", 3)]
    )

    total_score += get_score(
        "\n11. How many hours per day do you spend sitting?",
        [("10+ hours", 0),
         ("7–9 hours", 1),
         ("4–6 hours", 2),
         ("Less than 4 hours", 3)]
    )

    print(f"\nTotal Activity Score: {total_score}/33")

    if total_score <= 7:
        level = "sedentary"
        pal = 1.2
    elif total_score <= 14:
        level = "lightly_active"
        pal = 1.375
    elif total_score <= 23:
        level = "moderately_active"
        pal = 1.55
    else:
        level = "very_active"
        pal = 1.725

    print(f"\n💪 Your Activity Level: {level}")
    print(f"📈 Suggested PAL Multiplier for TDEE: {pal}")

if __name__ == "__main__":
    main()
