from bs4 import BeautifulSoup
import pandas as pd
import requests
import shutil
import os

page_number = 1
PAGES = 10 #(multiply by 20 for number of results)
base_url = 'http://www.legislation.gov.uk'


#https://www.legislation.gov.uk/asp
#http://www.legislation.gov.uk/ukpga
#http://www.legislation.gov.uk/browse/wales
#http://www.legislation.gov.uk/browse/ni

years = [x for x in range(1947, 2021)]#will need updating

country_list = ['http://www.legislation.gov.uk/ukpga','https://www.legislation.gov.uk/asp',
                'http://www.legislation.gov.uk/anaw', 'http://www.legislation.gov.uk/nia']
country_name_list = ['UK', 'Scotland', 'Wales', 'Northern Island']


for country, country_name in zip(country_list[1:], country_name_list[1:]):
    page_number = 1
    base_dir  = "C:/Users/My Account/Documents/Legally/" + '{}/'.format(country_name)
    path_laws = base_dir  + 'Laws/'
    path_notes = base_dir + 'Notes/'
    links = []
    laws = []
    notes = []
    names = []
    
    while page_number <= PAGES:
        
        url = country + '?page=' +str(page_number)
        print(url)
        page_number +=1
        
        response = requests.get(url, timeout = 10)        
        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()
        
        name_elems = soup.select('td:nth-child(1) a')
        for link in name_elems:
            link = str(link).split('"')[1]
            link = base_url + link
            if link not in links:
                links.append(link)
    
    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()
        name = str(soup.select('.pageTitle')).split('>')[1].split('<')[0]
        pdf_list = soup.select('.pdfLink')
        law = base_url + str(pdf_list[0]).split('"')[3]
        note = law.split('/pdfs')[0] + '/notes/data.pdf'
        names.append(name)
        laws.append(law)
        notes.append(note)
        
    items = {'Names': names,
             'Laws': laws,
             'Notes': notes}
    
    df = pd.DataFrame(items)
    df.to_csv('Legislation Spreadsheet'+''+'.csv')
    
    r = requests.get(country)
    soup = BeautifulSoup(r.content, 'html.parser')
    r.close()
    if country == 'http://www.legislation.gov.uk/ukpga':
        numbers = soup.select('.legYear')
        
    else:
        numbers = soup.findAll("li", {"class": "legYear"})
    
    
    
    year_num = {}           
    for number in numbers:
        number = str(number)
        x = number.split('>')[2]
        year = x.split(' ')[0]
        count = x.split('(')[1].split(')')[0]
        year_num.update({year : count})
                
    num_laws = list(year_num.values())
    num_laws = [int(i) for i in num_laws]
    num_laws = sum(num_laws)  
    
    years = years
    name_list = []
    fail_list = []
    
    for year in years:
        try:
            key = str(year)
            year = str(year) + '/'
            n = 0
            
            for i in range(len(df)):
                
                if n == int(year_num[key]):
                    print(key +'-Completed it mate')
                    break
                else:
                    if year in df['Laws'].iloc[i]:
                        name = df['Names'].iloc[i]
                        print(name)
                        try:
                            response_pdf = requests.get(df['Laws'].iloc[i])       
                            with open(path_laws + year + name + '-Law.pdf', 'wb') as f:
                                f.write(response_pdf.content)
                            response_pdf.close()
                            response_notes = requests.get(df['Notes'].iloc[i])
                            if response_notes.reason == 'OK':
                                with open(path_notes + year + name + '-Notes.pdf', 'wb') as f:
                                    f.write(response_notes.content)
                                response_notes.close()
                                name_list.append(name)    
                            n+=1
                        except:
                            fail_list.append(name)
        except:
            print('error with: ', year)

    print(df)
    #Create files for years in 'Laws' and 'Notes'
    #Iterate through laws and notes, then through files, if year in url matches year in file then store in file
    '''
base_dir  = "C:/Users/My Account/Desktop/Legally/"
path_laws = base_dir + 'Laws/'
path_notes = base_dir + 'Notes/'
years = [x for x in range(1947, 2021)]#will need updating
   
for country in country_name_list:
    base_dir  = "C:/Users/My Account/Documents/Legally/" + '{}/'.format(country)
    os.mkdir(base_dir)
    path_laws = base_dir  + 'Laws/'
    path_notes = base_dir + 'Notes/'
    os.mkdir(path_laws)
    os.mkdir(path_notes)
    print(base_dir)
    print(path_laws)
    print(path_notes)
    for year in years:
        laws_dir = path_laws + '{}'.format(year)
        notes_dir = path_notes + '{}'.format(year)
        print(laws_dir)
        print(notes_dir)
    #shutil.rmtree(path_notes + '{}'.format(year), ignore_errors = True)
        os.mkdir(notes_dir)
        os.mkdir(laws_dir)
    '''
    
    