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

# Function to execute the bot
def run_bot(action="check"):
    threading.Thread(target=bot_execution, args=(action,), daemon=True).start()

def bot_execution(action):
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

        # Switch to iframe containing login form
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

        time.sleep(5)

        # Navigate to CallManager page
        driver.get("https://commportal.calltower.com/bg/#line8005326761/main.html#/callmanager#topTabBox=Forwarding")
        logging.info("Navigated to CallManager page.")

        time.sleep(3)

        # Switch to the outer iframe
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "embedded")))

        # Switch to the inner iframe containing the checkbox
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameResizer0")))
        logging.info("Switched to iframe containing checkbox.")

        # Wait for checkbox
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div/div[3]/div[7]/div[2]/form/div/div/div/div/label/input")))

        # Check/uncheck
        if action == "check" and not checkbox.is_selected():
            checkbox.click()
            logging.info("Checked the checkbox.")
        elif action == "uncheck" and checkbox.is_selected():
            checkbox.click()
            logging.info("Unchecked the checkbox.")

        time.sleep(2)

        # Switch back to Apply button iframe
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "embedded")))
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "iFrameResizer0")))

        # Find Apply button
        apply_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[onclick="return doSubmit(\'ucfForm\');"]')))
        logging.info("Apply button found.")

        # Ensure button visibility
        driver.execute_script("arguments[0].style.display = 'block'; arguments[0].visibility = 'visible';", apply_button)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", apply_button)

        # Click Apply
        try:
            apply_button.click()
            logging.info("Clicked Apply button.")
        except Exception:
            driver.execute_script("arguments[0].click();", apply_button)
            logging.info("Clicked Apply button using JS.")

        messagebox.showinfo("Success", f"Bot action '{action}' completed successfully.")

    except Exception as e:
        logging.error(f"Error: {e}")
        messagebox.showerror("Error", f"Error: {e}")

    finally:
        driver.quit()
        logging.info("Browser closed.")

# Function to schedule the bot
def schedule_bot():
    def parse_time(date_str, hour, minute, ampm):
        try:
            if not date_str or not hour or not minute or not ampm:
                raise ValueError("Missing time inputs")

            hour = int(hour)
            minute = int(minute)

            if ampm == "PM" and hour != 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0

            formatted_time = f"{date_str} {hour:02}:{minute:02}"
            parsed_datetime = datetime.strptime(formatted_time, "%m/%d/%y %H:%M")

            return eastern_tz.localize(parsed_datetime)

        except Exception as e:
            logging.error(f"Error parsing time: {e}")
            return None

    start_time = parse_time(start_date.get(), start_hour.get(), start_minute.get(), start_ampm.get())
    end_time = parse_time(end_date.get(), end_hour.get(), end_minute.get(), end_ampm.get())

    if not start_time or not end_time:
        messagebox.showerror("Error", "Invalid start or end time.")
        return

    current_time = datetime.now(eastern_tz)

    if start_time > current_time:
        delay_start = (start_time - current_time).total_seconds()
        threading.Timer(delay_start, lambda: run_bot("check")).start()
        logging.info(f"Bot scheduled to start at {start_time.strftime('%I:%M %p %m/%d/%Y')} ET")

    if end_time > current_time:
        delay_end = (end_time - current_time).total_seconds()
        threading.Timer(delay_end, lambda: run_bot("uncheck")).start()
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
# Buttons
schedule_button = tk.Button(app, text="Schedule", command=schedule_bot)
schedule_button.grid(row=4, column=0, pady=10)

run_now_button = tk.Button(app, text="Run Now", command=lambda: run_bot("check"), bg="green", fg="white")
run_now_button.grid(row=4, column=1, pady=10)

app.mainloop()