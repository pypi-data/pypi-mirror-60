from random import choice

from personaednd.ol import Ordo
from personaednd.sources.reader import Reader


class Backgrounds(Reader):
    def __init__(self) -> None:
        super().__init__("backgrounds")

    def get_backgrounds(self) -> tuple:
        """Returns a tuple of available backgrounds."""
        return tuple(self.find().keys())

    def get_background_equipment(self, background) -> list:
        """Returns a list of bonus equipment by background."""
        return self.find([background, "equipment"])

    def get_background_languages(self, background) -> int:
        """Returns a count of bonus languages by background."""
        return self.find([background, "languages"])

    def get_background_skills(self, background) -> list:
        """Returns a list of bonus skills by background."""
        return self.find([background, "skills"])

    def get_background_tools(self, background) -> list:
        """Returns a list of bonus tool proficiencies by background."""
        background_tools = list()
        for tool in self.find([background, "tool_proficiency"]):
            if Tools().has_sub_tools(tool):
                sub_tool = choice(Tools().get_sub_tools(tool))
                background_tools.append("{}: {}".format(tool, sub_tool))
            else:
                background_tools.append(tool)
        return background_tools


class Classes(Reader):
    def __init__(self) -> None:
        super().__init__("classes")

    def get_archetypes(self, _class) -> list:
        """Returns a list of archetypes by class."""
        return self.find([_class, "archetypes"])

    def get_class_armor_proficiency(self, _class) -> list:
        """Returns a list of armor proficiencies by class."""
        return self.find([_class, "armor_proficiency"])

    def get_class_default_background(self, _class) -> str:
        """Returns default class background by class."""
        return self.find([_class, "background"])

    def get_class_primary_abilities(self, _class) -> dict:
        """Returns a dict of primary abilities by class."""
        return self.find([_class, "primary_abilities"])

    def get_class_tool_proficiency(self, _class) -> list:
        """Returns a list of tool proficiencies by class."""
        if _class == "Monk":
            return [
                choice(Tools().get_tools(["Artisan's tools", "Musical instrument"]))
            ]
        else:
            return self.find([_class, "tool_proficiency"])

    def get_class_weapon_proficiency(self, _class) -> list:
        """Returns a list of weapon proficiencies by class."""
        return self.find([_class, "weapon_proficiency"])

    def get_classes(self) -> tuple:
        """Returns a tuple of available classes."""
        return tuple(self.find().keys())

    def get_hit_die(self, _class) -> int:
        """Returns a hit die integer value by class."""
        return self.find([_class, "hit_die"])

    def get_saving_throws(self, _class) -> list:
        """Returns a list of saving throws by class."""
        return self.find([_class, "saving_throws"])

    def get_spell_slots(self, _class, level, archetype=None) -> str:
        """Returns spell slots by class, level and archetype."""
        try:
            if _class == "Fighter" and archetype != "Eldritch Knight":
                raise KeyError
            elif _class == "Rogue" and archetype != "Arcane Trickster":
                raise KeyError
            else:
                spell_slots = self.find([_class, "spell_slots", level])
                if len(spell_slots) is not 0:
                    return spell_slots
                else:
                    raise KeyError
        except KeyError:
            return ""


