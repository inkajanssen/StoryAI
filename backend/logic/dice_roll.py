import random

def roll_skill_check(ability_score, difficulty_class):
    """
    Simulates a DND 5e 1d20 skill check.
    :param ability_score: determines the modifier that is added to the roll
    :param difficulty_class: the difficulty of the action the char wants to do
    :return: The outcome as "SUCCESS" for success or "FAILURE" for failure,
             the d20 roll, modifier and the roll + modifier
    """
    modifier = max(0, (ability_score - 10) // 2)
    d20_roll = random.randint(1,20)
    result = d20_roll + modifier
    outcome = "SUCCESS" if result >= difficulty_class else "FAILURE"

    return outcome, d20_roll, modifier, result
