from itemzer.request_page import make_bs4_element


class GetCounter:

    def __init__(self, name):
        self.name = name
        self.url = f"https://lolcounter.com/champions/{self.name}"

    def get_counter(self):
        list_champs = []
        get = make_bs4_element(self.url).find("div", class_="weak-block")

        # Get all counter champs but display only 5 champs
        for champs in get.find_all('div', class_="name"):
            list_champs.append(champs.text)
        return u"\u001b[36m%s\u001b[0m is weak against : \u001b[31m%s\u001b[0m " % (self.name.capitalize(), ", ".join(list_champs[:5]))

    def get_strong(self):
        list_champs = []
        get = make_bs4_element(self.url).find("div", class_="strong-block")

        for champs in get.find_all('div', class_='name'):
            list_champs.append(champs.text)
        return f"\u001b[36m{self.name.capitalize()}\u001b[0m is strong against : \u001b[32m%s\u001b[0m" % ", ".join(list_champs[:5])

    def get_counter_strong(self):
        print("\n\u001b[31m === COUNTER & STRONGER ===\u001b[0m")
        print(self.get_counter())
        print(self.get_strong())
