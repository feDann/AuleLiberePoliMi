import requests
from bs4 import BeautifulSoup
from pprint import pprint

URL = "https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do"
COLSPAN = 52
ROW_SKIP_AFTER_FLOOR = 3

# Return a dict with all the info about the classrooms for the day
def find_classrooms(location , day , month , year):
    info = {}
    params = {'csic': location , 'categoria' : 'tutte', 'tipologia' : 'tutte', 'giorno_day' : day , 'giorno_month' : month, 'giorno_year' : year , 'jaf_giorno_date_format' : 'dd%2FMM%2Fyyyy'  , 'evn_visualizza' : ''}
    r = requests.get(URL , params= params)
    soup = BeautifulSoup(r.text, 'html.parser')
    tableContainer = soup.find("div", {"id": "tableContainer"})
    tableRows = tableContainer.find_all('tr')[5:]
    return tableRows[0]




if __name__ == "__main__":
    pprint(find_classrooms('MIA' , 1 , 6 , 2021))