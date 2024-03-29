import requests
from bs4 import BeautifulSoup

r = requests.get("https://www.cdc.gov/disasters/volcanoes/facts.html")
soup = BeautifulSoup(r.text, "html.parser")
t = " ".join(soup.text.split())
print(t)