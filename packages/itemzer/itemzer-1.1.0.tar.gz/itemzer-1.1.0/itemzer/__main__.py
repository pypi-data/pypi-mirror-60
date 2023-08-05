 #! /usr/bin/env python3 

# import modules
from itemzer.get_items import GetItems
from itemzer.get_runes import GetRunes
from itemzer.get_skills_order import GetSkills
from itemzer.get_counter_champs import GetCounter

# import system
import sys


def main():
    try:
        GetItems(sys.argv[1]).get_items()
        GetRunes(sys.argv[1]).list_runes()
        GetSkills(sys.argv[1]).get_skills()
        GetCounter(sys.argv[1]).get_counter_strong()
    except AttributeError:
        print("Champion name unknown")
    except BaseException:
        print("Error during getting informations. Please try again")


if __name__ == "__main__":
    main()
