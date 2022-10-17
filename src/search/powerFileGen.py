import re
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www7.ceda.polimi.it/spazi/spazi/controller/RicercaAula.do?spazi___model___formbean___RicercaAvanzataAuleVO___postBack=true&spazi___model___formbean___RicercaAvanzataAuleVO___formMode=FILTER&spazi___model___formbean___RicercaAvanzataAuleVO___sede=tutte&spazi___model___formbean___RicercaAvanzataAuleVO___sigla=&spazi___model___formbean___RicercaAvanzataAuleVO___categoriaScelta=tutte&spazi___model___formbean___RicercaAvanzataAuleVO___tipologiaScelta=tutte&spazi___model___formbean___RicercaAvanzataAuleVO___iddipScelto=tutti&spazi___model___formbean___RicercaAvanzataAuleVO___soloPreseElettriche=S&spazi___model___formbean___RicercaAvanzataAuleVO___soloPreseElettriche_default=N&spazi___model___formbean___RicercaAvanzataAuleVO___soloPreseDiRete_default=N&evn_ricerca_avanzata=Ricerca aula"

"""
Since having to call poli for each room every time to check if there are power outlets takes a lot of time
the idea is to create this little script that does it once and generates a json file
that can be opened and checked by the bot in constant time. Of course this won't be updated live but
we don't add and remove power outlets to rooms every day, so launching this script every now and then is more than fine.
"""

r = requests.get(URL)
soup = BeautifulSoup(r.text, 'html.parser')
tableContainer = soup.find("tbody", {"class": "TableDati-tbody"})
tableRows = tableContainer.find_all('tr')

roomsWithPower = []

for row in tableRows:
    link = row.find_all('td')[2]
    id_aula = int(re.findall("idaula=(\d+)&",link.find("a")['href'])[0])
    roomsWithPower.append(id_aula)

json.dump(roomsWithPower,open("../json/roomsWithPower.json","w"),indent=3)