class Feats(Reader):
    def __init__(self) -> None:
        super().__init__("feats")

    def get_ability_requirements(self, feat) -> dict:
        """Returns ALL ability score requirements for feat."""
        requirements = {}
        strength = self.find([feat, "strength"])
        if strength > 1:
            requirements["Strength"] = strength
        dexterity = self.find([feat, "dexterity"])
        if dexterity > 1:
            requirements["Dexterity"] = dexterity
        constitution = self.find([feat, "constitution"])
        if constitution > 1:
            requirements["Constitution"] = constitution
        intelligence = self.find([feat, "intelligence"])
        if intelligence > 1:
            requirements["Intelligence"] = intelligence
        wisdom = self.find([feat, "wisdom"])
        if wisdom > 1:
            requirements["Wisdom"] = wisdom
        charisma = self.find([feat, "charisma"])
        if charisma > 1:
            requirements["Charisma"] = charisma
        return requirements

    def get_caster_requirement(self, feat) -> dict:
        """Returns caster requirements for feat."""
        return self.find([feat, "caster"])

    def get_feats(self) -> list:
        """Returns a list of feats."""
        return list(self.find().keys())

    def get_proficiency_requirement(self, feat) -> tuple:
        """Returns a tuple of proficiency requirements for feat."""
        return tuple(self.find([feat, "proficiency"]))

    def has_requirements(
        self,
        feat,
        _class,
        archetype,
        level,
        scores,
        armor_proficiency,
        weapon_proficiency,
    ) -> bool:
        """Checks if all requirements for feat are met."""
        if (
            feat in ("Heavily Armored", "Lightly Armored", "Moderately Armored",)
            and _class == "Monk"
        ):
            return False
        elif feat in (
            "Heavily Armored",
            "Lightly Armored",
            "Moderately Armored",
            "Weapon Master",
        ):
            # Character already has heavy armor proficiency.
            if feat == "Heavily Armored" and "Heavy" in armor_proficiency:
                return False
            # Character already has light armor proficiency.
            if feat == "Lightly Armored" and "Light" in armor_proficiency:
                return False
            # Character already has medium armor proficiency.
            if feat == "Moderately Armored" and "Medium" in armor_proficiency:
                return False
            # Character already has martial weapon proficiency.
            if feat == "Weapon Master" and "Martial" in weapon_proficiency:
                return False
        elif feat == "Magic Initiative" and _class not in (
            "Bard",
            "Cleric",
            "Druid",
            "Sorcerer",
            "Warlock",
            "Wizard",
        ):
            return False
        proficiency = self.get_proficiency_requirement(feat)
        proficiencies = armor_proficiency + weapon_proficiency
        if len(proficiency) is not 0 and proficiency not in proficiencies:
            return False
        if self.get_caster_requirement(feat) and not is_caster(
            _class, level, archetype
        ):
            return False
        for name, value in self.get_ability_requirements(feat).items():
            my_value = scores[name]["Value"]
            if feat == "Ritual Caster":
                if my_value >= value:
                    return True
            else:
                if my_value < value:
                    return False
        return True


class Races(Reader):
    def __init__(self) -> None:
        super().__init__("races")

    def get_languages(self, race, background) -> list:
        """Returns a list of languages by race and background."""
        languages = self.find([race, "languages"])
        # Remove duplicate languages.
        o = Ordo(
            ["Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", "Halfling", "Orc"],
            data_type=None,
            sort=False,
            sort_reverse=False,
            allow_duplicates=False,
        )
        o.excludere(languages)
        # Add racial bonus language, if applicable.
        if race in ("Elf, High", "Half-elf", "Human"):
            languages.append(o.arbitrium())
        # Add background bonus language(s).
        background_languages = Backgrounds().get_background_languages(background)
        if background_languages > 0:
            for _ in range(background_languages):
                languages.append(o.arbitrium())
        languages.sort()
        return languages

    def get_races(self) -> tuple:
        """Returns a tuple of available races."""
        return tuple(self.find().keys())

    def get_racial_armor_proficiency(self, race) -> list:
        """Returns a list of armor proficiencies by race."""
        return self.find([race, "armor_proficiency"])

    def get_racial_bonus(self, race, use_variant=False) -> dict:
        """Returns a dictionary of ability bonuses by race."""
        ability = self.find([race])
        bonuses = {}
        if ability["strength"] is not 0:
            bonuses["Strength"] = ability["strength"]
        if ability["dexterity"] is not 0:
            bonuses["Dexterity"] = ability["dexterity"]
        if ability["constitution"] is not 0:
            bonuses["Constitution"] = ability["constitution"]
        if ability["intelligence"] is not 0:
            bonuses["Intelligence"] = ability["intelligence"]
        if ability["wisdom"] is not 0:
            bonuses["Wisdom"] = ability["wisdom"]
        if ability["charisma"] is not 0:
            bonuses["Charisma"] = ability["charisma"]
        # Half-elf or Human w/ variant rule.
        if race == "Half-elf" or race == "Human" and use_variant:
            abilities = [
                "Strength",
                "Dexterity",
                "Constitution",
                "Intelligence",
                "Wisdom",
                "Charisma",
            ]
            for x in range(0, 2):
                ability = None
                if race == "Half-elf":
                    ability = choice(abilities)
                if race == "Human":
                    ability = choice(abilities)
                bonuses[ability] = 1
        # Human w/o variant rule.
        elif race == "Human":
            bonuses["Strength"] = 1
            bonuses["Dexterity"] = 1
            bonuses["Constitution"] = 1
            bonuses["Intelligence"] = 1
            bonuses["Wisdom"] = 1
            bonuses["Charisma"] = 1
        return bonuses

    def get_racial_tool_proficiency(self, race) -> list:
        """Returns a list of tool proficiencies by race."""
        racial_tools = self.find([race, "tool_proficiency"])
        if race in ("Dwarf", "Dwarf, Hill", "Dwarf, Mountain"):
            return [choice(racial_tools)]
        return racial_tools

    def get_racial_weapon_proficiency(self, race) -> list:
        """Returns a list of weapon proficiencies by race."""
        return self.find([race, "weapon_proficiency"])


