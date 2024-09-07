import json
import os
import requests
import platform
import webbrowser
import time  # Import the time module
from datetime import datetime
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
LOGIN_USERNAME = "username"  # Replace with the login username
PASSWORD = "password"  # Replace with your actual password
INSTAGRAM_USER_USERNAME = "example_user"  # Replace with the Instagram username to track
INTERVAL = 180  # Seconds
BASE_DIR = "old_stuff_but_usable"
DRIVER_DIR = os.path.join(BASE_DIR, "drivers")

# Ensure the driver directory exists
os.makedirs(DRIVER_DIR, exist_ok=True)

def get_default_browser():
    """Detects the default browser."""
    try:
        browser = webbrowser.get()
        if "chrome" in str(browser).lower():
            return "chrome"
        elif "firefox" in str(browser).lower():
            return "firefox"
    except webbrowser.Error:
        pass

    # Check for Firefox ESR explicitly
    if os.path.exists("/bin/firefox-esr"):
        return "firefox"

    return None

def download_driver(browser):
    """Downloads the appropriate driver for the detected browser."""
    if browser == "chrome":
        url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
        driver_path = os.path.join(DRIVER_DIR, "chromedriver")
    elif browser == "firefox":
        url = "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz"
        driver_path = os.path.join(DRIVER_DIR, "geckodriver")
    else:
        raise ValueError("Unsupported browser")

    response = requests.get(url)
    response.raise_for_status()

    zip_path = driver_path + ".zip" if browser == "chrome" else driver_path + ".tar.gz"
    with open(zip_path, 'wb') as file:
        file.write(response.content)

    # Extract the driver
    if browser == "chrome":
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(DRIVER_DIR)
    elif browser == "firefox":
        import tarfile
        with tarfile.open(zip_path, 'r:gz') as tar_ref:
            tar_ref.extractall(DRIVER_DIR)

    os.chmod(driver_path, 0o755)  # Make the driver executable
    return driver_path

def get_timestamp():
    """Returns the current timestamp in 'YYYY-MM-DD-HH-MM-SS' format."""
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

def ensure_directories(log_dir):
    """Creates necessary directories for storing data within the log directory."""
    directories = ["profile_pages", "profile_data", "screenshots", "profile_pictures"]
    for dir_name in directories:
        dir_path = os.path.join(log_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)

def ensure_log_directory():
    """Creates a directory for logs based on the current timestamp."""
    timestamp = get_timestamp()
    log_dir = os.path.join(BASE_DIR, "logs", timestamp)
    os.makedirs(log_dir, exist_ok=True)
    ensure_directories(log_dir)
    return log_dir

def log_message(message, level="INFO", log_dir=None):
    """Logs messages to a file with timestamp and severity level."""
    if log_dir is None:
        log_dir = ensure_log_directory()
    log_file_path = os.path.join(log_dir, "logfile.log")
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{get_timestamp()} - {level} - {message}\n")
    color = {
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED
    }.get(level, Fore.WHITE)
    print(f"-----------------\n{color}{level}: {message}{Style.RESET_ALL}\n-----------------")

def take_screenshot(driver, filename):
    """Takes a screenshot and saves it."""
    driver.save_screenshot(filename)
    log_message(f"Screenshot saved to {filename}")

def initialize_browser():
    """Initializes and returns a Selenium WebDriver instance."""
    browser = get_default_browser()
    if not browser:
        raise ValueError("No supported default browser found")

    driver_path = download_driver(browser)

    if browser == "chrome":
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--lang=en")  # Set language to English
        service = ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    elif browser == "firefox":
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-popup-blocking")
        firefox_options.add_argument("--disable-notifications")
        firefox_options.set_preference("intl.accept_languages", "en-US, en")  # Set language to English
        service = FirefoxService(executable_path=driver_path)
        driver = webdriver.Firefox(service=service, options=firefox_options)

    return driver

def click_button_by_coordinates(driver, element):
    """Click an element using its coordinates."""
    location = element.location
    size = element.size
    x = location['x'] + size['width'] // 2
    y = location['y'] + size['height'] // 2
    actions = ActionChains(driver)
    actions.move_by_offset(x, y).click().perform()
    log_message(f"Clicked button at coordinates: ({x}, {y})")

