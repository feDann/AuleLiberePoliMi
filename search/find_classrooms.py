from logging import root
import requests
from bs4 import BeautifulSoup
import json

URL = "https://www7.ceda.polimi.it/spazi/spazi/controller/OccupazioniGiornoEsatto.do"
BASE_URL = "https://www7.ceda.polimi.it/spazi/spazi/controller/"
BUILDING = 'innerEdificio'
ROOM = 'dove'
LECTURE = 'slot'
TIME_SHIFT = 0.25
MIN_TIME = 8
MAX_TIME = 20

GARBAGE = ["PROVA_ASICT" , "2.2.1-D.I."]


"""
Clean the dict with all the class occupancies from rooms that don't exists or are unreacheable
"""
def clean_data(infos):
    for building in infos:
        for room in GARBAGE:
            if room in infos[building]:
                del infos[building][room]          
            
    return infos


"""
Return a dict with all the info about the classrooms for the chosen day , 
the function makes a get requests to the URL and then 
build a dict with the classes information stored on the html table (the code may not be perfect 🥲)
"""

def find_classrooms(location , day , month , year):
    info = {} 
    buildingName = '-' #defaul value for building
    info[buildingName] = {} #first initialization due to table format

    params = {'csic': location , 'categoria' : 'tutte', 'tipologia' : 'tutte', 'giorno_day' : day , 'giorno_month' : month, 'giorno_year' : year , 'jaf_giorno_date_format' : 'dd%2FMM%2Fyyyy'  , 'evn_visualizza' : ''}
    r = requests.get(URL , params= params)
    
    soup = BeautifulSoup(r.text, 'html.parser')
    tableContainer = soup.find("div", {"id": "tableContainer"})
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