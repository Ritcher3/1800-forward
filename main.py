import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Edge WebDriver Path
EDGE_DRIVER_PATH = r"C:\Users\rsain\Downloads\edgedriver_win64\msedgedriver.exe"

# Function to initialize the WebDriver
def initialize_driver():
    edge_options = Options()
    edge_options.add_argument("--disable-logging")
    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=edge_options)
    logging.info("Edge WebDriver initialized.")
    return driver

# Function to handle login process
# Function to handle login process
def login():
    global driver
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    
    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password.")
        logging.error("Missing email or password.")
        return
    
    try:
        logging.info("Starting login process.")
        driver = initialize_driver()
        driver.get("https://commportal.calltower.com/bg/#bg/login.html")
        logging.info("Navigated to CommPortal login page.")
        
        wait = WebDriverWait(driver, 20)
        
        # Switch to the iframe containing the login form
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='embedded']")))
        
        # Enter email
        email_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='DirectoryNumberDummy']")))
        email_field.send_keys(email)
        logging.info("Entered email.")
        
        # Enter password
        password_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='Password']")))
        password_field.send_keys(password)
        logging.info("Entered password.")
        
        # Submit login form
        password_field.submit()
        logging.info("Submitted login form.")
        
        # Wait for login to process
        time.sleep(5)  # Adjusted sleep time
        
        # Navigate directly to the new URL
        driver.get("https://commportal.calltower.com/bg/#line8005326761/main.html#/callmanager#topTabBox=Forwarding")
        logging.info("Navigated directly to CallManager page.")

        # Wait for login to process
        time.sleep(5)  # Adjusted sleep time

         # Switch to the iframe containing the login form
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='embedded']")))
        
        # Switch to the iframe containing the checkbox
        iframe = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameResizer0")))
        logging.info("Switched to the iframe containing the checkbox.")
        
        # Wait for the checkbox to be clickable and click it using the provided XPath
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[7]/div[2]/form[1]/div[1]/div[1]/div[1]/div[1]/label[1]/input[1]")))
        checkbox.click()
        logging.info("Clicked the checkbox.")

        
        # Small delay to ensure UI updates before clicking Apply
        time.sleep(3)

        # Ensure we're in the correct iframe hierarchy
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "embedded")))
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameResizer0")))

        # Wait for the Apply button using the correct selector
        apply_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[onclick="return doSubmit(\'ucfForm\');"]')))
        logging.info("Apply button found.")

        # Ensure the Apply button is visible before clicking
        driver.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", apply_button)

        # Scroll the Apply button into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", apply_button)

        # Small delay before clicking
        time.sleep(1)

        # Click Apply (try normal click first, then JS click if needed)
        try:
            apply_button.click()
            logging.info("Clicked the Apply button successfully using normal click.")
        except Exception:
            driver.execute_script("arguments[0].click();", apply_button)
            logging.info("Clicked the Apply button using JavaScript.")

        # Show a message indicating success
        messagebox.showinfo("Success", "Login successful, navigated to CallManager page, and clicked the Apply button.")

    except Exception as e:
        logging.error(f" An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
    
    # Do not close the driver after navigating
    # Uncomment the next line if you want to close the driver at some point
    # driver.quit()


# Create Tkinter UI
app = tk.Tk()
app.title("CommPortal Login Automation")
app.geometry("400x300")
app.resizable(False, False)

email_label = tk.Label(app, text="Email:")
email_label.pack(pady=5)
email_entry = tk.Entry(app, width=40)
email_entry.pack()

password_label = tk.Label(app, text="Password:")
password_label.pack(pady=5)
password_entry = tk.Entry(app, width=40, show="*")
password_entry.pack()

login_button = tk.Button(app, text="Login", command=login)
login_button.pack(pady=10)

app.mainloop()