def login_to_instagram(driver):
    """Logs into Instagram and handles any prompts for saving login information."""
    driver.get("https://www.instagram.com/accounts/login/")
    
    log_dir = ensure_log_directory()
    take_screenshot(driver, os.path.join(log_dir, "login_page_loaded.png"))
    
    try:
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.NAME, "username")))

        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys(LOGIN_USERNAME)
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)
        
        try:
            save_info_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save info')]"))
            )
            save_info_button.click()
            log_message("Clicked 'Save Info' button.", log_dir=log_dir)
        except Exception as e:
            log_message(f"No 'Save Info' button found or could not be clicked: {e}", "WARNING", log_dir=log_dir)
            take_screenshot(driver, os.path.join(log_dir, "no_save_info_button.png"))

        try:
            not_now_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
            )
            not_now_button.click()
            log_message("Clicked 'Not Now' button for notifications.", log_dir=log_dir)
        except Exception as e:
            log_message(f"No 'Not Now' button for notifications found or already handled: {e}", "WARNING", log_dir=log_dir)
        
        time.sleep(5)
        
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Instagram']")))
            log_message("Logged in successfully. SVG logo detected.", log_dir=log_dir)
        except Exception as e:
            take_screenshot(driver, os.path.join(log_dir, "login_svg_logo_not_found.png"))
            log_message(f"Failed to detect Instagram homepage header (logo): {e}", "ERROR", log_dir=log_dir)
            raise
    
    except Exception as e:
        take_screenshot(driver, os.path.join(log_dir, "login_page_elements_not_found.png"))
        log_message(f"Login page elements not found: {e}", "ERROR", log_dir=log_dir)
        raise

