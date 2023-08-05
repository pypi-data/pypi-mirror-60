import requests
from bs4 import BeautifulSoup as bs


def make_request(url):
	request = requests.get(url).content
	return request


def make_bs4_element(url):
	element = bs(make_request(url), 'html.parser')
	return element

