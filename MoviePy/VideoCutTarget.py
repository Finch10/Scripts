#!pip install selenium
#!apt-get update # to update ubuntu to correctly run apt install
#!apt install chromium-chromedriver
#!cp /usr/lib/chromium-browser/chromedriver /usr/bin
import sys
import time
import requests
from selenium import webdriver

import pandas as pd
import time
from selenium.common.exceptions import NoSuchElementException
import os
from PyPDF2 import PdfFileReader

# sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')


def wait_get_href() -> tuple:
    """Returns a tuple with the URL and the name of the document.
    If there is no file, it returns a tuple with empty variables"""

    #Make 15 attempts to find element with file on page
    for _ in range(15):
        try:
            element = driver.find_element_by_xpath(
                '//*[@id="contentload"]/table/tbody/tr/td[2]/a[1]'
            )
            url = element.get_attribute("href")
            name = element.text
            return (url, name)
        except NoSuchElementException:
            time.sleep(1.5)
    #If didn't find anything return str variables with blank values
    url = ""
    name = ""
    return (url, name)


def get_number_pages(href):
    """Gets the url of the file and returns the number of pages"""

    driver.get(href)
    time.sleep(3)
    pdf_download_icon = driver.find_element_by_xpath(
        "/html/body/div[1]/div[3]/div[2]/div[2]/div/div/div/div[3]/div[2]/div/a[2]"
    )
    # Retrieves the list of source files in the directory to find the file that
    #will be loaded by getting a new list and deleting the old files
    precedent_files_list = os.listdir()
    #Downloading file
    pdf_download_icon.click()
    
    #If the file is too large, the programs will try to get a list of files in the directory
    # several times to find out if the file has been downloaded
    #
    # Variable for counting number of while iterations 
    counter_while = 0
    #Variable used to stop iterations
    flag_while = True
    while flag_while:
        #Wait for downloading
        time.sleep(4)

        #Getting new list of files in directory
        current_files_list = os.listdir()
        # Identify file that was downloaded
        new_file = list(set(current_files_list) - set(precedent_files_list))

        if new_file:
            flag_while = False
        elif counter_while == 5:
            #Returns number of pages 0 if the file failed to be downloaded    
            return 0
        else:
            #Increase by 1 if the file was not downloaded
            counter_while += 1

    #Extracting name of file from list by it's index
    new_file = new_file[0]

    # opening file and extracting number of pages
    pdf = PdfFileReader(open(new_file, "rb"))
    number_pages = pdf.getNumPages()

    # Delete downloaded file
    os.remove(new_file)
    return number_pages

def process_excel(list_documents):
    """Retrieves a list of documents and returns the name, URL, page numbers 
    and returns a dictionary with this data"""

    #Store the data in the dictionary for further creation of the csv table 
     processed_data = {
        "Denumire": [],
        "Numar": [],
        "Data": [],
        "URL": [],
        "Number of Pages": [],
    }

    #Creates a variable to count the total number of pages
    total_number_pages = 0
    #Iterate throw excel file with initial documents
    for number, data in list_documents:

        driver.get("https://www.legis.md/")
        nr_doc_tag = driver.find_element_by_id("nr_doc")

        nr_doc_tag.click()
        nr_doc_tag.send_keys(number)

        data_doc_tag = driver.find_element_by_id("datepicker1")
        data_doc_tag.click()
        data_doc_tag.send_keys(data)

        search_button = driver.find_element_by_class_name("glyphicon-search")
        search_button.click()

        #Search for document
        href, name = wait_get_href()
        if href:
            number_pages = get_number_pages(href)
            total_number_pages += number_pages
        else:
            number_pages = ""

        processed_data["Denumire"].append(name)
        processed_data["Numar"].append(number)
        processed_data["Data"].append(data)
         processed_data["URL"].append(href)
         processed_data["Number of Pages"].append(number_pages)

    #Adding row with total value and blank data to otherses 
     processed_data["Denumire"].append("")
     processed_data["Denumire"].append("Total")
     processed_data["Number of Pages"].append("")
     processed_data["Number of Pages"].append(total_number_pages)
     processed_data["Numar"].append("")
     processed_data["Numar"].append("")
     processed_data["Data"].append("")
     processed_data["Data"].append("")
     processed_data["URL"].append("")
     processed_data["URL"].append("")

    return processed_data


def main():

    # Setting up Selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome("chromedriver", chrome_options=chrome_options)


    # Importing data from excel
    df = pd.read_excel("/content/drive/MyDrive/Documente/Lista cu documente/Lista 1.xlsx")
    # Transform in massive for better use
    list_documents = df.values
    processed_data = process_excel(list_documents)
    #Save data in csv file
    df_with_href = pd.DataFrame.from_dict(processed_data)
    df_with_href.to_csv("/content/drive/MyDrive/Documente/Documente prelucrate/1lista.csv")

    return None

if __name__ == __main__:
    main()
