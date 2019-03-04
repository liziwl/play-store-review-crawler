import time
import platform
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import reviewdb as rdb

CLEAN_ALL = False
DUMP_DB = True
DUMP_CSV = False
LOAD_TIME = 10
MAX_REVIEW_NUM = 5000

ALL_REVIEW_TAG = "d15Mdf bAhLNe"
SHOW_MORE_CLASS_TAG = "content.CwaK9"
BRIEF_COMMENT_TAG = "bN97Pc"
FULL_COMMENT_TAG = "fbQN7e"

scroll_to_bottom = "window.scrollTo(0, document.body.scrollHeight);"
click_show_more = "var a = document.querySelector('" + SHOW_MORE_CLASS_TAG + "'); a.click();"


def update_quote(text, have_nextline=False):
    rt = text.replace("\"", "\"\"")
    rt = rt.replace("'", "''")
    if not have_nextline:
        rt = rt.replace("\r", "")
        rt = rt.replace("\n", "")
    return rt


def extract_data(review_item):
    tmp = []
    # name
    name = review_item.find_elements_by_tag_name("span")[0].text
    name = update_quote(name, True)
    tmp.append(name)

    # review date
    tmp.append(review_item.find_elements_by_tag_name("span")[2].text)
    # star
    tmp.append(review_item.find_element_by_xpath(".//*[@aria-label]").get_attribute("aria-label"))

    comment_full = review_item.find_element_by_xpath(
        ".//*[@jsname='{}']".format(FULL_COMMENT_TAG)).get_attribute("textContent")
    comment_full = update_quote(comment_full)

    comment = review_item.find_element_by_xpath(".//*[@jsname='{}']".format(BRIEF_COMMENT_TAG)).text
    comment = update_quote(comment)

    if comment_full != "":
        comment = comment_full
    tmp.append(comment)

    if len(review_item.find_elements_by_css_selector(".LVQB0b")) > 0:
        re_tmp = review_item.find_elements_by_css_selector(".LVQB0b span")
        re_name = re_tmp[0].text
        re_name = update_quote(re_name, True)
        tmp.append(re_name)

        re_date = re_tmp[1].text
        tmp.append(re_date)

        prefix = len(review_item.find_elements_by_css_selector(".LVQB0b div")[-1].text)
        re_comm = review_item.find_elements_by_css_selector(".LVQB0b")[0].text
        re_comm = re_comm[prefix:]
        re_comm = update_quote(re_comm)
        tmp.append(re_comm)

    return tmp


def scroll_end(driver):
    check_end = 'return (window.scrollY + window.innerHeight) >= document.body.scrollHeight;'
    for i in range(2):
        # double check
        flag = driver.execute_script(check_end)
        while not flag:
            driver.execute_script(scroll_to_bottom)
            time.sleep(LOAD_TIME)
            flag = driver.execute_script(check_end)
            if not flag:
                print("Scroll to show more")


def get_review_num(driver):
    return len(driver.find_elements_by_xpath("//div[contains(@class, '{}')]".format(ALL_REVIEW_TAG)))


def main_for_app(app_name):
    url = "https://play.google.com/store/apps/details?id=" + app_name + "&showAllReviews=true&hl=en"
    driver.get(url)
    scroll_end(driver)

    page_num = 0
    # print("SHOW_MORE_CLASS_TAG", len(driver.find_elements_by_css_selector(SHOW_MORE_CLASS_TAG)))
    while len(driver.find_elements_by_css_selector(SHOW_MORE_CLASS_TAG)) > 0:
        print("page", page_num)
        page_num += 1
        button = driver.execute_script(click_show_more)
        time.sleep(LOAD_TIME)
        scroll_end(driver)
        # print("SHOW_MORE_CLASS_TAG", len(driver.find_elements_by_css_selector(SHOW_MORE_CLASS_TAG)))

        print("review num:", get_review_num(driver))
        if get_review_num(driver) > MAX_REVIEW_NUM:
            break

    reviews = driver.find_elements_by_xpath("//div[contains(@class, '{}')]".format(ALL_REVIEW_TAG))
    print("review num:", len(reviews))

    if DUMP_DB:
        db_driver = rdb.Reviewdb()
        table_name = app_name.replace(".", "_")

        if CLEAN_ALL:
            db_driver.db_droptable(table_name)
        db_driver.db_newtable(table_name)
        for review_item in reviews:
            tmp = extract_data(review_item)
            db_driver.db_insert_row(table_name, tmp)
        db_driver.db_close()

    if DUMP_CSV:
        db_driver = rdb.Reviewdb()
        table_name = app_name.replace(".", "_")
        db_driver.dump_csv(table_name)
        db_driver.db_close()


def get_driver():
    OS = platform.system()
    if OS == "Windows":
        driver = webdriver.Chrome('./lib/chromedriver.exe')
    elif OS == "Linux":
        driver = webdriver.Chrome('./lib/chromedriver_linux')
    elif OS == "Darwin":
        driver = webdriver.Chrome('./lib/chromedriver_mac')
    else:
        driver = None
    return driver


if __name__ == '__main__':
    app_id = ['com.github.shadowsocks', 'it.feio.android.omninotes']
    app_id = app_id[0:1]
    for name in app_id:
        driver = get_driver()
        if driver is None:
            exit(-1)

        wait = WebDriverWait(driver, LOAD_TIME)
        main_for_app(name)
        driver.quit()