def download_image(url, filename):
    """Downloads an image from a URL and saves it to a file."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            file.write(response.content)
        log_message(f"Image saved to {filename}")
    except requests.RequestException as e:
        log_message(f"Failed to download image: {e}", "ERROR")

def get_profile_details(username, driver):
    """Fetches and returns profile details."""
    driver.get(f"https://www.instagram.com/{username}/")

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "header")))

        try:
            followers = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers/')]/span"))
            ).text
        except NoSuchElementException:
            followers = "Followers count not found"

        try:
            followings = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following/')]/span"))
            ).text
        except NoSuchElementException:
            followings = "Followings count not found"

        try:
            bio = driver.find_element(By.CSS_SELECTOR, "span._ap3a._aaco._aacu._aacx._aad7._aade").text
        except NoSuchElementException:
            bio = "Bio not found"

        try:
            profile_photo_url = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.xpdipgo"))
            ).get_attribute("src")
        except NoSuchElementException:
            profile_photo_url = "Profile photo not found"

        return {
            "followers": followers,
            "followings": followings,
            "bio": bio,
            "profile_photo_url": profile_photo_url
        }
    
    except TimeoutException as e:
        log_dir = ensure_log_directory()
        take_screenshot(driver, os.path.join(log_dir, "profile_details_timeout.png"))
        log_message(f"Timeout while retrieving profile details: {e}", "ERROR", log_dir=log_dir)
        raise
    except NoSuchElementException as e:
        log_dir = ensure_log_directory()
        take_screenshot(driver, os.path.join(log_dir, "profile_details_no_element.png"))
        log_message(f"Element not found: {e}", "ERROR", log_dir=log_dir)
        raise
    except Exception as e:
        log_dir = ensure_log_directory()
        take_screenshot(driver, os.path.join(log_dir, "profile_details_failed.png"))
        log_message(f"Failed to retrieve profile details: {e}", "ERROR", log_dir=log_dir)
        raise

def save_profile_page(username, filename):
    """Downloads and saves the profile page as HTML."""
    url = f"https://www.instagram.com/{username}/"
    try:
        log_message(f"Downloading profile page from {url}")
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        log_message(f"Profile page saved to {filename}")
    except requests.RequestException as e:
        log_message(f"Failed to download profile page: {e}", "ERROR")

def save_to_database(details, timestamp):
    """Saves profile details to the SQLite database."""
    conn = sqlite3.connect('profile_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile_details (
            timestamp TEXT PRIMARY KEY,
            followers TEXT,
            followings TEXT,
            bio TEXT,
            profile_photo_url TEXT
        )
    ''')
    cursor.execute('''
        INSERT OR REPLACE INTO profile_details (timestamp, followers, followings, bio, profile_photo_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, details['followers'], details['followings'], details['bio'], details['profile_photo_url']))
    conn.commit()
    conn.close()

def load_previous_details_from_db():
    """Loads the most recent profile details from the database."""
    conn = sqlite3.connect('profile_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile_details (
            timestamp TEXT PRIMARY KEY,
            followers TEXT,
            followings TEXT,
            bio TEXT,
            profile_photo_url TEXT
        )
    ''')
    cursor.execute("SELECT * FROM profile_details ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'followers': row[1],
            'followings': row[2],
            'bio': row[3],
            'profile_photo_url': row[4]
        }
    return None

def log_changes(old_details, new_details, log_dir):
    """Logs the changes between old and new profile details."""
    timestamp = get_timestamp()
    filename = os.path.join(log_dir, "profile_data", f"profile_changes_{timestamp}.json")
    with open(filename, 'w') as log_file:
        json.dump({
            "old_content": old_details,
            "new_content": new_details
        }, log_file, indent=2)
    log_message(f"Changes logged to {filename}", log_dir=log_dir)

def save_profile_photo(url, filename):
    """Downloads and saves the profile photo."""
    if url != "Profile photo not found":
        download_image(url, filename)
    else:
        log_message("Profile photo URL not found. Skipping download.", "WARNING")

def track_profile_details():
    """Tracks profile details periodically."""
    log_dir = ensure_log_directory()
    previous_details = load_previous_details_from_db()
    
    # Prepare paths for saved profile picture
    previous_profile_photo_path = os.path.join(log_dir, "profile_pictures", "profile_picture_previous.jpg")

    driver = initialize_browser()
    try:
        login_to_instagram(driver)
    except Exception as e:
        log_message(f"Failed to log in. Error: {e}", "ERROR", log_dir=log_dir)
        driver.quit()
        return

    while True:
        start_time = time.time()
        try:
            current_details = get_profile_details(INSTAGRAM_USER_USERNAME, driver)
            timestamp = get_timestamp()
            profile_photo_path = os.path.join(log_dir, "profile_pictures", f"profile_picture_{timestamp}.jpg")
            
            # Save profile details to database
            save_to_database(current_details, timestamp)
            # Save the profile page as HTML
            profile_page_path = os.path.join(log_dir, "profile_pages", f"profile_page_{timestamp}.html")
            save_profile_page(INSTAGRAM_USER_USERNAME, profile_page_path)

            # Save and compare profile photo
            save_profile_photo(current_details['profile_photo_url'], profile_photo_path)
            if previous_details:
                if previous_details['profile_photo_url'] != current_details['profile_photo_url']:
                    # Save the previous profile photo for comparison
                    if os.path.exists(previous_profile_photo_path):
                        os.rename(previous_profile_photo_path, os.path.join(log_dir, "profile_pictures", f"profile_picture_{timestamp}_previous.jpg"))
                    # Update the path to the current profile photo
                    os.rename(profile_photo_path, previous_profile_photo_path)
                    log_message("Profile photo has changed.", log_dir=log_dir)

            if previous_details is None:
                previous_details = current_details
            elif current_details != previous_details:
                log_changes(previous_details, current_details, log_dir)
                screenshot_path = os.path.join(log_dir, "screenshots", f"profile_page_{timestamp}.png")
                take_screenshot(driver, screenshot_path)
                previous_details = current_details

            log_message(f"{INSTAGRAM_USER_USERNAME} has {current_details['followers']} followers, {current_details['followings']} followings.", log_dir=log_dir)
            log_message(f"Bio: {current_details['bio']}", log_dir=log_dir)
            log_message(f"Profile Photo URL: {current_details['profile_photo_url']}", log_dir=log_dir)

        except Exception as e:
            log_message(f"An error occurred: {e}", "ERROR", log_dir=log_dir)

        while time.time() - start_time < INTERVAL:
            elapsed_time = time.time() - start_time
            remaining_time = INTERVAL - elapsed_time
            print(f"\rTime until next check: {int(remaining_time)} seconds", end='', flush=True)
            time.sleep(1)

    driver.quit()

if __name__ == "__main__":
    track_profile_details()