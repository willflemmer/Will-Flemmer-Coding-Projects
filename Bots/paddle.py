from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

from selenium.webdriver.common.keys import Keys



class paddle_bot:

    def __init__(self, days):
        self.days = days

        self.bot = webdriver.Chrome(ChromeDriverManager().install())
        self.get_links()


    def get_links(self):

        home = 'https://stclementstennis.mycourts.co.uk/payplay_bookings.asp?'
        self.bot.get(home)
        time.sleep(2)

        day_elems = self.bot.find_elements_by_xpath("//div[@class = 'desktop']/a[contains(@href, 'payplay_bookings.asp?d')]")[1:]

        day_links = {}
        for item in day_elems:
            day = item.text.split(' ')[0]
            day = day.lower()
            day = day[:2]
            link = item.get_attribute('href')

            day_links.update({day: link})


        self.validate_days(day_links)

    def validate_days(self, day_links):


        for item in self.days:
            try:
                day = item['day']
                link = day_links[day]
                times = item['times']


                self.check_times(link, times)
            except:
                pass


    def check_times(self,link, times):
        self.bot.get(link)
        time.sleep(2)
        all_courts = self.bot.find_elements_by_xpath("//div[@class = 'pp_court']")
        p_courts = all_courts[-2:]
        av_times = []
        for court in p_courts:

            av_times_input = court.find_elements_by_xpath(".//label/input[@name = 'ctid_csv']")
            all_times = court.find_elements_by_xpath('.//label')
            for time_t in all_times:

                if 'not' not in time_t.text.lower():
                    time_t = time_t.text.split(' ')[0]
                    av_times.append(time_t)

            print(av_times)
            print(times)
            for start_time in times:
                mins = start_time[-2:]


                if mins == '00':
                    end_time = start_time[:-2] + '30'

                if mins == '30':
                    end_time = int(start_time[:-2]) +1
                    end_time = str(end_time) + '00'

                print('start time', start_time)
                print('end_time', end_time)

                if start_time in av_times and end_time in av_times:
                    print(start_time, 'SLOT AVAILABLE')
                    self.book_time(start_time, end_time, court)
                else:
                    print(start_time, 'NOT AVAILABLE' )


    def book_time(self, start_time, end_time, court):
        xpath1 = ".//label[contains(text(), '{}')]/input".format(start_time)
        start_box = court.find_element_by_xpath(xpath1).click()
        time.sleep(2)
        xpath2 = ".//label[contains(text(), '{}')]/input".format(end_time)
        end_box = court.find_element_by_xpath(xpath2).click()
        time.sleep(2)
        submit = court.find_element_by_xpath(".//input[@type = 'submit']").click()
        time.sleep(3)
        code = self.bot.find_element_by_xpath("//span[@id = 'vc']").text
        self.bot.find_element_by_xpath("//input[@id= 'verification_code']").send_keys(code)
        time.sleep(2)
        self.bot.find_element_by_xpath("//input[@id= 'button']").click()
        time.sleep(2)
        print('done')




# Input times and days in order of priority
# monday --> 'mo'
# tuesday --> 'tu'
# wednesday --> 'we'
# thursday --> 'th'
# friday --> 'fr'
# saturday --> 'sa'
# sunday --> 'su'
p = paddle_bot([{'day':'mo', 'times': ['700', '800', '900']}])