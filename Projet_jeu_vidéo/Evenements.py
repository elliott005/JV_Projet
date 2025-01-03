class Evenements:
    def __init__(self, save_id) -> None:
        if save_id == 0:
            self.quests = {
                "parlerPotato": {"progress": 0, "end": 2, "endFunc": self.parlerPotatoEnd},
            }
            self.questItems = {
            }
        else:
            self.quests = {
                "parlerPotato": {"progress": 0, "end": 2},
                "sauverPoule": {"progress": 0, "end": 6, "endFunc": self.sauverPouleEnd},
                "parlerPotatoEncore": {"progress": 0, "end": 3}
            }
            self.questItems = {
                "poule": "sauverPoule"
            }

        self.dialoguesProgression = {}
    
    def sauverPouleEnd(self, mapjeu, joueur):
        mapjeu.addItem(2, (200, 100), "coin", "Coin2.png::0::0;0", animated="Coin2.png::0::0;0")
        joueur.items["poule"] = joueur.items["poule"][4:]
    
    def parlerPotatoEnd(self, mapjeu, joueur):
        joueur.code = "1111"

    def progressQuest(self, p_type, name, mapjeu, joueur):
        attr = getattr(self, p_type)
        if attr[name]["progress"] < attr[name]["end"]:
            attr[name]["progress"] += 1
            if attr[name]["progress"] == attr[name]["end"] and "endFunc" in attr[name]:
                attr[name]["endFunc"](mapjeu, joueur)