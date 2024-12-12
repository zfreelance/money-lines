from multiprocessing import freeze_support
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from selenium.webdriver.remote.webelement import WebElement


IS_HEADLESS = False # Hide automated Browser
SAFE_TITLES = ["Hard Rock"] # list of titles page scraped should give

def parseEvent(event: WebElement):
    team_names_el = event.find_elements(By.CSS_SELECTOR, ".hide-for-medsmall")
    team_names = [team_name_el.text for team_name_el in team_names_el]

    return team_names

def main():
    print("[+] Launching Browser...")

    driver = uc.Chrome(headless=IS_HEADLESS, use_subprocess=True)
    driver.implicitly_wait(10)

    # set state cookie
    driver.get('https://app.hardrock.bet/404')
    driver.add_cookie({"name": "childSite", "value": "AZ"})
    driver.add_cookie({"name": "showCookiesBanner", "value": "false"})

    driver.get('https://app.hardrock.bet/')

    if not any(keyword in driver.title for keyword in SAFE_TITLES):
        print(f"[!] Detected Abnormal Page Title {driver.title}. Exiting...")
        exit(1)

    # click nba button
    nba_button = driver.find_element(By.CSS_SELECTOR, 'li[data-cy="sports-tab:NBA"]')
    nba_button.click()

    events_list = driver.find_elements(By.CSS_SELECTOR, 'div.events-group .column .hr-market-view')

    for event in events_list:
        data = parseEvent(event)
        print(data)

    print("Done.")

    time.sleep(100)

    driver.quit()

if __name__ == '__main__':
    try:
        main()
    except TimeoutException as e:
        print(f"[!] Timed out. {e.msg}")
        exit(1)
    except NoSuchElementException as e:
        print(f"[!] Failed to locate element. {e.msg}")