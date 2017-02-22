import requests
import ResultsProcessor

rootUrl = "http://www.smilemonalisa.com/results"
zips = ["10001","33601","61606","68105","75201"]
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}

def get_data_for_zip(zip):
    return {"zipcode": zip,
    "proximity": "300"}

def make_request(data):
    response = requests.post(rootUrl, headers=headers, data=data)
    return response

if __name__ == "__main__":
    responces = []
    for zip in zips:
        responce = make_request(get_data_for_zip(zip))
        responces.append(responce)

    doctors_dict = {}

    for i in range(len(responces)):
        doctors_dict[zips[i]] = ResultsProcessor.get_links_to_doctors_page(responces[i])

    for zip,links in doctors_dict.items():
        worker = ResultsProcessor.DoctorPageProcessor(links,zip)
        worker.run()
