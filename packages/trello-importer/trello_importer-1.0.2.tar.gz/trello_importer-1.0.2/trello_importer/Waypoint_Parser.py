import os
import pathlib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pprint import pprint
import re
import time


class Parser:
    """
        This package help to add Mission(Waypoint) from https://f4.intek.edu.vn/ to Trello
    """
    def __init__(self, file_path, key_word):
        """

        :param file_path: str ( https://f4.intek.edu.vn/login/index.php  )
        :param key_word: str (Project name)
        """
        self.__file_path = file_path
        self.__key_word = key_word
        self.__data = [] #list of waypoint

    #def find_text(self):
    #    """
    #    :return: a list of waypoint from README.md
    #    """
    #    #find text in txt,doc file
    #    list_data = []
    #    file_path = os.path.abspath(self.__file_path)
    #    with open(file_path) as f:
    #        for line in f:
    #            if self.__key_word in line:
    #                list_data.append(line)
    #    self.__data = list_data
    #    return list_data

    #def strip_text(self, rm_text):
    #    # rm_text : a list of text that you want to remove
    #    if len(self.__data) > 0:
    #        for text_index in range(len(self.__data)):
    #            for data in rm_text:
    #                self.__data[text_index] = self.__data[text_index].strip(data)

    def read_data_index(self):
        # check data index
        for data_index in range(len(self.__data)):
            print("line:", data_index, "- data:", self.__data[data_index])

    def remove_line(self, line_number):
        """

        :param line_number:  line number that you want to remove
        """
        del self.__data[line_number]

    def find_html_text(self,driver,email,password):
        """

        :param driver: str  (we use geckodriver to open webpage)
        :param email:str (mail name)
        :param password:str (mail password)
        :return: driver obj (session which the system are operating),list_waypoint(list):a list of WP mission
        """
        driver = webdriver.Firefox(executable_path = geckgodriver)
        #gotowebname
        driver.get(self.__file_path)
        driver.maximize_window()
        time.sleep(1)
        #login by google
        driver.find_element_by_link_text("Google").click()
        time.sleep(1)
        #mail id
        driver.find_element_by_name("identifier").send_keys(email)
        driver.find_element_by_xpath("//*[@id='identifierNext']").click()
        time.sleep(2)
        #mail pass
        driver.find_element_by_name("password").send_keys(password)
        time.sleep(1)
        driver.find_element_by_xpath("//*[@id='passwordNext']").click()
        time.sleep(1)
        driver.find_element_by_link_text("My missions").click()
        time.sleep(1)
        #project name seach
        driver.find_element_by_name("search").send_keys(self.__key_word)
        time.sleep(1)
        driver.find_element_by_name("search").send_keys(Keys.ENTER)
        time.sleep(1)
        try:
            driver.find_element_by_link_text("Resume").click()
        except:
            driver.find_element_by_link_text("Start").click()
        html = driver.page_source
        html = re.findall('(?:(?<=title="Completed:)|(?<=title="Not completed:))(.*)(?:(?=" alt)|(?=$))', html)
        list_waypoint = []
        for wp in range(len(html)):
            if "WP" in html[wp]:
                list_waypoint.append(html[wp])

        self.__data=list_waypoint
        return driver,list_waypoint


    def add_to_trello(self,webname,driver,html):

        #driver = webdriver.Firefox(executable_path=geckgodriver)
        time.sleep(1)
        #driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')  #macos
        driver.get(webname)
        driver.maximize_window()
        time.sleep(1)
        #login by google
        driver.find_element_by_xpath("//*[@id='google-link']").click()
        time.sleep(1)
        click_add_board = []
        create_board_text = []
        click_button = []
        list_of_title = ["","Backlogs","Todo","Doing","Review","Done","[Sprint#1]"]
        click_add_board = (driver.find_elements_by_class_name("board-tile.mod-add"))

        for element in click_add_board: element.click()

        create_board_text = (driver.find_elements_by_class_name("subtle-input"))
        time.sleep(1)
        #add board name
        for element in create_board_text: element.send_keys(self.__key_word)
        time.sleep(1)
        #click next
        click_button = driver.find_elements_by_class_name("button.primary")
        for element in click_button: element.click()
        # add title
        time.sleep(2)
        for title in list_of_title:
            add_list_button = []
            add_list_text = []
            add_list_text = driver.find_elements_by_class_name("list-name-input")
            for element in add_list_text:
                #click add title
                element.click()
                if title == "Backlogs":
                    add_card_button = []
                    card_textfield = []
                    element.send_keys(title)
                    add_list_button = driver.find_elements_by_class_name("primary.mod-list-add-button.js-save-edit")
                    for element in add_list_button: element.click()
                    add_card_button = driver.find_elements_by_class_name("js-add-a-card")
                    for project_name in add_card_button: project_name.click()
                    for project_name in html:
                        card_textfield = driver.find_elements_by_class_name("list-card-composer-textarea.js-card-title")
                        for element in card_textfield:element.send_keys(project_name)
                        add_another_card_button = []
                        add_another_card_button = driver.find_elements_by_class_name("primary.confirm.mod-compact.js-add-card")
                        for element in add_another_card_button:element.click()
                        #time.sleep(0.5)
                else:
                    add_list_text = driver.find_elements_by_class_name("list-name-input")
                    for element in add_list_text : element.send_keys(title)
                    add_list_button = driver.find_elements_by_class_name("primary.mod-list-add-button.js-save-edit")
                    for element in add_list_button: element.click()










#web address or path tx
#geckgodriver = '/usr/bin/google-chrome-stable'
#driver = webdriver.Firefox(executable_path = geckgodriver)

#find_data = Parser("https://f4.intek.edu.vn/login/index.php", "QR Code Reader")
#driver,list_waypoint = find_data.find_html_text(driver,"minh.nong@f4.intek.edu.vn","quocminh2910")
#find_data.read_data_index()
#find_data.add_to_trello("https://trello.com/login",driver,list_waypoint)

# print(find_data.find_text())
# print(find_data.strip_text(["#", "\n"]))
# find_data.read_data_index()
# find_data.remove_line(54)
# find_data.read_data_index()
