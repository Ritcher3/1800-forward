import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime
import threading
import time
import logging
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Edge WebDriver Path
EDGE_DRIVER_PATH = r"C:\Users\rsain\Downloads\edgedriver_win64\msedgedriver.exe"

# Get current Eastern Time (EDT/EST handled automatically)
eastern_tz = pytz.timezone("America/New_York")

# Function to initialize the WebDriver
def initialize_driver():
    edge_options = Options()
    edge_options.add_argument("--disable-logging")
    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=edge_options)
    logging.info("Edge WebDriver initialized.")
    return driver

# Function to execute the bot at the scheduled time
def run_bot(action="check"):
    global driver
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password.")
        logging.error("Missing email or password.")
        return

    try:
        logging.info(f"Starting bot action: {action}")
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
        time.sleep(5)

        # Navigate directly to the new URL
        driver.get("https://commportal.calltower.com/bg/#line8004476299/main.html#/callmanager#topTabBox=Forwarding")
        logging.info("Navigated directly to CallManager page.")

        # Wait for login to process
        time.sleep(5)

        # Switch to the outer iframe
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "embedded")))

        # Switch to the inner iframe containing the checkbox
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameResizer0")))
        logging.info("Switched to the iframe containing the checkbox.")

        # Wait for the checkbox to be clickable
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[7]/div[2]/form[1]/div[1]/div[1]/div[1]/div[1]/label[1]/input[1]")))

        # Check or uncheck based on action
        if action == "check" and not checkbox.is_selected():
            checkbox.click()
            logging.info("Checked the checkbox.")
        elif action == "uncheck" and checkbox.is_selected():
            checkbox.click()
            logging.info("Unchecked the checkbox.")

        # Small delay to ensure UI updates before clicking Apply
        time.sleep(2)

        # Switch to the Apply button's iframe
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "embedded")))
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameResizer0")))

        # Find the Apply button
        apply_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[onclick="return doSubmit(\'ucfForm\');"]')))
        logging.info("Apply button found.")

        # Ensure the Apply button is visible before clicking
        driver.execute_script("arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", apply_button)

        # Scroll the Apply button into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", apply_button)

        # Click Apply (try normal click first, then JS click if needed)
        try:
            apply_button.click()
            logging.info("Clicked the Apply button successfully using normal click.")
        except Exception:
            driver.execute_script("arguments[0].click();", apply_button)
            logging.info("Clicked the Apply button using JavaScript.")

        # Show a message indicating success
        messagebox.showinfo("Success", f"Bot action '{action}' completed successfully.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

    finally:
        driver.quit()
        logging.info("Browser closed.")

# Get current Eastern Time (EDT/EST handled automatically)
eastern_tz = pytz.timezone("America/New_York")        

# Function to schedule the bot execution
def schedule_bot():
    # Function to schedule the bot execution
    def parse_time(date_str, hour, minute, ampm):
        try:
            # Ensure inputs are not empty
            if not date_str or not hour or not minute or not ampm:
                raise ValueError("Missing time inputs")

            # Convert hour and minute to integers
            hour = int(hour)
            minute = int(minute)

            # Convert 12-hour format to 24-hour format
            if ampm == "PM" and hour != 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0

            # Format the full datetime
            formatted_time = f"{date_str} {hour:02}:{minute:02}"
            parsed_datetime = datetime.strptime(formatted_time, "%m/%d/%y %H:%M")

            logging.info(f"Parsed Scheduled Time: {parsed_datetime}")
            return parsed_datetime

        except Exception as e:
            logging.error(f"Error parsing time: {e}")
            return None


    # Get values from the UI
    start_time = parse_time(start_date.get(), start_hour.get(), start_minute.get(), start_ampm.get())
    end_time = parse_time(end_date.get(), end_hour.get(), end_minute.get(), end_ampm.get())


    if not start_time or not end_time:
        return

    # Convert times to Eastern Timezone
    start_time = eastern_tz.localize(start_time)
    end_time = eastern_tz.localize(end_time)
    current_time = datetime.now(eastern_tz)

    if start_time > current_time:
        threading.Timer((start_time - current_time).total_seconds(), lambda: print("Bot Start Action")).start()
        logging.info(f"Bot scheduled to start at {start_time.strftime('%I:%M %p %m/%d/%Y')} ET")

    if end_time > current_time:
        threading.Timer((end_time - current_time).total_seconds(), lambda: print("Bot End Action")).start()
        logging.info(f"Bot scheduled to stop at {end_time.strftime('%I:%M %p %m/%d/%Y')} ET")

    messagebox.showinfo("Scheduled", "Bot scheduled successfully!")

# Create Tkinter UI
app = tk.Tk()
app.title("CommPortal Automation")
app.geometry("500x250")

# Email & Password
tk.Label(app, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
email_entry = tk.Entry(app, width=40)
email_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

tk.Label(app, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
password_entry = tk.Entry(app, width=40, show="*")
password_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# Define the values for hours, minutes, and AM/PM
hours = [str(i) for i in range(1, 13)]  # 1 to 12
minutes = ["00", "15", "30", "45"]  # Available minute intervals
ampm_options = ["AM", "PM"]  # AM/PM options

# Start Time Row
tk.Label(app, text="Start Time:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
start_date = DateEntry(app, width=10)
start_date.grid(row=2, column=1, padx=5, pady=5, sticky="w")
start_hour = ttk.Combobox(app, values=hours, width=3)
start_hour.grid(row=2, column=2, padx=5, pady=5, sticky="w")
start_hour.set("1")  # Default value (1 PM or AM depending on selection)

start_minute = ttk.Combobox(app, values=minutes, width=3)
start_minute.grid(row=2, column=3, padx=5, pady=5, sticky="w")
start_minute.set("00")  # Default value (00 minutes)

start_ampm = ttk.Combobox(app, values=ampm_options, width=5)
start_ampm.grid(row=2, column=4, padx=5, pady=5, sticky="w")
start_ampm.set("AM")  # Default value (AM)

# End Time Row
tk.Label(app, text="End Time:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
end_date = DateEntry(app, width=10)
end_date.grid(row=3, column=1, padx=5, pady=5, sticky="w")
end_hour = ttk.Combobox(app, values=hours, width=3)
end_hour.grid(row=3, column=2, padx=5, pady=5, sticky="w")
end_hour.set("1")  # Default value (1 PM or AM depending on selection)

end_minute = ttk.Combobox(app, values=minutes, width=3)
end_minute.grid(row=3, column=3, padx=5, pady=5, sticky="w")
end_minute.set("00")  # Default value (00 minutes)

end_ampm = ttk.Combobox(app, values=ampm_options, width=5)
end_ampm.grid(row=3, column=4, padx=5, pady=5, sticky="w")
end_ampm.set("AM")  # Default value (AM)


# Schedule Button
schedule_button = tk.Button(app, text="Schedule", command=schedule_bot)
schedule_button.grid(row=4, column=0, columnspan=5, pady=10)

app.mainloop()