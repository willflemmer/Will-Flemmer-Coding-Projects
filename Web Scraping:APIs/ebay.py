import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
import time
from urllib.parse import quote
import sys
import mysql.connector
from sqlalchemy import create_engine

class Ebay:
    
    def update_oauth(self):
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)
        time.sleep(2)
        user = 'flemmerwill@gmail.com'
        password = '' #removed for security
    
        driver.get("https://developer.ebay.com/my/auth?env=production&index=0&auth_type=oauth")
        
        time.sleep(5)
        driver.find_element_by_xpath("//input[@placeholder = 'Username or email']").send_keys(user)
        time.sleep(3)
        driver.find_element_by_xpath("//input[@placeholder = 'Password']").send_keys(password)
        time.sleep(3)
        driver.find_element_by_xpath("//button[@class = 'btn btn--primary sign-in-button']").send_keys(Keys.ENTER)
        time.sleep(8)
        
        driver.find_element_by_xpath("//a[contains(text(), 'Get OAuth Application Token')]").send_keys(Keys.ENTER)
        time.sleep(4)
        
        token = driver.find_element_by_xpath("//div[@id = 's0-0-21-7-2-oauth-app-token']").text
        time.sleep(2)
        driver.close()
        return token
        
        
    
    def get_categories(self):
        r = requests.get("https://open.api.ebay.com/shopping?callname=GetCategoryInfo&appid=williamf-buysmart-PRD-6c8e8a00c-d4a81966&siteid=0&CategoryID=-1&version=967&IncludeSelector=ChildCategories")
        print(r.text)
        soup = bs(r.content, 'lxml')
        
        cats = soup.find_all('category')
        cat_list = []
                
        bad_cats = ['Travel', 'Tickets & Experiences', 'Stamps', 'Sports Mem, Cards & Fan Shop', 'Specialty Services',
                    'Real Estate', 'Pottery & Glass', 'Gift Cards & Coupons', 'Entertainment Memorabilia', 'Dolls & Bears',
                    'Crafts', 'Coins & Paper Money', 'Collectibles', 'Antiques', 'Art', 'Music','Everything Else', 'Root']
        
        for cat in cats:
            id_num = cat.find('categoryid').text
            cat_name = cat.find('categoryname').text
            if cat_name not in bad_cats:
                cat_dict = {'id': id_num, 'category': cat_name}
                cat_list.append(cat_dict)
            
                
        print(len(cat_list))
        bad_l2s = ['Catalogs', 'CNC, Metalworking & Manufacturing', 'Fasteners & Hardware',
                   'Heavy Equipment, Parts & Attachments',
                    'HVAC & Refrigeration',
                    'Hydraulics, Pneumatics, Pumps & Plumbing',
                    'Industrial Automation & Motion Controls',
                     'Material Handling',
                     'Modular & Prefabricated Buildings',
                     'Restaurant & Food Service',
                     'Retail & Services',
                     'Test, Measurement & Inspection',
                     'Websites & Businesses for Sale',
                      'Binoculars & Telescopes',
                      'Camcorders',  'PDAs',
                      'PDA Accessories',
                      'Film Stock',
                     'Laserdiscs',
                     'UMDs',
                     'VHS Tapes',
                     'Other Formats',]
        
        sub_cats = []
        id_list = []
        for cat in cat_list: 
            
            id_num = cat['id']
            name = cat['category']
            r = requests.get("https://open.api.ebay.com/shopping?callname=GetCategoryInfo&appid=williamf-buysmart-PRD-6c8e8a00c-d4a81966&siteid=0&CategoryID={}&version=967&IncludeSelector=ChildCategories".format(id_num))
            soup = bs(r.content, 'xml')
            items = soup.find_all('Category')
            for item in items:
                num = item.find('CategoryID').text
                name = item.find('CategoryName').text
                if name not in bad_l2s:
                    d = {'id': num, 'category': name, 'parent_category': cat['category']}
                    sub_cats.append(d)
                    id_list.append(num)
                
        #return sub_cats
        print(len(sub_cats))
        l3_dict_list = []
        for di in sub_cats:
            l2_cat = di['category']
            l2_id = di['id']
            l1_cat = di['parent_category']
            r = requests.get("https://open.api.ebay.com/shopping?callname=GetCategoryInfo&appid=williamf-buysmart-PRD-6c8e8a00c-d4a81966&siteid=0&CategoryID={}&version=967&IncludeSelector=ChildCategories".format(l2_id))
            soup = bs(r.content, 'xml')
            items = soup.find_all('Category')
            for item in items:
                num = item.find("CategoryID").text
                l3_cat = item.find("CategoryName").text
                item_d = {'id': num, 
                          'l3_cat': l3_cat,
                          'l2_cat': l2_cat,
                          'l1_cat': l1_cat}
                l3_dict_list.append(item_d)
        
        print("number of l3 cats", len(l3_dict_list))
        return l3_dict_list
    
    
    
    #3. Iterate Through Categories:
        #filters need to be encoded
        #need to increase offset and iterate
    def drop_dups(self):
        print('Dropping dups')
        self.cursor.execute("DROP TABLE IF EXISTS copy_table")
        self.conn.commit()
        self.cursor.execute('CREATE TABLE copy_table LIKE {}'.format(self.table))
        self.conn.commit()
        self.cursor.execute('INSERT INTO copy_table SELECT * FROM {} GROUP BY url, title, price, website'.format(self.table))
        self.conn.commit()
        self.cursor.execute('DROP TABLE {}'.format(self.table))
        self.conn.commit()
        self.cursor.execute('ALTER TABLE copy_table RENAME TO {}'.format(self.table))
        self.conn.commit()


    def upload_to_database(self, df):
        print('Uploading to Database')
        
        self.conn = mysql.connector.connect(
            host = '64.20.48.90',
            user = 'gencomma_will', 
            password = 'Polster123',
            database = '{}'.format(self.database))
        
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS {} (id INT(11) AUTO_INCREMENT PRIMARY KEY,
                              title VARCHAR(535), price DECIMAL(50, 2), website VARCHAR(535), url TEXT NOT NULL,
                              src TEXT NOT NULL, parent_category VARCHAR(535), sub_category VARCHAR(535),
                                description TEXT NOT NULL, mpn TEXT NOT NULL, gtin TEXT NOT NULL, brand VARCHAR(535), aspects TEXT NOT NULL) '''.format(self.table))
        self.conn.commit()
        
        lower_bound = 0
        higher_bound = lower_bound + 50000
        
        if len(df) > 50000:
            while higher_bound < len(df) + 50000:
                print("in while loop")
                upload_df = df[lower_bound:higher_bound]
            
                self.engine = create_engine('mysql+mysqlconnector://gencomma_will:Polster123@64.20.48.90/{}'.format(self.database), echo=False)
    
                
                self.cursor.execute("SET collation_connection = 'utf8_general_ci'")
                self.cursor.execute("ALTER DATABASE {} CHARACTER SET utf8 COLLATE utf8_general_ci".format(self.database))
                self.cursor.execute("ALTER TABLE {} CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci".format(self.table))
                self.conn.commit()
                
                upload_df.drop_duplicates(inplace = True)
                upload_df.to_sql(name='{}'.format(self.table), con=self.engine, if_exists = 'append', index = False) 
                
                lower_bound += 50000
                higher_bound = lower_bound + 50000
        else:
             print("not in while loop")
             self.engine = create_engine('mysql+mysqlconnector://gencomma_will:Polster123@64.20.48.90/{}'.format(self.database), echo=False)
             
             self.cursor.execute("SET collation_connection = 'utf8_general_ci'")
             self.cursor.execute("ALTER DATABASE {} CHARACTER SET utf8 COLLATE utf8_general_ci".format(self.database))
             self.cursor.execute("ALTER TABLE {} CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci".format(self.table))
             self.conn.commit()
             upload_df = df
             upload_df.drop_duplicates(inplace = True)
             upload_df.to_sql(name='{}'.format(self.table), con=self.engine, if_exists = 'append', index = False) 

        
        self.drop_dups() 
        
        self.cursor.execute('DROP TABLE IF EXISTS ebay_skeleton_backup')
        self.cursor.execute('CREATE TABLE ebay_skeleton_backup LIKE {}'.format(self.table))
        self.conn.commit()
        self.cursor.execute('INSERT INTO ebay_skeleton_backup SELECT * FROM {}'.format(self.table))
        self.conn.commit()
        
        self.cursor.close()
        self.conn.close()
        
        print('Upload Finished')
    
    def extract_data(self, item_list, parent_category, sub_category):
        results_list = []
        print("Number of items from page: ", len(item_list))
        for item in item_list:
            try:
                item_id = item['itemId']
                #print(item_id)
                request_url = "https://api.ebay.com/buy/browse/v1/item/{}?fieldgroups=PRODUCT".format(item_id)
                r = requests.get(request_url, headers = self.h)
                data = json.loads(r.text)
                
                price = item['price']['convertedFromValue']
                title = item['title']
                website = 'ebay'
                url = item['itemAffiliateWebUrl']
                
                if 'thumbnailImages' in item.keys():
                    src = item['thumbnailImages'][0]['imageUrl']
                elif 'image' in data.keys():
                    src = data['image']['imageUrl']
                
                if 'product' in data.keys():
                    
                    if 'gtins' in data['product'].keys():
                        gtin = data['product']['gtins'][0]
                    else:
                        gtin = 'NA'
                        
                    if 'mpns' in data['product'].keys():
                        mpn = data['product']['mpns'][0]
                    else:
                        mpn = 'NA'
                        
                    if 'description' in data['product'].keys():
                        description = data['product']['description']
                    else:
                        description = 'NA'
                        
                    if 'brand' in data['product'].keys():
                        brand = data['product']['brand']
                    else:
                        brand = 'NA'
                        
                    if 'aspectGroups' in data['product'].keys():
                        aspect_list = data['product']['aspectGroups'][1]['aspects']
                        aspects = []
                        for a in aspect_list:
                            if a["localizedName"].lower() != "brand":
                                vals = {"name": a["localizedName"], "values":a['localizedValues']}
                                aspects.append(vals)
                        aspects = json.dumps(aspects)
                    else:
                        aspects = 'NA'
                    
                else:
                    description = 'NA'
                    
                    if 'mpn' in data.keys():
                        mpn = data['mpn']
                    else:
                        mpn = 'NA'
                        
                    if 'gtin' in data.keys():
                        gtin = data['gtin']
                    else:
                        gtin = "NA"
                        
                    if "brand" in data.keys():
                        brand = data["brand"]
                    else:
                        brand = 'NA'
                        
                    if 'localizedAspects' in data.keys():
                        aspects = []
                        aspect_list = data['localizedAspects']
                        for a in aspect_list:
                            if a['name'].lower() != "brand":
                                vals = {"name": a["name"], "values":a['value']}
                                aspects.append(vals)
                        aspects = json.dumps(aspects) #converts to string form
                        #use aspects = ast.literal_eval(aspects) to get back to list of dicts
                        
                    else:
                        aspects = 'NA'
                    
                    
                d = {'price': price, 'title': title, 'website': website, 'url':url,'src': src, 'parent_category': parent_category, 'sub_category': sub_category,
                         'gtin':gtin, 'mpn':mpn, 'description': description, 'aspects':aspects, 'brand':brand}
                    
                results_list.append(d)
            
                
            except:
                pass
            
        return results_list
    
    def __init__(self):
        self.database = 'gencomma_items'
        self.table = 'ebay_skeleton'
        #save cats in json locally
        #cat_dict_list = self.get_categories()
        with open('cat_dict.json') as json_file:
            cat_dict_list = json.load(json_file)
        
        print(len(cat_dict_list))
        token = self.update_oauth()
        enc = quote("priceCurrency:GBP,price:[25..1000000],conditions:{NEW},itemLocationCountry:GB,buyingOptions:{FIXED_PRICE},deliveryCountry:GB")

        self.df = self.iterate_through_cats(cat_dict_list, token, enc)
        self.upload_to_database(self.df)
        
        
    def iterate_through_cats(self, cat_dict_list, token, enc):
        columns = ['title', 'price', 'website', 'url', 'src', 'parent_category', 'sub_category', 'gtin',
           'mpn', 'aspects', 'description', 'brand']
        df = pd.DataFrame(columns = columns)
        e_list = []
        cat_count = 0
        call_count = 0
        
        #2600 in total
        # [n:m] n is included, m is not included
        
        #Calls per cat = (cat_end - cat_start) * pages * 200 < 100,000
        cat_start = 620
        cat_end = cat_start + 80 #change to 90
        pages = 5 #200 items/page
        
        # if do page = 1, can scrape 450 cats in a day
        # if do page = 3, can scrape 150 cats in a day
        
        for d in cat_dict_list[cat_start:cat_end]:
            cat_count+=1
            items_scraped_in_cat = 0
            id_num = d['id']
            parent_cat = d['l1_cat']
            sub_cat = d['l2_cat']
            
            if sub_cat  == 'Everything Else':
                continue
            
            print(df)
            print('\n')
            print(parent_cat)
            print(sub_cat)
            print('Category Count: ', cat_count)
            print('Call Count: ', call_count)
            print('\n')
            offset = 0
            for i in range(pages): 
                
                call_count+=200
                
                #try:
                Authorization = 'Bearer ' + token
                header_encode = 'affiliateCampaignId=5338721072,contextualLocation=' + quote('country=GB')
                h = {'X-EBAY-C-ENDUSERCTX': header_encode,
                     'Authorization': Authorization
                     }
                self.h = h
                url = "https://api.ebay.com/buy/browse/v1/item_summary/search?category_ids={}&limit=200&offset={}&filter={}".format(id_num, offset,enc)
                r = requests.get(url, headers = h)
                
                if r.status_code == 500:
                    print("SERVER ERROR")
                    print(r.text)
                    #sys.exit()
                    
                #print(r.status_code)
                if r.status_code != 200:
                    print(r.text)
                    token = self.update_oauth()
                    Authorization = 'Bearer ' + token
                    header_encode = 'affiliateCampaignId=5338721072,contextualLocation=' + quote('country=GB')
                    self.h = {'X-EBAY-C-ENDUSERCTX': header_encode,
                         'Authorization': Authorization}
                    url = "https://api.ebay.com/buy/browse/v1/item_summary/search?category_ids={}&limit=200&offset={}&filter={}".format(id_num, offset,enc)
                    r = requests.get(url, headers = self.h)
                
                #print(url)
                data = json.loads(r.text)
                if 'itemSummaries' in data.keys():
                    total_items_in_cat = data['total']
                    item_list = data['itemSummaries']
                
                    list_of_results = self.extract_data(item_list, parent_cat, sub_cat) #list of dicts
                    df = df.append(list_of_results)
                    print('Item list length: ',len(item_list))
                    offset +=len(item_list)
                    
                    
                else: 
                    print('Item list not in response')
                    break
                
                if len(item_list) < 200:
                    print('Break: Less than 200 items on page')
                    break
                    
                
                    items_scraped_in_cat += len(item_list)
                if items_scraped_in_cat >= total_items_in_cat:
                    print('Scraped all items in category')
                    break
                        

                #except:
                    print('Error with ', sub_cat)
                    e_list.append(sub_cat)
                        
                        
        return df
                    
        print('Finished run')
        
if __name__ == '__main__':
    ebay = Ebay()
