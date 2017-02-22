import requests
import ResultsProcessor
from multiprocessing.pool import ThreadPool
from requests.exceptions import ConnectionError
from time import sleep

rootUrl = "http://www.smilemonalisa.com/results"
zips = open('zips.txt', 'r').read().split('\n')
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}

def get_data_for_zip(zip):
    return {"zipcode": zip,
    "proximity": "300"}

def make_request(data):
    for i in range(0,4):
        try:
            response = requests.post(rootUrl, headers=headers, data=data)
            return response
        except ConnectionError:
            sleep(5)

def scrape(t):
    i, zip = t
    response = make_request(get_data_for_zip(zip))
    if response:
        print('Got response from zip ' + zip)
        links = ResultsProcessor.get_links_to_doctors_page(response)
        worker = ResultsProcessor.DoctorPageProcessor(links, zip)
        worker.run()

if __name__ == "__main__":
    with ThreadPool(100) as p:
        p.map(scrape, enumerate(zips))

