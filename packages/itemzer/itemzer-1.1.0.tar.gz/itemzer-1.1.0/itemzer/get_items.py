from itemzer.request_page import make_bs4_element


class GetItems:

	def __init__(self, name):
		self.name = name
		self.url = f"https://champion.gg/champion/{self.name}"

	def get_items(self):
		list_items = []
		items = make_bs4_element(self.url).find("div", class_="build-wrapper")

		for lien in items.find_all('a', href=True):
			list_items.append(lien['href'].split('/')[-1])
		item_index = 1
		print("\u001b[31m === ITEMS ===")

		for value_item in list_items:
			print(f"\u001b[32m{item_index}\u001b[0m: \u001b[36m{value_item}\u001b[0m")
			item_index += 1
