import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from colorama import Fore, Style
import time
import os
import csv
from typing import List, Dict
from multiprocessing import freeze_support


IS_HEADLESS = True # Hide automated Browser
SAFE_TITLES = ["Hard Rock"] # list of titles page scraped should give
UPDATE_INTERVAL = 10 # how often sportspage excel should be update (in Seconds)
EXCEL_FILENAME = "../sportspage_nba.csv"

def safe_find_element_text(event, selector_type, selector, default_text="?") -> str:
    """
    Select text element with CSS selector. If not found return Default text
    """
    try:
        return event.find_element(selector_type, selector).text
    except NoSuchElementException:
        return default_text

def parseEvent(event: WebElement):
    """
    Parse event element
    """
    team_names_el = event.find_elements(By.CSS_SELECTOR, ".participants .show-for-medsmall")

    team_names = [team_name_el.text for team_name_el in team_names_el]

    if len(team_names) != 2:
        raise Exception(f"Team names length isn't 2. {team_names}")

    spread_bh = safe_find_element_text(event, By.CSS_SELECTOR, "div[data-cy=\"wager-button:Spread BH\"] .selection-line-value")
    spread_ah = safe_find_element_text(event, By.CSS_SELECTOR, "div[data-cy=\"wager-button:Spread AH\"] .selection-line-value")

    total_over = safe_find_element_text(event, By.CSS_SELECTOR, "div[data-cy=\"wager-button:Total Points Over\"] .selection-line-value")
    total_under = safe_find_element_text(event, By.CSS_SELECTOR, "div[data-cy=\"wager-button:Total Points Under\"] .selection-line-value")

    win_b = safe_find_element_text(event, By.CSS_SELECTOR, "div[data-cy=\"wager-button:To Win B\"]")
    win_a = safe_find_element_text(event, By.CSS_SELECTOR, "div[data-cy=\"wager-button:To Win A\"]")

    total_O_split = total_over.split(" ")
    total_U_split = total_under.split(" ")

    teams = [
        {
            "team_name": team_names[0],
            "spread": spread_bh,
            "total_pts": total_O_split[1] if len(total_O_split) > 1 else total_over,
            "win": win_b
        },
        {
            "team_name": team_names[1],
            "spread": spread_ah,
            "total_pts": total_U_split[1] if len(total_U_split) > 1 else total_under,
            "win": win_a
        }
    ]

    return teams

def save_excel_file(events_data: List[List[Dict]]):
    """
    Save Data in Excel File
    """
    file_path = os.path.join(os.path.dirname(__file__), EXCEL_FILENAME)

    first_rows = [["Team Name","Spread","Total Points","Win"], []]

    excel_rows = []

    for event_data in events_data:
        for i, team in enumerate(event_data):
            excel_rows.append(list(team.values()))

            # separate each dual
            if i == 1:
                excel_rows.append([])

    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerows(first_rows)
        writer.writerows(excel_rows)

    print(f"{Fore.GREEN}[+] Saved Excel file with sportspage{Style.RESET_ALL}")

def update_excel_events(driver):
    """
    Select events and update excel
    """
    events_list = driver.find_elements(By.CSS_SELECTOR, 'div.events-group .column .hr-market-view')

    print(f"{Fore.GREEN}[+] Events found: {len(events_list)}{Style.RESET_ALL}")

    events_data = []

    for event in events_list:
        try:
            event_data = parseEvent(event)

            events_data.append(event_data)
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to parse event. Ignoring. {e.msg if hasattr(e, 'msg') else e} . Element InnerHTML {event.get_attribute('innerHTML')}{Style.RESET_ALL}")

    save_excel_file(events_data)

def main():
    print(f"{Fore.GREEN}[+] Launching Browser...{Style.RESET_ALL}")

    driver = uc.Chrome(headless=IS_HEADLESS, use_subprocess=False)
    driver.implicitly_wait(10)

    # set state cookie
    driver.get('https://app.hardrock.bet/404')
    driver.add_cookie({"name": "childSite", "value": "AZ"})
    driver.add_cookie({"name": "showCookiesBanner", "value": "false"})

    driver.get('https://app.hardrock.bet/')

    if not any(keyword in driver.title for keyword in SAFE_TITLES):
        print(f"{Fore.RED}[!] Detected Abnormal Page Title. {driver.title}. Your IP is maybe flagged. Exiting...{Style.RESET_ALL}")
        exit(1)

    # click nba button
    nba_button = driver.find_element(By.CSS_SELECTOR, 'li[data-cy="sports-tab:NBA"]')
    nba_button.click()

    # show all events
    driver.execute_script("document.documentElement.style.zoom = \"0.1\";")
    time.sleep(1) # ensure all elements are still there

    while True:
        update_excel_events(driver)

        print(f"{Fore.YELLOW}[-] Waiting {UPDATE_INTERVAL} seconds before updating excel again {Style.RESET_ALL}")

        time.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    freeze_support()

    while True:
        try:
            main()
        except TimeoutException as e:
            print(f"{Fore.RED}[!] Timed out. {e.msg}{Style.RESET_ALL}")
        except NoSuchElementException as e:
            print(f"{Fore.RED}[!] Failed to locate element. {e.msg}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error. {e.msg if hasattr(e, 'msg') else e}{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}[-] Trying again...{Style.RESET_ALL}")
        time.sleep(1)