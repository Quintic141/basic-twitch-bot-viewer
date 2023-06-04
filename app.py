from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from dotenv import load_dotenv
from threading import Thread, Event
import time, os

DRIVER_PATH = "driver\chromedriver.exe"

proxy_servers = [
     "https://www.blockaway.net",
     "https://www.croxyproxy.com",
     "https://www.croxyproxy.rocks",
     "https://www.croxy.org",
     "https://www.youtubeunblocked.live",
     "https://www.croxyproxy.net"
]

LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
STATUS_MSG = "Status - "

class ProxyViewer(Thread):
    def __init__(self, args):
       # Call the Thread class's init function
       Thread.__init__(self)
       self.driver = self.get_driver()
       self.views = args[0]
       self.proxy = args[1]
       self.twitch_username = args[2]
       self.event = args[3]
       self.driver_id = args[4]

    def run(self):
        self.start_proxy(self.driver, self.views, self.proxy, self.twitch_username)

    def get_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(executable_path=DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(15)
        return driver

    def start_proxy(self, driver, views, proxy, twitch_username):
        # Close all except 1
        for tab in range(1, len(driver.window_handles)):
            driver.switch_to.window(driver.window_handles[tab])
            driver.close()

        global closed_drivers, drivers_ok
        for v_number in range(views):
            try:
                if(v_number == views-1):
                    drivers_ok+=1
                self.print_msg(f'[{proxy}] Opening tab {v_number+1}/{views} - OK: {drivers_ok}/{used_proxies}')
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
                driver.get(proxy)        

                text_box = driver.find_element(By.ID, 'url')
                text_box.send_keys(twitch_username)
                text_box.send_keys(Keys.RETURN)

                if event.is_set():
                    closed_drivers+=1
                    self.print_msg(f'Closing proxy: {self.proxy} ({closed_drivers}/{used_proxies})')
                    self.driver.quit()                
                    return

            except:
                self.print_msg(f'Error opening tab with proxy: [{proxy}]')

        while True:
            for tab in driver.window_handles:
                if event.is_set():
                    closed_drivers+=1
                    self.print_msg(f'Closing proxy: {self.proxy} ({closed_drivers}/{used_proxies})')
                    self.driver.quit()                
                    return

                driver.switch_to.window(tab)
                try:
                    driver.refresh()
                except:
                    self.print_msg(f'Time-out [{proxy}], closing tab.')
                    driver.close()
                time.sleep(5)
    
    def print_msg(self, msg):
        print(LINE_UP, end=LINE_CLEAR)        
        print(STATUS_MSG + msg)



if __name__ == '__main__':
    print(f'> Close this app using instructions or some browsers will remaing in memory.')

    load_dotenv()
    twitch_username = os.getenv('TWITCH_CHANNEL_URL')
    used_proxies = os.getenv('USED_PROXIES') # 1 proxy -> 1 browser windows -> 1 thread
    views_x_proxy = os.getenv('VIEWS_X_PROXY')
    
    # To stop all threads
    event = Event()

    print(f'> Starting {used_proxies} proxies with {views_x_proxy} views each, for {twitch_username}\n\n')
    drivers_ok = 0

    for v in range(used_proxies):
        x = ProxyViewer(args=(views_x_proxy, proxy_servers[v%len(proxy_servers)], twitch_username, event, v,))
        x.start()

    input("ENTER to STOP...")
    print(LINE_UP, end='\r')
    closed_drivers = 0    

    # Set event so we can stop all threads with it in.
    event.set()
    print("\nClosing browsers, wait...\n")