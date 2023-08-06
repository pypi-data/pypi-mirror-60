from collections import OrderedDict
from random import choice

import numpy

from personaednd.dice import Dice
from personaednd.ol import Ordo
from personaednd.sources import Classes, Feats, Races, Skills, Tools, Weapons


class ScoreAssigner:
    def __init__(self, _class: str, race: str, use_variant=False) -> None:
        # Full list of primary abilities.
        o = Ordo(
            Classes().get_primary_abilities(_class),
            data_type=None,
            sort=False,
            sort_reverse=False,
            allow_duplicates=False,
        )
        o.simul(Classes().get_saving_throws(_class))
        # Full list of abilities, excluding primary abilities.
        n = Ordo(
            [
                "Strength",
                "Dexterity",
                "Constitution",
                "Intelligence",
                "Wisdom",
                "Charisma",
            ],
            data_type=None,
            sort=False,
            sort_reverse=False,
            allow_duplicates=False,
        )
        n.excludere(o.get())
        raw_scores = list(self.roll_drop_lowest())
        ability_scores = OrderedDict()
        ability_scores["Strength"] = {}
        ability_scores["Dexterity"] = {}
        ability_scores["Constitution"] = {}
        ability_scores["Intelligence"] = {}
        ability_scores["Wisdom"] = {}
        ability_scores["Charisma"] = {}
        # Assign primary abilities.
        for selection in range(o.longitudinem()):
            value = max(raw_scores)
            raw_scores.remove(value)
            modifier = get_ability_modifier(value)
            ability_scores[o.arbitrium()] = {"Value": value, "Modifier": modifier}
        # Assign secondary abilities.
        for selection in range(n.longitudinem()):
            value = max(raw_scores)
            raw_scores.remove(value)
            modifier = get_ability_modifier(value)
            ability_scores[n.arbitrium()] = {"Value": value, "Modifier": modifier}
        # Apply racial bonus(es).
        bonuses = Races().get_racial_bonus(race, use_variant)
        for ability, values in ability_scores.items():
            if ability in bonuses:
                value = values["Value"] + bonuses[ability]
                value = value > 20 and 20 or value
                modifier = get_ability_modifier(value)
                ability_scores[ability] = {"Value": value, "Modifier": modifier}
        self.ability_scores = ability_scores

    @staticmethod
    def roll_drop_lowest(threshold=60) -> numpy.ndarray:
        """Returns six totaled results of 3(4) at threshold or higher."""
        die = Dice("d6", 4)
        results = numpy.array([], dtype=int)
        while results.sum() < threshold:
            for _ in range(1, 7):
                result = die.roll()
                excl_result = result.min(initial=None)
                ability_score = result.sum() - excl_result
                results = numpy.append(results, ability_score)
            score_total = results.sum()
            try:
                maximum_score = results.max(initial=None)
                minimum_score = results.min(initial=None)
            except ValueError:
                # Empty array, force re-roll.
                maximum_score = 14
                minimum_score = 7
            if score_total < threshold or maximum_score < 15 or minimum_score < 8:
                results = numpy.array([], dtype=int)
        return results