class Skills(Reader):
    def __init__(self) -> None:
        super().__init__("skills")

    def get_class_skills(self, _class) -> list:
        """Returns ALL skills by class."""
        skill_list = list()
        for name in list(self.find().keys()):
            if _class in self.get_proficient_classes(name):
                skill_list.append(name)
        return skill_list

    def get_proficient_classes(self, skill) -> tuple:
        """Returns a tuple of ALL proficient classes by skill."""
        return tuple(self.find([skill, "classes"]))

    def get_skill_ability(self, skill) -> str:
        """Returns a skill's associated ability name by skill."""
        return self.find([skill, "ability"])

    def get_skills(self) -> list:
        """Returns ALL skills."""
        return list(self.find().keys())

    def select_skills(self, race, background, _class) -> list:
        """Randomly selects skills based upon race, background and class."""
        skills = list()
        # Add racial skills first.
        if race in ("Elf", "Elf, Drow", "Elf, High", "Elf, Wood", "Half-orc"):
            if race == "Half-orc":
                racial_skill = "Intimidation"
            else:
                racial_skill = "Perception"
            skills.append(racial_skill)
            # print("select_skills: racial skill -> {} ({})".format(racial_skill, race))
        elif race == "Half-elf":
            o = Ordo(
                self.get_skills(),
                data_type=None,
                sort=False,
                sort_reverse=False,
                allow_duplicates=False,
            )
            for _ in range(2):
                racial_skill = o.arbitrium()
                skills.append(racial_skill)
                """
                print(
                    "select_skills: racial skill -> {} ({})".format(racial_skill, race)
                )
                """
        # Next, add background skills.
        background_skills = Backgrounds().get_background_skills(background)
        if len(background_skills) is not 0:
            for background_skill in background_skills:
                if background_skill not in skills:
                    skills.append(background_skill)
                    """
                    print(
                        "select_skills: background skill -> {} ({})".format(
                            background_skill, background
                        )
                    )
                    """
        # Finally, choose class skills.
        for _ in range(get_skill_allotment(_class)):
            o = Ordo(
                self.get_class_skills(_class),
                data_type=None,
                sort=False,
                sort_reverse=False,
                allow_duplicates=False,
            )
            o.excludere(skills)
            class_skill = o.arbitrium()
            skills.append(class_skill)
        skills.sort()
        return skills


