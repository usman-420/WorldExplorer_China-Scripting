# traveller_profile.py
# builds a profile by asking the user some questions
# the returned dict is used by the other functions

from WorldExplorer.config import PROFILES, BUDGETS, COMPANY, MOBILITY, MONTHS


def traveller_profile():
    """
    Asks the user a series of questions to build their travel profile.
    Returns a dict with all answers.
    """

    print("\n🌏 WorldExplorer - China")
    print("Let's figure out where you should go!\n")

    profile = {}

    profile["budget"]        = pick_one("What's your budget?", BUDGETS)
    profile["travel_months"] = pick_many("When are you planning to go?", MONTHS)
    profile["days"]          = pick_number("How many days are you travelling?")
    profile["interests"]     = pick_many("What kind of traveller are you? (pick one or more)", PROFILES)
    profile["company"]       = pick_one("Who are you going with?", COMPANY)
    profile["mobility"]      = pick_one("How do you want to get around?", MOBILITY)

    print("\nAlright, here's your profile:")
    for key, val in profile.items():
        print(f"  {key}: {val}")

    return profile


def pick_one(question, options):
    """lets the user pick one option from a list, keeps asking if input is wrong"""
    
    keys   = list(options.keys())   if isinstance(options, dict) else options
    labels = list(options.values()) if isinstance(options, dict) else options

    while True:
        print(f"\n{question}")
        for i, label in enumerate(labels, 1):
            print(f"  {i}. {label}")
        
        choice = input("Pick a number: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            return keys[int(choice) - 1]
        
        print("  not a valid option, try again")


def pick_many(question, options):
    """same as pick_one but allows multiple selections separated by commas"""

    keys   = list(options.keys())   if isinstance(options, dict) else options
    labels = list(options.values()) if isinstance(options, dict) else options

    while True:
        print(f"\n{question}")
        for i, label in enumerate(labels, 1):
            print(f"  {i}. {label}")

        choice = input("Pick one or more numbers (e.g. 1,3): ").strip()
        parts  = [p.strip() for p in choice.split(",")]

        result = []
        ok = True

        for p in parts:
            if p.isdigit() and 1 <= int(p) <= len(keys):
                result.append(keys[int(p) - 1])
            else:
                ok = False
                break

        if ok and result:
            return result

        print("  something went wrong, try again")


def pick_number(question, min_val=1, max_val=365):
    """asks for a number and validates it's within range"""

    while True:
        choice = input(f"\n{question} ({min_val}-{max_val}): ").strip()

        if choice.isdigit() and min_val <= int(choice) <= max_val:
            return int(choice)

        print(f"  please enter a number between {min_val} and {max_val}")