class ScoreImprovement:
    def __init__(
        self,
        _class: str,
        archetype: str,
        level: int,
        race: str,
        scores: OrderedDict,
        armor_proficiency: list,
        tool_proficiency: list,
        weapon_proficiency: list,
        languages: list,
        skills: list,
        feats: list,
    ) -> None:
        # Character data
        self._class = _class
        self.archetype = archetype
        self.level = level
        self.race = race
        self.ability_scores = scores
        self.armors = armor_proficiency
        self.tools = tool_proficiency
        self.weapons = weapon_proficiency
        self.languages = languages
        self.skills = skills
        self.feats = feats
        self.saving_throws = Classes().get_saving_throws(self._class)

    def _assign_features(self, feat) -> None:
        """Assign features by feat."""
        # Actor
        if feat == "Actor":
            self._assign_score("Charisma", 1)
        # Athlete/Lightly Armored/Moderately Armored/Weapon Master
        if feat in (
            "Athlete",
            "Lightly Armored",
            "Moderately Armored",
            "Weapon Master",
        ):
            ability_choice = choice(["Strength", "Dexterity"])
            self._assign_score(ability_choice, 1)
            if feat == "Lightly Armored":
                self.armors.append("Light")
            elif feat == "Moderately Armored":
                self.armors.append("Medium")
                self.armors.append("Shield")
        # Durable
        if feat == "Durable":
            self._assign_score("Constitution", 1)
        # Heavily Armored/Heavy Armor Master
        if feat in ("Heavily Armored", "Heavy Armor Master"):
            self._assign_score("Strength", 1)
            if feat == "Heavily Armored":
                self.armors.append("Heavy")
        # Keen Mind/Linguist
        if feat in ("Keen Mind", "Linguist"):
            self._assign_score("Intelligence", 1)
            if feat == "Linguist":
                # Remove already known languages.
                o = Ordo(
                    [
                        "Abyssal",
                        "Celestial",
                        "Common",
                        "Deep Speech",
                        "Draconic",
                        "Dwarvish",
                        "Elvish",
                        "Giant",
                        "Gnomish",
                        "Goblin",
                        "Halfling",
                        "Infernal",
                        "Orc",
                        "Primordial",
                        "Sylvan",
                        "Undercommon",
                    ],
                    data_type=None,
                    sort=False,
                    sort_reverse=False,
                    allow_duplicates=False,
                )
                o.excludere(self.languages)
                # Choose 3 bonus languages.
                for _ in range(3):
                    bonus_language = o.arbitrium()
                    self.languages.append(bonus_language)
        # Observant
        if feat == "Observant":
            if self._class in ("Cleric", "Druid"):
                self._assign_score("Wisdom", 1)
            elif self._class in ("Wizard",):
                self._assign_score("Intelligence", 1)
        # Resilient
        if feat == "Resilient":
            # Remove all proficient saving throws.
            o = Ordo(
                [
                    "Strength",
                    "Dexterity",
                    "Constitution",
                    "Intelligence",
                    "Wisdom",
                    "Charisma",
                ],
                data_type=None,
                sort=False,
                sort_reverse=False,
                allow_duplicates=False,
            )
            o.excludere(self.saving_throws)
            # Choose one non-proficient saving throw.
            ability_choice = o.arbitrium()
            if self.isadjustable(ability_choice, 1):
                self._assign_score(ability_choice, 1)
            self.saving_throws.append(ability_choice)
        # Skilled
        if feat == "Skilled":
            for _ in range(3):
                skilled_choice = choice(["Skill", "Tool"])
                if skilled_choice == "Skill":
                    o = Ordo(
                        Skills().get_skills(),
                        data_type=None,
                        sort=False,
                        sort_reverse=False,
                        allow_duplicates=False,
                    )
                    o.excludere(self.skills)
                    skill_choice = o.arbitrium()
                    self.skills.append(skill_choice)
                elif skilled_choice == "Tool":
                    o = Ordo(
                        Tools().get_tools(),
                        data_type=None,
                        sort=False,
                        sort_reverse=False,
                        allow_duplicates=False,
                    )
                    o.excludere(self.tools)
                    tool_choice = o.arbitrium()
                    self.tools.append(tool_choice)
        # Tavern Brawler
        if feat == "Tavern Brawler":
            self._assign_score(choice(["Strength", "Constitution"]), 1)
            self.weapons.append("Improvised weapons")
            self.weapons.append("Unarmed strikes")
        # Weapon Master
        if feat == "Weapon Master":
            o = Ordo(
                Weapons().get_martial_weapons(),
                data_type=None,
                sort=False,
                sort_reverse=False,
                allow_duplicates=False,
            )
            if "Simple" not in self.weapons:
                o.simul(Weapons().get_simple_weapons())
            for weapon in self.weapons:
                if weapon in ("Simple", "Martial"):
                    continue
                if weapon in o.get():
                    o.minuas(weapon)
            for _ in range(4):
                weapon = o.arbitrium()
                self.weapons.append(weapon)

    def _assign_score(self, ability_name: str, bonus: int) -> None:
        if self.isadjustable(ability_name, bonus):
            old = self.ability_scores[ability_name]["Value"]
            new = old + bonus
            self.ability_scores[ability_name]["Value"] = new
            self.ability_scores[ability_name]["Modifier"] = get_ability_modifier(new)

    def assign_feat(self) -> None:
        """Assigns a random valid feat."""
        o = Ordo(
            Feats().get_feats(),
            data_type=None,
            sort=False,
            sort_reverse=False,
            allow_duplicates=False,
        )
        o.excludere(self.feats)
        feat = o.arbitrium()
        has_required = False
        while True:
            if has_required:
                break
            while feat in self.feats:
                feat = o.arbitrium()
            while True:
                required_check = Feats().has_requirements(
                    feat=feat,
                    _class=self._class,
                    archetype=self.archetype,
                    level=self.level,
                    scores=self.ability_scores,
                    armor_proficiency=self.armors,
                    weapon_proficiency=self.weapons,
                )
                if required_check:
                    has_required = True
                    self.feats.append(feat)
                    break
                else:
                    feat = o.arbitrium()
        self._assign_features(feat)

    def assign_upgrade(self) -> None:
        """Assigns ability upgrades or a feat (if ability upgrade not applicable)."""
        bonus = choice([1, 2])
        o = Ordo(
            Classes().get_primary_abilities(self._class),
            data_type=None,
            sort=False,
            sort_reverse=False,
            allow_duplicates=False,
        )
        o.simul(Classes().get_saving_throws(self._class))
        num_of_adjustments = bonus is 1 and 2 or 1
        ability_selections = list()
        # Select bonus ability(ies).
        for _ in range(num_of_adjustments):
            ability_selections.append(o.arbitrium())
        # Apply ability upgrade or feat if not applicable.
        for ability in ability_selections:
            if self.isadjustable(ability, bonus):
                self._assign_score(ability, bonus)
            else:
                self.assign_feat()

    def isadjustable(self, ability, bonus) -> bool:
        """Checks if ability is lt or eq to 20 with bonus."""
        score = self.ability_scores[ability]["Value"] + bonus
        return score <= 20 and True or False


def get_ability_modifier(score) -> int:
    """Returns ability modifier by score."""
    return score is not 0 and int((score - 10) / 2) or 0
