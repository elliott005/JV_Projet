dialogues = {
    "blep": {
        "evenements": {
            1: {"type": "quests", "nom": "parlerPotato", "min": 0, "max": 1},
        },
        "restrictions": {
            2: {"type": "quests", "nom": "parlerPotato", "min": 2, "max": -1},
        },
        "texte": [
            ["dialogue different!!!"],
            ["Va parler a Potato, parce-que pourquoi pas.", "Il est dans la caverne."],
            ["Tu peux voir ton inventaire avec TAB"],
            ["Bravo!!! Tu as fini le tutoriel!"],
            ["salut!"]
        ]
    },
    "potato": {
        "evenements": {
            1: {"type": "quests", "nom": "parlerPotato", "min": 1, "max": -1},
        },
        "restrictions": {
            1: {"type": "quests", "nom": "parlerPotato", "min": 1, "max": 2},
        },
        "texte": [
            ["Salut!"],
            ["Blep t'as demandé de venir me parler!?"],
            ["POTATO!!!!"]
        ]
    }
}