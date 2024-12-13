import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from selenium.webdriver.remote.webelement import WebElement


IS_HEADLESS = True # Hide automated Browser
SAFE_TITLES = ["Hard Rock"] # list of titles page scraped should give

def parseEvent(event: WebElement):
    team_names_el = event.find_elements(By.CSS_SELECTOR, ".participants .show-for-medsmall")

    team_names = [team_name_el.text for team_name_el in team_names_el]

    if len(team_names) != 2:
        raise Exception(f"Team names length isn't 2. {team_names}")

    spread_bh = event.find_element(By.CSS_SELECTOR, "div[data-cy=\"wager-button:Spread BH\"] .selection-line-value").text
    spread_ah = event.find_element(By.CSS_SELECTOR, "div[data-cy=\"wager-button:Spread AH\"] .selection-line-value").text

    total_over = event.find_element(By.CSS_SELECTOR, "div[data-cy=\"wager-button:Total Points Over\"] .selection-line-value").text
    total_under = event.find_element(By.CSS_SELECTOR, "div[data-cy=\"wager-button:Total Points Under\"] .selection-line-value").text

    win_b = event.find_element(By.CSS_SELECTOR, "div[data-cy=\"wager-button:To Win B\"]").text
    win_a = event.find_element(By.CSS_SELECTOR, "div[data-cy=\"wager-button:To Win A\"]").text

    teams = [
        {
            "team_name": team_names[0],
            "spread": spread_bh,
            "total_pts": total_over.split(" ")[1],
            "win": win_b
        },
        {
            "team_name": team_names[1],
            "spread": spread_ah,
            "total_pts": total_under.split(" ")[1],
            "win": win_a
        }
    ]

    return teams

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

    # show all events
    driver.execute_script("document.documentElement.style.zoom = \"0.1\";")
    time.sleep(1) # ensure all elements are still there

    events_list = driver.find_elements(By.CSS_SELECTOR, 'div.events-group .column .hr-market-view')

    print(f"[+] Events found: {len(events_list)}")

    for event in events_list:
        try:
            data = parseEvent(event)
        except Exception as e:
            print("[!] Failed to parse event")

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