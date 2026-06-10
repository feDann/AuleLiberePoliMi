from logging import root
import requests
import requests_cache
import time as time_module
import logging
from bs4 import BeautifulSoup
import json

requests_cache.install_cache('polimi_cache', expire_after=3600)

URL = "https://onlineservices.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do"
BASE_URL = "https://onlineservices.polimi.it/spazi/spazi/controller/"
BUILDING = 'innerEdificio'
ROOM = 'dove'
LECTURE = 'slot'
TIME_SHIFT = 0.25
MIN_TIME = 8
MAX_TIME = 20

GARBAGE = ["PROVA_ASICT" , "2.2.1-D.I."]



def clean_data(infos):
    """Filters out non-existent or unreachable rooms from the occupancy data.

    Args:
        infos (dict): The dictionary containing classroom occupancy information.

    Returns:
        dict: The cleaned dictionary with invalid rooms removed.
    """
    for building in infos:
        for room in GARBAGE:
            if room in infos[building]:
                del infos[building][room]          
            
    return infos


def find_classrooms(location , day , month , year):
    """Retrieves classroom information for a specific date and location.

    Makes a GET request to the Politecnico di Milano online services and parses
    the HTML response to extract room occupancy data.

    Args:
        location (str): The campus location code (e.g., 'MIA').
        day (int): The day of the month.
        month (int): The month (1-12).
        year (int): The year (YYYY).

    Returns:
        dict: A dictionary containing structured information about classrooms and their schedules.
    """
    info = {} 
    buildingName = '-' #defaul value for building
    info[buildingName] = {} #first initialization due to table format

    params = {'csic': location , 'categoria' : 'tutte', 'tipologia' : 'tutte', 'giorno_day' : day , 'giorno_month' : month, 'giorno_year' : year , 'jaf_giorno_date_format' : 'dd%2FMM%2Fyyyy'  , 'evn_visualizza' : ''}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    start_time = time_module.time()
    r = requests.get(URL , params= params, headers=headers)
    elapsed_time = time_module.time() - start_time
    
    cache_status = "HIT" if getattr(r, 'from_cache', False) else "MISS"
    logging.info(f"PoliMi Request: {elapsed_time:.2f}s | Cache: {cache_status}")
    
    if r.status_code != 200:
        print(f"Error: Failed to fetch data. Status code: {r.status_code}")
        return {}
    
    soup = BeautifulSoup(r.text, 'html.parser')
    soup = BeautifulSoup(r.text, 'html.parser')
    tableContainer = soup.find("div", {"id": "tableContainer"})
    if not tableContainer:
         print(f"Error: Table container not found. Response content length: {len(r.text)}")
         return {}
    tableRows = tableContainer.find_all('tr')[3:] #remove first three headers

    with open("json/roomsWithPower.json","r") as j:
        rwp = set(json.load(j))

    for row in tableRows:
        tds = row.find_all('td')
        if 'class' not in row.attrs:
            if BUILDING in tds[0].attrs['class']:
                buildingName = tds[0].string
                try:
                    # buildingName = re.search('(Edificio.*)' , buildingName).group(1) #take only the building name
                    buildingName = buildingName.split('-')[2]
                except:
                    print(buildingName)
                if buildingName not in info:
                    info[buildingName] = {}
        else:
            room = ''
            time = 7.75
            for td in tds:
                if ROOM in td.attrs['class']:
                    room = td.find('a').string.replace(" ","")
                    link = td.find('a')['href']
                    id_aula = int(link.split("=")[-1])
                    
                    if room not in info[buildingName]:
                        info[buildingName][room] = {}
                        info[buildingName][room]['link'] = BASE_URL + link
                        info[buildingName][room]['lessons'] = []
                        info[buildingName][room]['powerPlugs'] = id_aula in rwp

                elif LECTURE in td.attrs['class'] and room != '':
                    duration = int(td.attrs['colspan'])
                    lesson_name = td.find('a').string
                    lesson = {}
                    lesson['name'] = lesson_name
                    lesson['from'] = time
                    time += duration/4
                    lesson['to'] = time
                    info[buildingName][room]['lessons'].append(lesson)
                else:
                    time += TIME_SHIFT
    return clean_data(info)




if __name__ == "__main__":
    infos =  find_classrooms('MIA' , 25 , 10 , 2021)
    with open('json/infos_a.json' , 'w') as outfile:
        json.dump(infos , outfile, indent=3)