class Tools(Reader):
    def __init__(self) -> None:
        super().__init__("tools")

    def get_main_tools(self) -> tuple:
        """Returns a tuple of all main level tools."""
        return tuple(self.find().keys())

    def get_sub_tools(self, tool) -> tuple:
        """Return a tuple of sub level tools for a tool."""
        tools = tuple(self.find([tool]))
        if len(tools) > 0:
            return tools
        return tuple()

    def get_tools(self, main_tools=None) -> list:
        """Returns a tuple of ALL tools or main tools, if applicable."""
        tools = list()
        if isinstance(main_tools, (list, tuple)):
            for tool in main_tools:
                if not self.has_sub_tools(tool):
                    continue
                for sub_tool in self.get_sub_tools(tool):
                    tools.append("{}: {}".format(tool, sub_tool))
        else:
            for tool in list(self.get_main_tools()):
                if self.has_sub_tools(tool):
                    for sub_tool in self.get_sub_tools(tool):
                        tools.append("{}: {}".format(tool, sub_tool))
                else:
                    tools.append(tool)
        tools.sort()
        return tools

    def has_sub_tools(self, tool) -> bool:
        """Checks if a tool has sub level tools."""
        if len(self.get_sub_tools(tool)) is 0:
            return False
        return True


class Weapons(Reader):
    def __init__(self) -> None:
        super().__init__("weapons")

    def get_martial_weapons(self) -> list:
        """Returns a list of martial weapons."""
        return self.find(["Martial"])

    def get_simple_weapons(self) -> list:
        """Returns a list of simple weapons."""
        return self.find(["Simple"])


def get_ability_modifier(scores, ability) -> int:
    """Returns ability modifier value from dictionary of abilities."""
    return scores[ability]["Modifier"]


def get_skill_allotment(_class) -> int:
    """Returns allotment value of skills by class."""
    if _class in ("Rogue",):
        num_of_skills = 4
    elif _class in ("Bard", "Ranger"):
        num_of_skills = 3
    else:
        num_of_skills = 2
    return num_of_skills


def get_allotted_feats(_class, level=1) -> int:
    """Returns allotment value of feats by class and level."""
    num_of_feats = 0
    for _ in range(1, level + 1):
        if (_ % 4) == 0 and _ is not 20:
            num_of_feats += 1
    if _class == "Fighter" and level >= 6:
        num_of_feats += 1
    if _class == "Rogue" and level >= 8:
        num_of_feats += 1
    if _class == "Fighter" and level >= 14:
        num_of_feats += 1
    if level >= 19:
        num_of_feats += 1
    return num_of_feats


def get_proficiency(proficiency, _race, _class) -> list:
    proficiency_list = {
        "armors": {
            "class": Classes().get_class_armor_proficiency(_class),
            "racial": Races().get_racial_armor_proficiency(_race),
        },
        "tools": {
            "class": Classes().get_class_tool_proficiency(_class),
            "racial": Races().get_racial_tool_proficiency(_race),
        },
        "weapons": {
            "class": Classes().get_class_weapon_proficiency(_class),
            "racial": Races().get_racial_weapon_proficiency(_race),
        },
    }
    try:
        proficiencies = proficiency_list[proficiency]["racial"]
        proficiencies += proficiency_list[proficiency]["class"]
        proficiencies = list(dict.fromkeys(proficiencies))
        proficiencies.sort()
        return proficiencies
    except KeyError:
        return list()


def get_proficiency_bonus(level=1) -> int:
    """Returns a proficiency bonus value by level."""
    if level in range(1, 5):
        proficiency_bonus = 2
    elif level in range(5, 9):
        proficiency_bonus = 3
    elif level in range(9, 13):
        proficiency_bonus = 4
    elif level in range(13, 17):
        proficiency_bonus = 5
    else:
        proficiency_bonus = 6
    return proficiency_bonus


def is_caster(_class, level, archetype=None) -> bool:
    """Returns True if caster by _class, level, archetype or False if not."""
    if _class in ("Bard", "Cleric", "Druid", "Sorcerer", "Warlock", "Wizard"):
        return True
    elif _class in ("Paladin", "Ranger") and level > 1:
        return True
    elif _class is "Fighter" and archetype in ("Eldritch Knight",):
        return True
    elif _class is "Rogue" and archetype in ("Arcane Trickster",):
        return True
    else:
        return False
