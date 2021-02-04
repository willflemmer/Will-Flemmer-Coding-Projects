from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np

class SocialMBot:
    
    def __init__(self, account):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-proxy-server')
        chrome_options.add_argument("--start-maximized")
        self.account = account
        '''
        prox = Proxy()
        prox.proxy_type = ProxyType.MANUAL
        PROXY = "http://5.79.73.131:13010"
        #prox.socks_proxy = PROXY
        prox.ssl_proxy = PROXY
        prox.http_proxy = PROXY
        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)
        '''
        #self.bot = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities)
        self.bot = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    
    def login(self):
        try:
            self.bot.get('https://www.instagram.com')
            #input('Press Enter Once Page Has Loaded')
            time.sleep(np.random.randint(20, 30))
            if self.account == 'bsbc':
                user = 'buysmartbuycheap'
                passw = 'B0sch!2020' #removed for security
                

                
            self.bot.find_element_by_xpath("//input[@name = 'username']").send_keys(user)
            time.sleep(2)
            self.bot.find_element_by_xpath("//input[@name = 'password']").send_keys(passw)
            time.sleep(np.random.randint(1, 5))
            self.bot.find_element_by_xpath("//button[@class = 'sqdOP  L3NKy   y3zKF     ']").send_keys(Keys.ENTER)
            #input('Press Enter Once Page Has Loaded') 
            time.sleep(np.random.randint(20, 30))
        except:
            pass

    def page_followers(self, page_url):
        self.login()
        
        self.bot.get(page_url)
        time.sleep(np.random.randint(5, 10))

        following_xpath = "//a[contains(@href, '/followers/')]"
        self.bot.find_element_by_xpath(following_xpath).send_keys(Keys.ENTER)
        time.sleep(5)
        dialog = self.bot.find_element_by_xpath("//div[@role = 'dialog']//a")
        time.sleep(2)
        count = 0
        while count < 100:
            window = self.bot.find_element_by_xpath("//div[@class = 'isgrP']//a")

            time.sleep(2)
            unfollows = self.bot.find_elements_by_xpath("//button[@class = 'sqdOP  L3NKy   y3zKF     ']")
            
            for unfollow in unfollows:
                try:
                    if unfollow.text == 'Follow':
                        
                            unfollow.send_keys(Keys.ENTER)
                            time.sleep(8)
                            #self.bot.find_element_by_xpath("//button[@class = 'aOOlW -Cab_   ']").send_keys(Keys.ENTER)
                            #time.sleep(5)
                            count+=1
                            print('Followed', count, 'Pages')
                except:
                    print('Follow Failed')
                    
            print('\n Scrolling')
            try:
                window.send_keys(Keys.PAGE_DOWN)
                time.sleep(2)
            except:
                print('Issue with Scrolling')
            
        print('Followed', count, 'Pages in Total')
        self.bot.quit()

        
        
        
        
    
    def insta_follow_like(self, hashtag_list, POSTS_PER_HASH):
        self.login()
        follow_counter = 0
        like_counter = 0 
        general_counter = 0
        #Searching for hashtag:
        for search in hashtag_list:
            try:
                search = '#' + search
                self.bot.find_element_by_xpath("//input[@placeholder = 'Search']").send_keys(search)
                time.sleep(np.random.randint(10, 20))
                
                #Getting 2 most popular Related hashtag links:
                links = self.bot.find_elements_by_xpath("//a[@class = 'yCE8d  ']")
                links = links[:2]
            except:
                pass
            
            #Iterating through 2 most popular hashtag links:
            for elem in links:
                try:
                    href = elem.get_attribute('href')
                    url = href
                    self.bot.get(url)
                    time.sleep(np.random.randint(10, 25))
                    #clicking on first image
                    self.bot.find_element_by_xpath("//div[@class = 'v1Nh3 kIKUG  _bz0w']/a").send_keys(Keys.ENTER)
                    time.sleep(10)
                except:
                    pass
                #Liking/Following first 100 Posts
                for i in range(POSTS_PER_HASH):
                    try:
                        print('POST NUMBER: ', general_counter)
                        print("LIKED POSTS: ", like_counter)
                        print("FOLLOWED PAGES: ", follow_counter)
                        print('\n')
                        general_counter +=1
                        time.sleep(np.random.randint(10, 25))
                        prob1 = np.random.randint(10)
                        prob2 = np.random.randint(10)
                        #like:
                        if prob1 >= 5:
                            like = self.bot.find_element_by_xpath("//span[@class = 'fr66n']/button[@class = 'wpO6b ']")
                            
                            #check = self.bot.find_element_by_xpath("//span[@class = 'fr66n']/button/div/*[name()='svg']").get_attribute('aria-label')
                            #if check == 'Like':
                            like.send_keys(Keys.ENTER)
                            like_counter+=1
                            time.sleep(2)
                                
                        #follow
                        if prob2 >= 3:
                            follow = self.bot.find_element_by_xpath("//div[@class = 'bY2yH']/button")
                            f_check = follow.text
                            if f_check == 'Follow':
                                follow.send_keys(Keys.ENTER)
                                follow_counter +=1
                                time.sleep(4)
                                
                        #next
                        self.bot.find_element_by_css_selector('body').send_keys(Keys.RIGHT)
                        
                        #self.bot.find_element_by_xpath("//a[@class = ' _65Bje  coreSpriteRightPaginationArrow']").send_keys(Keys.ENTER)
                    except:
                        pass
      
    def twitter(self):
        self.bot.get("https://twitter.com/")
        
        
        
        
        
    def unfollow(self):
        self.bot.get('https://www.instagram.com')
        input('Press Enter Once Page Has Loaded')
        user = 'buysmartbuycheap'
        passw = 'B0sch!2020'
        self.bot.find_element_by_xpath("//input[@name = 'username']").send_keys(user)
        time.sleep(2)
        self.bot.find_element_by_xpath("//input[@name = 'password']").send_keys(passw)
        time.sleep(np.random.randint(1, 5))
        self.bot.find_element_by_xpath("//button[@class = 'sqdOP  L3NKy   y3zKF     ']").send_keys(Keys.ENTER)
        input('Press Enter Once Page Has Loaded') 
        self.bot.get("https://www.instagram.com/buysmartbuycheap/following/")
        time.sleep(5)
        following = self.bot.find_element_by_xpath("//a[contains(@href, 'cheap/following')]")
        time.sleep(2)
        following.send_keys(Keys.ENTER)
        time.sleep(5)
                        
        dialog = self.bot.find_element_by_xpath("//div[@role = 'dialog']//a")
        time.sleep(2)
        count = 0
        while count < 100:
            if count == 0:
                for i in range(20):
                    window = self.bot.find_element_by_xpath("//div[@class = 'isgrP']//a")
                    print('\n Scrolling')
                    window.send_keys(Keys.PAGE_DOWN)
                    time.sleep(2)
            
            time.sleep(2)
            unfollows = self.bot.find_elements_by_xpath("//div[@class = 'Pkbci']/button")
            
            for unfollow in unfollows:
                time.sleep(1)
                if unfollow.text == 'Following':
                    
                    unfollow.send_keys(Keys.ENTER)
                    time.sleep(3)
                    self.bot.find_element_by_xpath("//button[@class = 'aOOlW -Cab_   ']").send_keys(Keys.ENTER)
                    time.sleep(5)
                    count+=1
                    print('Unfollowed', count, 'Pages')
            
               
            print('\n Scrolling')
            window.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)
            
        print('Unfollowed', count, 'Pages in Total')
        
                        

        
        
        
        

price_spy = "https://www.instagram.com/pricespy/"
price_runner = "https://www.instagram.com/pricerunner_com/"

s = SocialMBot('bsbc')

s.page_followers(price_spy)

s = SocialMBot('dokhalicious')
s.page_followers(enjoy_dokha)
#s.insta_follow_like()
 
#s.unfollow() 

        
        
        
        
        
        
        
        
        
        
        
        
        