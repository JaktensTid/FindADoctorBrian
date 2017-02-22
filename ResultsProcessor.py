from lxml import html
from lxml import etree
import requests
import csv
from requests.exceptions import ConnectionError
from time import sleep

xpath_a_hrefs = "//div[@class='cyno-btn-wrapper']/a/@href"

def get_links_to_doctors_page(response):
    document = html.fromstring(response.content)
    return document.xpath(xpath_a_hrefs)

class DoctorPageProcessor():
    xpath_title = '//div[@property="dc:title"]'
    xpath_div_a_href = '//div[@class="field field-name-field-listing-website field-type-link-field field-label-hidden"]/div/div/a/@href'
    xpath_div_where_content = '//div[@class="field field-name-field-collection-practitioners field-type-field-collection field-label-above"]'
    xpath_div_first_name = './/div[@class="field field-name-field-pract-fname field-type-text field-label-hidden"]/div/div/text()'
    xpath_div_mi = './/div[@class="field field-name-field-pract-mi field-type-text field-label-hidden"]/div/div/text()'
    xpath_div_last_name = './/div[@class="field field-name-field-pract-lname field-type-text field-label-hidden"]/div/div/text()'

    def __init__(self, doctor_page_links, corresponding_zip):
        self.doctor_page_links = doctor_page_links
        self.corresponding_zip = corresponding_zip

    def run(self):
        clinics = self.get_corresponding_records()
        with open('result/' + self.corresponding_zip +'.csv', 'w', newline='', encoding="utf-8") as csvfile:
            titles = ["Clinic", "Link", "Doctor"]
            writer = csv.DictWriter(csvfile, fieldnames=titles)
            writer.writeheader()
            for doctor,info in clinics.items():
                writer.writerow({"Clinic": doctor, "Link": info[0], "Doctor": info[1]})

    def get_corresponding_records(self):
        result = {}
        for d_link in self.doctor_page_links:
            for i in range(0, 4):
                try:
                    response = requests.get(d_link)
                    document = html.fromstring(response.content)
                    if response.status_code != 200:
                        print("*************** STATUS CODE INVALID " + d_link + " **********************")
                    try:
                        link = document.xpath(self.xpath_div_a_href)[0]
                    except IndexError:
                        link = " "
                    title = document.xpath(self.xpath_title)[0].text_content()
                    doctor = self.get_doctor(document, d_link)
                    print('Page scraped: ' + d_link)
                    result[title] = (link,doctor)
                    break
                except ConnectionError:
                    sleep(5)
        return result

    def get_doctor(self, document, locator):
        def get(div_content):
            repr = etree.tostring(div_content)
            first_name = ""
            mi_name = ""
            last_name = ""
            try:
                first_name = div_content.xpath(self.xpath_div_first_name)[0]
            except IndexError:
                pass
            mi_names = div_content.xpath(self.xpath_div_mi)
            if len(mi_names) != 0:
                mi_name = mi_names[0]
            try:
                last_name = div_content.xpath(self.xpath_div_last_name)[0]
            except IndexError:
                pass
            full_name = first_name + " " + mi_name + " " + last_name if mi_name != "" else first_name + " " + last_name
            if full_name == " ":
                full_name = " "
            return full_name
        divs = document.xpath(self.xpath_div_where_content)
        if divs:
            full_names = []
            div_content = divs[0]
            odd = div_content.xpath('.//div[@class="field-item odd"]')
            if odd:
                for o in odd:
                    full_names.append(get(o))
            even = div_content.xpath('.//div[@class="field-item even"]')
            if even:
                for e in even:
                    full_names.append(get(e))
            filtered = list(filter(None, list(map(lambda x: x.strip(), full_names))))
            return ', '.join(filtered)
        print('Div is empty')
        return None


