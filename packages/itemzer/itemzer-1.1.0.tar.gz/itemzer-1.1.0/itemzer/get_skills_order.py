from itemzer.request_page import make_bs4_element


class GetSkills:

	def __init__(self, name):
		self.name = name
		self.url = f"http://www.op.gg/champion/{self.name}/statistics/top"

	def get_skills(self):
		counter_skills = 1
		get = make_bs4_element(self.url).find('table', class_='champion-skill-build__table')
		get_table = get.find_all('td')
		list_skills = [value.text.replace('\t', '').replace('\n', '') for value in get_table]

		print("\u001b[31m === FIRST 3 SKILLS === ")
		for value in list_skills[:3]:
			print(f"\u001b[32m{counter_skills}\u001b[0m:\u001b[36m{value}\u001b[0m", end=" ")

			counter_skills += 1
