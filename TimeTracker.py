import tkinter as tk
from tkinter import filedialog
import pyperclip
import pyautogui
import pygetwindow
import re
from datetime import datetime, timedelta
import pathlib
import configparser
import os
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import subprocess
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs import Messagebox
import shutil
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from screeninfo import get_monitors
import ctypes as ct
from win11toast import toast
from pytz import timezone
import pytz
import webbrowser
import threading
import sys
from tendo import singleton

try:
    me = singleton.SingleInstance()
except singleton.SingleInstanceException:
    sys.exit(-1)

message_box_shown = False
lunch_message_box_shown = False
current_date = datetime.today()

config = configparser.ConfigParser()

documents_path = pathlib.Path.home() / 'Documents'

config_file_path = documents_path / 'TimeTracker.ini'

task_file_path = documents_path / 'TimeTracker_Tasks'
script_directory = os.path.dirname(os.path.abspath(__file__))
readme_file_path = os.path.join(script_directory, 'README.md')

def save_position():
    coordinates = [window.winfo_x(), window.winfo_y()]
    config["WindowPosition"] = {
    "X": str(coordinates[0]),
    "Y": str(coordinates[1])
    }
    with open(config_file_path, "w") as config_file:
        config.write(config_file)

def set_position():
    config.read(config_file_path)
    stored_coordinates = None

    def get_active_displays():
        active_displays = []
        
        for monitor in get_monitors():
            active_displays.append({
                'name': monitor.name,
                'width': monitor.width,
                'height': monitor.height,
                'x': monitor.x,
                'y': monitor.y
            })
            
        return active_displays

    def valid_coordinates(saved_x, saved_y):
        active_displays = get_active_displays()
        
        for display in active_displays:
            if (
                saved_x >= display['x'] and
                saved_x < display['x'] + display['width'] and
                saved_y >= display['y'] and
                saved_y < display['y'] + display['height']
            ):
                return True
        
        return False

    if "WindowPosition" in config:
        stored_coordinates = (int(config["WindowPosition"]["X"]), int(config["WindowPosition"]["Y"]))
        saved_x = stored_coordinates[0]
        saved_y = stored_coordinates[1]

        if valid_coordinates(saved_x, saved_y):
            try:
                # Apply stored coordinates if the stored screen matches the current screen
                window.geometry(f"+{stored_coordinates[0]}+{stored_coordinates[1]}")
            except Exception as e:
                print(e)
        else:
            center(window)
    else:
        center(window)

# Read from config file
def read_config():
    global style
    config.read(config_file_path)

    current_date = datetime.today()
    current_date = str(current_date.date())

    entry_keys_to_check = [
    ('clock_in_time', clock_in_time_display),
    ('clock_out_lunch_time', clock_out_1_time_display),
    ('clock_in_lunch_time', clock_in_2_time_display)
    ]

    for key, display in entry_keys_to_check:
        try:
            value_parts = config.get('Times', key).split('|')
            if len(value_parts) > 1 and value_parts[1] != current_date:
                display.state(['invalid'])
            elif len(value_parts) == 1:
                display.state(['invalid'])
        except Exception as e:
            print(e)
            display.state(['invalid'])

    time_keys_to_set = [
        'clock_in_time', 'clock_out_lunch_time', 'clock_in_lunch_time','clock_out_time', 
        'lunch_by_time', 'add_time_1', 'add_time_2','time_out', 'pto_check', 'min_lunch'
    ]

    for key in time_keys_to_set:
        try:
            value = config.get('Times', key)
            if '|' in value:
                value = value.split('|')[0]
            globals()[key].set(value)
        except Exception as e:
            pass    

    menu_keys_to_set = [
        'lunch_by_timer','clock_out_timer','alarm_var', 'lunch_alarm_var', 'window_mode', 
        'selected_sound', 'font_size', 'ca_toggle', 'tz_toggle', 'ae_toggle'
        ]

    for key in menu_keys_to_set:
        try:
            value = config.get('Menu', key)
            globals()[key].set(value)
        except Exception as e:
            pass

    try:
        window_mode_value = window_mode.get()
        style.theme_use(themename=window_mode_value)
        ca_assoc_toggle()
        time_zone_toggle()
        add_entries_toggle()
    except Exception as e:
        pass

    file_name = str(current_date).split(' ')[0]+'.txt'
    file_location = os.path.join(task_file_path, file_name)
    if not os.path.exists(task_file_path):
        os.makedirs(task_file_path)
    if not os.path.exists(os.path.join(file_location)):
            open(file_location, "w")

# Write to config file
def write_config(index, state=None):
    # open config file
    config.read(config_file_path)

    if not config.has_section('Times'):
        config.add_section('Times')
        config.set('Times', 'clock_in_time', '8:00:00 AM')
        config.set('Times', 'clock_out_lunch_time', '12:00:00 PM')
        config.set('Times', 'clock_in_lunch_time', '1:00:00 PM')

    current_date = datetime.today()
    current_date = str(current_date.date())
    if index == 'clock_in_time':
        if state == 'invalid':
            config['Times']['clock_in_time'] = clock_in_time.get()
        else:
            config['Times']['clock_in_time'] = clock_in_time.get()+"|"+current_date
    elif index == 'clock_out_lunch_time':
        if state == 'invalid':
            config['Times']['clock_out_lunch_time'] = clock_out_lunch_time.get()
        else:
            config['Times']['clock_out_lunch_time'] = clock_out_lunch_time.get()+"|"+current_date
    elif index == 'clock_in_lunch_time':
        if state == 'invalid':
            config['Times']['clock_in_lunch_time'] = clock_in_lunch_time.get()
        else:
            config['Times']['clock_in_lunch_time'] = clock_in_lunch_time.get()+"|"+current_date
    elif index == 'times':
            config['Times']['clock_out_time'] = clock_out_time.get()
            config['Times']['lunch_by_time'] = lunch_by_time.get()
            config['Times']['add_time_1'] = add_time_1.get()
            config['Times']['add_time_2'] = add_time_2.get()
            config['Times']['time_out'] = time_out.get()
            config['Times']['pto_check'] = str(pto_check.get())
            config['Times']['min_lunch'] = minimum_lunch.get()
    elif index == 'menu':
        config['Menu'] = {
            'alarm_var': str(alarm_var.get()),
            'lunch_alarm_var': lunch_alarm_var.get(),
            'window_mode': window_mode.get(),
            'selected_sound': selected_sound.get(),
            'lunch_by_timer': lunch_by_timer.get(),
            'clock_out_timer': clock_out_timer.get(),
            'font_size': font_size.get(),
            'ca_toggle': ca_toggle.get(),
            'tz_toggle': tz_toggle.get(),
            'ae_toggle': ae_toggle.get()
        }
    elif index == 'sound':
        sound_var = custom_sound_name.get()
        next_index = 1
        
        if 'Sounds' in config:
            existing_indexes = [int(key.split('_')[1]) for key in config['Sounds'] if key.startswith('index_')]
            if existing_indexes:
                next_index = max(existing_indexes) + 1
            config['Sounds'][f"index_{next_index}"] = sound_var
        else:
            config['Sounds'] = {
                f"index_{next_index}": sound_var
            }
    # write to config file
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

# Function to clear additional times
def clear_add_times():
    add_time_1.set("12:00:00 PM")
    add_time_2.set("12:00:00 PM")
    write_config('times')
    update()

# Function to handle time update button click
def grab_text(index):
    try:
        browser = check_browser_window()
        if browser == "Chrome":
            # Search for the Chrome browser window
            browser_window = pyautogui.getWindowsWithTitle('Google Chrome')[0]
        elif browser == "Edge":
            browser_window = pyautogui.getWindowsWithTitle('Edge')[0]
    

        # Activate the browser window
        browser_window.activate()

        # Simulate Ctrl+A (select all) and Ctrl+C (copy) keyboard shortcuts
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')

        retries = 0

        while retries < 3:
            try:
                # Simulate Ctrl+A (select all) and Ctrl+C (copy) keyboard shortcuts
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'c')
                break  # Break out of the loop if successful
            except Exception as e:
                retries += 1
                if retries >= 3:
                    print("Error", f"Clipboard operation failed after 3 retries.")
                else:
                    print("Warning", f"Clipboard operation failed. Retrying in 1 second...")
                    time.sleep(0.5)  # Wait for .5 seconds before retrying

        # Get the text from the clipboard
        text = pyperclip.paste()

        pyautogui.middleClick()

        time_window = pyautogui.getWindowsWithTitle('TimeTracker')[0]
        time_window.activate()

        # Use regex to extract the time from the grabbed text
        match = re.search(r"((Checked|Clocked) (in|out) at )?(\d{1,2}:\d{2}(:\d{2})? [APM]+)", text)
        if match:
            grabbed_time_str = match.group(4)
            if grabbed_time_str.count(":") == 1:
                hours, minutes, am_pm = re.split(r'[: ]', grabbed_time_str)
                grabbed_time_str = f"{hours}:{minutes}:00 {am_pm}"
            grabbed_time = datetime.strptime(grabbed_time_str, "%I:%M:%S %p")
            grabbed_time = format_time(grabbed_time)

            # Update the corresponding time based on the button index
            if index == "clock_in":
                clock_in_time.set(grabbed_time)
                write_config('clock_in_time')
                clock_in_time_display.state(['!invalid'])
            elif index == "clock_out":
                clock_out_lunch_time.set(grabbed_time)
                write_config('clock_out_lunch_time')
                clock_out_1_time_display.state(['!invalid'])
            elif index == "clock_in_2":
                clock_in_lunch_time.set(grabbed_time)
                write_config('clock_in_lunch_time')
                clock_in_2_time_display.state(['!invalid'])
            elif index == "add_time_1":
                add_time_1.set(grabbed_time)
                write_config('times')
            elif index == "add_time_2":
                add_time_2.set(grabbed_time)
                write_config('times')

            # Update times with new data
            update()

        else:
            show_info("Warning", "Unable to find a valid time in the grabbed text.")

    except Exception as e:
        show_info("Error", str(e))

    window.focus_set()

# Check which browser is being used
def check_browser_window():
    # Get the list of windows
    windows = pygetwindow.getAllTitles()

    # Check if Microsoft Edge window is open
    for window in windows:
        if re.search('Microsoft..Edge', window):
            return "Edge"

    # Check if Chrome window is open
    for window in windows:
        if "Google Chrome" in window:
            return "Chrome"

    # If neither Chrome nor Microsoft Edge window is found
    return None

# Function to update lunch by time and clock out time
def update():
    global message_box_shown
    message_box_shown = False

    if clock_in_time.get()=="" or clock_out_lunch_time.get()=="" or clock_in_lunch_time.get()=="":
        return

    # Calculate time worked, lunch by time, and lunch duration
    time_1 = datetime.strptime(clock_in_time.get(), "%I:%M:%S %p")
    time_2 = datetime.strptime(clock_out_lunch_time.get(), "%I:%M:%S %p")
    time_3 = datetime.strptime(clock_in_lunch_time.get(), "%I:%M:%S %p")

    time_worked = time_2 - time_1
    lunch_time = time_1 + timedelta(hours=4,minutes=59)
    lunch_duration = time_3 - time_2

    clock_out = timedelta(hours=8) - time_worked
    clock_out = time_3 + clock_out

    # See if additional times were captured and add this time to clock out time
    if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+",add_time_1.get()) and re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+",add_time_2.get()):
        time_clocked_out = datetime.strptime(add_time_2.get(), "%I:%M:%S %p") - datetime.strptime(add_time_1.get(), "%I:%M:%S %p")
        
        if pto_check.get():
            clock_out = timedelta(hours=8) - time_worked
            clock_out = time_3 + clock_out
        else:
            # Calculate new clock out time
            clock_out = clock_out + time_clocked_out

    # Calculate minimum lunch
    min_lunch = time_2 + timedelta(minutes=30)

    # Update the total work hours
    minimum_lunch.set(format_time(min_lunch))
    lunch_by_time.set(format_time(lunch_time))
    clock_out_time.set(format_time(clock_out))
    time_out.set(round((time_clocked_out.seconds / 60 / 60), 2))
    write_config('times')

# Convert time variable back to string and remove leading zeros from hour
def format_time(time):
    # Assuming you have a datetime object called `clock_out`
    # Convert the datetime object to a string
    try:
        time_str = time.strftime('%I:%M:%S %p')
    except:
        time_str = time

    # Remove leading zeros from the hour component
    try:
        time_parts = time_str.split(':')
        hour = str(int(time_parts[0])).strip()

        # Construct the updated time string
        updated_time_str = f"{hour}:{time_parts[1]}:{time_parts[2]}"

        return updated_time_str
    except:
        return time_str
        
    

# Function to update clock out and lunch by when manual time is entered
def handle_keypress(event, entry_id):
    # Function to be called when any key is pressed
    # Use regex to extract the time from the grabbed text
    # Update the corresponding time based on the button index
    if entry_id == "Entry 1":
        time = clock_in_time_display.get().strip()
        clock_in_time_display.state(['!invalid'])
        if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+",time):
            clock_in_time.set(format_time(time))
            update()
            write_config('clock_in_time')
            window.update()
    elif entry_id == "Entry 2":
        time = clock_out_1_time_display.get().strip()
        clock_out_1_time_display.state(['!invalid'])
        if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+", time):
            clock_out_lunch_time.set(format_time(time))
            update()
            write_config('clock_out_lunch_time')
            window.update()
    elif entry_id == "Entry 3":
        time = clock_in_2_time_display.get().strip()
        clock_in_2_time_display.state(['!invalid'])
        if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+", time):
            clock_in_lunch_time.set(format_time(time))
            update()
            write_config('clock_in_lunch_time')
            window.update()
    elif entry_id == "Entry 4":
        time = add_time_1_display.get().strip()
        if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+", time):
            add_time_1.set(format_time(time))
            update()
            write_config('times')
            window.update()
    elif entry_id == "Entry 5":
        time = add_time_2_display.get().strip()
        if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+", time):
            add_time_2.set(format_time(time))
            update()
            write_config('times')
            window.update()
    elif entry_id == 'readonly':
        update()
        update_time()

# Function to center window
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('+{}+{}'.format(x, y))
    win.deiconify()

def show_info(title, message):

    result = tk.BooleanVar()

    # Create a semi-transparent canvas
    canvas = ttk.Canvas(window, highlightthickness=0)
    canvas.place(relwidth=1, relheight=1, anchor='nw')
    canvas.update_idletasks()  # Update to ensure accurate measurements
        
    def on_close():
        result.set(False)
        top.destroy()
        canvas.destroy()

    def on_ok():
        result.set(True)
        top.destroy()
        canvas.destroy()

    if len(message) > 50:
        width = 600
    else:
        width = 200
    padding = 20

    # Create a temporary label to calculate the width and height needed for the message
    temp_label = ttk.Label(window, text=message, wraplength=width-2*padding)
    temp_label.update_idletasks()  # Update to ensure accurate measurements

    height = temp_label.winfo_reqheight() + 4*padding + 32 # Account for 2 times padding for each of the two widgets

    # Calculate the position of the message box in relation to the main window
    x_window = window.winfo_x()
    y_window = window.winfo_y()
    gui_width = window.winfo_width()
    gui_height = window.winfo_height()

    x = x_window + (gui_width - width) // 2
    y = y_window + (gui_height - height) // 2

    top = ttk.Toplevel(window)
    top.lift()
    top.title(title)
    top.geometry(f"{width}x{height}+{x}+{y}")

    label = ttk.Label(top, text=message, wraplength=width-2*padding)
    label.pack(padx=padding, pady=padding, side='top')

    ok_button = ttk.Button(top, text="OK", command=on_ok)
    ok_button.pack(pady=padding, padx=padding, side='bottom')

    top.focus_set()

    top.protocol("WM_DELETE_WINDOW", on_close)

    top.transient(window)  # Associate the messagebox with the main window
    top.grab_set()  # Make the messagebox modal
    top.focus_force()
    top.wait_window()  # Wait for the Toplevel window to be destroyed
    
    return result

def update_time():
    global default_color
    global message_box_shown
    global lunch_message_box_shown

    current_time = format_time(time)
    time_left = abs(datetime.strptime(clock_out_time.get(), "%I:%M:%S %p") - datetime.strptime(current_time, "%I:%M:%S %p"))
    time_left_lunch = abs(datetime.strptime(lunch_by_time.get(), "%I:%M:%S %p") - datetime.strptime(current_time, "%I:%M:%S %p"))
    
    if clock_out_timer.get() and ('invalid' not in clock_in_time_display.state()):
        if datetime.strptime(current_time, "%I:%M:%S %p") > datetime.strptime(clock_out_time.get(), "%I:%M:%S %p"):
            time_label.config(text="")
            window.after(500, update_time)
            return
        else:
            if datetime.strptime(current_time, "%I:%M:%S %p") >= (datetime.strptime(clock_out_time.get(), "%I:%M:%S %p") - timedelta(minutes=1)):
                if not message_box_shown:
                    message_box_shown = True
                    default_color.set(time_label.cget('foreground'))
                    time_label.config(foreground='red')
                    if alarm_var:
                        toast_alarm()
            else:
                if time_label.cget('foreground') == 'red':
                    time_label.config(foreground=default_color.get())
                else:
                    pass
        time_label.config(text=time_left)
    else:
        time_label.config(text="")
    
    if lunch_by_timer.get() and ('invalid' in clock_out_1_time_display.state()):
        if datetime.strptime(current_time, "%I:%M:%S %p") > datetime.strptime(lunch_by_time.get(), "%I:%M:%S %p"):
            lunch_time_label.config(text="")
            window.after(500, update_time)
            return
        else:    
            if datetime.strptime(current_time, "%I:%M:%S %p") >= (datetime.strptime(lunch_by_time.get(), "%I:%M:%S %p") - timedelta(minutes=1)):
                if not lunch_message_box_shown:
                    lunch_message_box_shown = True
                    default_color.set(lunch_time_label.cget('foreground'))
                    lunch_time_label.config(foreground='red')
                    if lunch_alarm_var:
                        toast_alarm()
            else:
                if lunch_time_label.cget('foreground') == 'red':
                    lunch_time_label.config(foreground=default_color.get())
                else:
                    pass
        lunch_time_label.config(text=time_left_lunch)
    else:
        lunch_time_label.config(text="")

    if task_timer.get():
        time_diff = abs(datetime.strptime(current_time, "%I:%M:%S %p") - datetime.strptime(start_time.get(), "%I:%M:%S %p"))
        task_time.set(time_diff)
    else:
        pass
    
    window.after(500, update_time)

def tooltip_button_clicked():
    show_info('Lunch By / Minimum Lunch', 'This section is for employees who reside in California. \n\nLunch By - The time displayed reflects the latest time you should be clocking out for lunch.\n\nMinimum Lunch - The time displayed reflects the earliest time you should be clocking in from a 30 minute lunch. \n\nIf taking a 30 minute lunch - be especially mindful to clock in at a minimum of exactly 30 minutes. If you are short by even 1 second, this will result in a CAML.')

def open_config():
    if config_file_path:
        try:
            subprocess.run(["C:\\Program Files\\Notepad++\\notepad++.exe", config_file_path])
        except Exception:
            try:
                subprocess.run(["notepad.exe", config_file_path])  # Open with the default text editor on Windows
            except Exception as e:
                print("An error occurred:", e)

def highlight_entry(entry):
    if entry == "Clock In":
        clock_in_time_display.state(['invalid'])
        write_config('clock_in_time', 'invalid')
    elif entry == "Clock Out for Lunch":
        clock_out_1_time_display.state(['invalid'])
        write_config('clock_out_lunch_time', 'invalid')
    elif entry == "Clock In from Lunch":
        clock_in_2_time_display.state(['invalid'])
        write_config('clock_in_lunch_time', 'invalid')
    elif entry == "All":
        clock_in_time_display.state(['invalid'])
        clock_out_1_time_display.state(['invalid'])
        clock_in_2_time_display.state(['invalid'])
        write_config('all', 'invalid')

def window_mode_toggle():
    style.theme_use(themename=window_mode.get())
    font_change(window)
    write_config('menu')

def font_change(widget):
    if isinstance(widget, ttk.Entry):
        widget.configure(font=("Helvetica", font_size.get()))
    for child in widget.winfo_children():
        font_change(child)
    style.configure('.' ,font=("Helvetica", font_size.get()))
    # menu_bar.option_add('*font',f"Helvetica, {font_size.get()}")
    for item in menu_bar.winfo_children():
        item.configure(font=("Helvetica", font_size.get()))
        for child in item.winfo_children():
            child.configure(font=("Helvetica", font_size.get()))
            for baby in child.winfo_children():
                baby.configure(font=("Helvetica", font_size.get()))
    write_config('menu')

def custom_alarm():
    custom_sound.set("")
    selection.set("")
    label_var.set("Click browse to add a sound")
    # Create a semi-transparent canvas
    canvas = tk.Canvas(window, highlightthickness=0)
    canvas.place(relwidth=1, relheight=1, anchor='nw')
    canvas.update_idletasks()  # Update to ensure accurate measurements
    
    def fetch_input(event):
        if event.keysym == 'Return':
            # Call the on_select function
            on_select()
        else:
            # Handle other key releases
            # Your code for handling other key releases here
            sound = get_sound_name.get()
            sound_name.set(sound)

    def get_input():
        selection.set(filedialog.askopenfilename(title="Select a .wav file", filetypes=[("WAV files", "*.wav")]))
        if selection.get() != "":
            if selection.get().lower().endswith(".wav"):
                # top.geometry(f"{width}x{height+50}+{x}+{y}")
                label_var.set("Name the sound: ")
                sound_name.set(os.path.basename(selection.get()[:-4]))
                get_sound_name.configure(width= 30)
                get_sound_name.pack()
            else:
                label_var.set("Error: Selected file is not a .wav file.")
        else:
            label_var.set("No file selected.")

    def on_close():
        top.destroy()
        canvas.destroy()
    
    def on_select():
        if sound_name.get() == "" or selection.get() == "":
            show_info("Error", "You must enter a valid name.")
            top.destroy()
            canvas.destroy()
            custom_alarm()
        custom_sound_name.set(sound_name.get())
        custom_sound.set(selection.get())
        top.geometry(f"{width}x{height}+{x}+{y}")
        get_sound_name.destroy()
        select_button.destroy()
        browse_button.destroy()
        ok_button = ttk.Button(top, text="Ok", command=on_close)
        ok_button.pack(pady=10, padx=10)
        try:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            sounds_folder = os.path.join(script_directory, 'alarm_sounds')
            file_copy(custom_sound.get(),sounds_folder, custom_sound_name.get()+".wav")
            selected_sound.set(custom_sound_name.get())
            get_sounds()
            create_sound_menu_entries()
            label_var.set(value="Alarm Sound Added!")
            frame.destroy()
        except Exception as e:
            show_info("Error", e)
            label_var.set(value=f"Error: {e}")

    padding = 20

    # Calculate the required width and height based on the message length
    width = 400 + padding
    height = 160

    # Calculate the position of the message box in relation to the main window
    x_window = window.winfo_x()
    y_window = window.winfo_y()
    gui_width = window.winfo_width()
    gui_height = window.winfo_height()

    x = x_window + (gui_width - width) // 2
    y = y_window + (gui_height - height) // 2

    top = ttk.Toplevel(window)
    top.title("Custom Sound")
    top.geometry(f"{width}x{height}+{x}+{y}")

    frame = ttk.Frame(top)
    frame.pack(anchor='center', side='bottom')

    label = ttk.Label(top, textvariable=label_var, wraplength=width - 2 * padding)
    label.pack(padx=padding, pady=padding, side=TOP)

    browse_button = ttk.Button(frame, text="Browse", command=get_input)
    browse_button.pack(pady=10, padx=10, side='left')

    select_button = ttk.Button(frame, text="Select", command=on_select)
    select_button.pack(pady=10, padx=10, side='right')

    get_sound_name = ttk.Entry(top, textvariable=sound_name, justify='left')
    get_sound_name.bind("<KeyRelease>", lambda event: fetch_input(event))

    top.focus_set()

    top.protocol("WM_DELETE_WINDOW", on_close)

    top.transient(window)  # Associate the messagebox with the main window
    top.grab_set()  # Make the messagebox modal
    font_change(top)
    top.wait_window()  # Wait for the Toplevel window to be destroyed

def create_sound_menu_entries():
    config.read(config_file_path)

    sound_menu.delete(4, "end")
    remove_menu.delete(0, "end")

    for value in config['Sounds'].items():
        key, value = value  # Unpack the tuple into key and value
        # Check if the value is already added to the sound menu
        # if key not in added_keys:
            # added_keys.add(key)  # Add the value to the set of added values
        sound_menu.add_radiobutton(label=value, variable=selected_sound, value=value, command=lambda i="menu": write_config(i))
        remove_menu.add_command(label=value, command=lambda i=value:remove_sound(i))

def file_copy(source, dest, name):
    if os.path.isfile(source) and os.path.isdir(dest):
        shutil.copy(source, os.path.join(dest, name))
    else:
        invalid_path = source if not os.path.isfile(source) else dest
        show_info("Error", f"Invalid directory: {invalid_path}")

def get_sounds():
    config.read(config_file_path)
    config['Sounds'] = {}
    with open(config_file_path, 'w') as configfile: config.write(configfile)

    sounds_folder = os.path.join(script_directory, 'alarm_sounds')
    for file_name in os.listdir(sounds_folder):
        if file_name.endswith('.wav'):
            custom_sound_name.set(file_name[:-4])
            write_config('sound')

    sound_in_file = False
    if selected_sound.get() == "Off":
        return
    for item in config['Sounds'].items():
        if selected_sound.get() == item[1]:
            sound_in_file = True
            break
    if sound_in_file:
        pass
    else:
        selected_sound.set('Rick')

def remove_sound(sound):

    result = show_info("Confirm", "This will also delete the file. Are you sure?")

    if result.get() is True:
        pass
    else:
        return

    script_directory = os.path.dirname(os.path.abspath(__file__))
    sounds_folder = os.path.join(script_directory, 'alarm_sounds')
    file_path = os.path.join(sounds_folder, sound+".wav")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            get_sounds()
            create_sound_menu_entries()
            show_info('Success','Sound successfully removed')
        except Exception as e:
            show_info('Error', e)
    else:
        show_info("Error","The file does not exist")

def task_view():
    task_name_entry.delete(0, 'end')
    task_category_entry.delete(0, 'end')
    task_description_entry.delete(0, 'end')
    if task_view_toggle.get() == True:
        task_pane.grid(row=0, sticky='w', padx=0, pady=[10,0])
        # tab_order()
    else:
        task_pane.grid_forget()

def start_task():
    if task_name_entry.get() != "":
        task_name_entry.state(['!invalid'])
        task_timer.set(True)
        task_name_entry.state(['readonly'])
        file_name = str(current_date).split(' ')[0]+'.txt'
        file_location = os.path.join(task_file_path, file_name)
        if not os.path.exists(task_file_path):
            os.makedirs(task_file_path)
        if not os.path.exists(os.path.join(file_location)):
            open(file_location, "w")
        start_time.set(format_time(time))
        task_start_button.state(['disabled'])
        task_stop_button.state(['!disabled'])
    else:
        task_name_entry.state(['invalid'])

def stop_task():
    task_start_button.state(['!disabled'])
    task_stop_button.state(['disabled'])
    task_name_entry.state(['!readonly'])
    file_name = str(current_date).split(' ')[0]+'.txt'
    file_location = os.path.join(task_file_path, file_name)
    with open(file_location, "a") as f:
        if os.path.getsize(file_location) == 0:
            f.write(task_category.get()+"|"+task_name.get()+"|"+task_time.get()+"|"+task_description.get())
        else:
            f.write("\n"+task_category.get()+"|"+task_name.get()+"|"+task_time.get()+"|"+task_description.get())
    task_name_entry.delete(0, 'end')
    task_description_entry.delete(0, 'end')
    task_time.set('Time Logged')
    task_pane.after(2000, lambda: task_time.set(""))
    task_timer.set(False)

def view_tasks():

    def on_save(event=None):
        task_entry.edit_modified(False)
        text_content = task_entry.get("1.0", "end-1c")
        
        with open(file_location, 'w') as file:
            file.write(text_content)

        on_close()

    def on_clear(event=None):
        with open(file_location, 'w') as file:
            file.write('')
        task_entry.delete("1.0", "end")

    def on_close():
        task_window.destroy()

    file_name = str(current_date).split(' ')[0] + '.txt'
    file_location = os.path.join(task_file_path, file_name)

    task_window = tk.Toplevel()
    task_window.title("Task View")

    task_text = open(file_location, "r").read()

    temp_label = ttk.Label(task_window, text=task_text)
    temp_label.update_idletasks()

    padding = 20

    width = 400 + padding
    height = max(2 * padding + 20 * (task_text.count('\n') + 1), 200)
    
    # Calculate the position of the message box in relation to the main window
    x_window = window.winfo_x()
    y_window = window.winfo_y()
    gui_width = window.winfo_width()
    gui_height = window.winfo_height()

    x = x_window + (gui_width - width) // 2
    y = y_window + (gui_height - height) // 2

    task_window.geometry(f"{width}x{height}+{x}+{y}")

    task_entry = tk.Text(task_window, wrap=tk.WORD)
    task_entry.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    task_window.grid_rowconfigure(0, weight=1)  # Allow the second row (task_entry) to expand
    task_window.grid_columnconfigure(0, weight=1)  # Allow the second row (task_entry) to expand

    task_entry.insert(tk.END, task_text)

    task_pane_lower = ttk.Frame(task_window)
    task_pane_lower.grid(row=1,sticky='s', padx=10, pady=10)
    save_button = ttk.Button(task_pane_lower, text="Save", underline=0, command=on_save)
    save_button.grid(row=0,column=1,padx=10)
    clear_button = ttk.Button(task_pane_lower, text="Clear", underline=0, command=on_clear)
    clear_button.grid(row=0,column=0,padx=10)
    task_window.bind("<Alt-s>", on_save)
    task_window.bind("<Alt-c>", on_clear)
    task_window.protocol("WM_DELETE_WINDOW", on_close)
    task_window.mainloop()

def open_task_folder():
        if task_file_path:
            try:
                subprocess.run(["Explorer", task_file_path])
            except Exception as e:
                print("An error occurred:", e)

def tab_order():
    task_category_entry.focus()
    widgets = [task_category_entry, task_name_entry, task_description_entry, task_start_button, task_stop_button]
    for w in task_pane.winfo_children:
        w.lift()
    
def create_chart():
    # Function to convert time in "%I:%M:%S" format to hours
    def time_to_hours(time_str):
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
        return time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600
    
    def on_close():
        return

    # Parse the text file and create a DataFrame
    data = []
    file_name = str(current_date).split(' ')[0]+'.txt'
    file_location = os.path.join(task_file_path, file_name)

    with open(file_location, "r") as file:
        for line in file:
            category_str, task_name_str, time_spent_str, description_str = line.strip().split("|")
            time_spent = time_to_hours(time_spent_str)
            data.append({"Category": category_str, "TimeSpent": time_spent})
    
    df = pd.DataFrame(data)

    # Calculate the ratio of time spent as a fraction of an 8-hour workday
    df['TimeRatio'] = df['TimeSpent'] / 8.0

    # Create a bar chart using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(df['Category'], df['TimeRatio'], color='skyblue')
    plt.xlabel('Task Category')
    plt.ylabel('Time Ratio (8-hour workday)')
    plt.title('Time Spent on Task Categories')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Show the chart
    plt.show()

def choose_theme():
    width = 900
    height = 450

    # Calculate the position of the message box in relation to the main window
    x_window = window.winfo_x()
    y_window = window.winfo_y()
    gui_width = window.winfo_width()
    gui_height = window.winfo_height()

    x = x_window + (gui_width - width) // 2
    y = y_window + (gui_height - height) // 2

    top = ttk.Toplevel(window)
    top.title("Themes")
    top.geometry(f"{width}x{height}+{x}+{y}")
    
    light_themes = ttk.Frame(top, borderwidth=1, relief="solid")
    light_themes.grid(column=0, padx=10, pady=10, ipadx=20, ipady=20, row=0, sticky="nsew")
    
    dark_themes = ttk.Frame(top, relief="solid")
    dark_themes.grid(column=1, padx=10, pady=10, ipadx=20, ipady=20, row=0, sticky="nsew")

    preview_frame = ttk.Frame(top)
    preview_frame.grid(column=0, columnspan=3, padx=10, pady=10, row=1, sticky="nsew")
    
    button_frame = ttk.Frame(top)
    button_frame.grid(column=0, columnspan=3, padx=10, pady=10, row=2, sticky="nsew")
    
    for i in range(10):
        top.rowconfigure(i, weight=1)
        top.columnconfigure(i, weight=1)
        light_themes.rowconfigure(i, weight=1)
        light_themes.columnconfigure(i, weight=1)
        dark_themes.rowconfigure(i, weight=1)
        dark_themes.columnconfigure(i, weight=1)
        preview_frame.rowconfigure(i, weight=1)
        preview_frame.columnconfigure(i, weight=1)
        button_frame.rowconfigure(i, weight=1)
        button_frame.columnconfigure(i, weight=1)

    light_themes_label = ttk.Label(light_themes, text='Light Themes')
    light_themes_label.grid(column=0, columnspan=4, padx=5, pady=20, row=0)
    
    dark_themes_label = ttk.Label(dark_themes, text='Dark Themes')
    dark_themes_label.grid(column=0, columnspan=4, padx=5, pady=20, row=0)

    Ferguson_light_radiobutton = ttk.Radiobutton(light_themes)
    Ferguson_light_radiobutton.configure(text='Ferguson Light', variable=window_mode, value='fergusonlight', command=window_mode_toggle)
    Ferguson_light_radiobutton.grid(column=0, padx=20, pady=5, row=1, sticky="w")

    Build_light_radiobutton = ttk.Radiobutton(light_themes)
    Build_light_radiobutton.configure(text='Build Light', variable=window_mode, value='buildlight', command=window_mode_toggle)
    Build_light_radiobutton.grid(column=0, padx=20, pady=5, row=2, sticky='w')

    Teams_light_radiobutton = ttk.Radiobutton(light_themes)
    Teams_light_radiobutton.configure(text='Teams Light', variable=window_mode, value='teamslight', command=window_mode_toggle)
    Teams_light_radiobutton.grid(column=0, padx=20, pady=5, row=3, sticky="w")

    Cosmo_radiobutton = ttk.Radiobutton(light_themes)
    Cosmo_radiobutton.configure(text='Cosmo', variable=window_mode, value='cosmo', command=window_mode_toggle)
    Cosmo_radiobutton.grid(column=0, padx=20, pady=5, row=4, sticky="w")

    Morph_radiobutton = ttk.Radiobutton(light_themes)
    Morph_radiobutton.configure(text='Morph', variable=window_mode, value='morph', command=window_mode_toggle)
    Morph_radiobutton.grid(column=1, padx=20, pady=5, row=1, sticky="w")

    Flatly_radiobutton = ttk.Radiobutton(light_themes)
    Flatly_radiobutton.configure(text='Flatly', variable=window_mode, value='flatly', command=window_mode_toggle)
    Flatly_radiobutton.grid(column=1, padx=20, pady=5, row=2, sticky="w")

    Journal_radiobutton = ttk.Radiobutton(light_themes)
    Journal_radiobutton.configure(text='Journal', variable=window_mode, value='journal', command=window_mode_toggle)
    Journal_radiobutton.grid(column=1, padx=20, pady=5, row=3, sticky="w")

    Litera_radiobutton = ttk.Radiobutton(light_themes)
    Litera_radiobutton.configure(text='Litera', variable=window_mode, value='litera', command=window_mode_toggle)
    Litera_radiobutton.grid(column=1, padx=20, pady=5, row=4, sticky="w")

    Lumen_radiobutton = ttk.Radiobutton(light_themes)
    Lumen_radiobutton.configure(text='Lumen', variable=window_mode, value='lumen', command=window_mode_toggle)
    Lumen_radiobutton.grid(column=2, padx=20, pady=5, row=1, sticky="w")

    Minty_radiobutton = ttk.Radiobutton(light_themes)
    Minty_radiobutton.configure(text='Minty', variable=window_mode, value='minty', command=window_mode_toggle)
    Minty_radiobutton.grid(column=2, padx=20, pady=5, row=2, sticky="w")

    Pulse_radiobutton = ttk.Radiobutton(light_themes)
    Pulse_radiobutton.configure(text='Pulse', variable=window_mode, value='pulse', command=window_mode_toggle)
    Pulse_radiobutton.grid(column=2, padx=20, pady=5, row=3, sticky="w")

    Sandstone_radiobutton = ttk.Radiobutton(light_themes)
    Sandstone_radiobutton.configure(text='Sandstone', variable=window_mode, value='sandstone', command=window_mode_toggle)
    Sandstone_radiobutton.grid(column=2, padx=20, pady=5, row=4, sticky="w")

    United_radiobutton = ttk.Radiobutton(light_themes)
    United_radiobutton.configure(text='United', variable=window_mode, value='united', command=window_mode_toggle)
    United_radiobutton.grid(column=3, padx=20, pady=5, row=1, sticky="w")

    Yeti_radiobutton = ttk.Radiobutton(light_themes)
    Yeti_radiobutton.configure(text='Yeti', variable=window_mode, value='yeti', command=window_mode_toggle)
    Yeti_radiobutton.grid(column=3, padx=20, pady=5, row=2, sticky="w")

    Simplex_radiobutton = ttk.Radiobutton(light_themes)
    Simplex_radiobutton.configure(text='Simplex', variable=window_mode, value='simplex', command=window_mode_toggle)
    Simplex_radiobutton.grid(column=3, padx=20, pady=5, row=3, sticky="w")

    Cerculean_radiobutton = ttk.Radiobutton(light_themes)
    Cerculean_radiobutton.configure(text='Cerculean', variable=window_mode, value='cerculean', command=window_mode_toggle)
    Cerculean_radiobutton.grid(column=3, padx=20, pady=5, row=4, sticky="w")

    Ferguson_dark_radiobutton = ttk.Radiobutton(dark_themes)
    Ferguson_dark_radiobutton.configure(text='Ferguson Dark', variable=window_mode, value='fergusondark', command=window_mode_toggle)
    Ferguson_dark_radiobutton.grid(column=0, padx=20, pady=5, row=1, sticky="w")

    Build_dark_radiobutton = ttk.Radiobutton(dark_themes)
    Build_dark_radiobutton.configure(text='Build Dark', variable=window_mode, value='builddark', command=window_mode_toggle)
    Build_dark_radiobutton.grid(column=0, padx=20, pady=5, row=2, sticky="w")

    Teams_dark_radiobutton = ttk.Radiobutton(dark_themes)
    Teams_dark_radiobutton.configure(text='Teams Dark', variable=window_mode, value='teamsdark', command=window_mode_toggle)
    Teams_dark_radiobutton.grid(column=0, padx=20, pady=5, row=3, sticky="w")

    Cyborg_radiobutton = ttk.Radiobutton(dark_themes)
    Cyborg_radiobutton.configure(text='Cyborg', variable=window_mode, value='cyborg', command=window_mode_toggle)
    Cyborg_radiobutton.grid(column=0, padx=20, pady=5, row=4, sticky="w")

    Darkly_radiobutton = ttk.Radiobutton(dark_themes)
    Darkly_radiobutton.configure(text='Darkly', variable=window_mode, value='darkly', command=window_mode_toggle)
    Darkly_radiobutton.grid(column=1, padx=20, pady=5, row=1, sticky="w")

    Solar_radiobutton = ttk.Radiobutton(dark_themes)
    Solar_radiobutton.configure(text='Solar', variable=window_mode, value='solar', command=window_mode_toggle)
    Solar_radiobutton.grid(column=1, padx=20, pady=5, row=2, sticky="w")

    Superhero_radiobutton = ttk.Radiobutton(dark_themes)
    Superhero_radiobutton.configure(text='Superhero', variable=window_mode, value='superhero', command=window_mode_toggle)
    Superhero_radiobutton.grid(column=1, padx=20, pady=5, row=3, sticky="w")

    Vapor_radiobutton = ttk.Radiobutton(dark_themes)
    Vapor_radiobutton.configure(text='Vapor', variable=window_mode, value='vapor', command=window_mode_toggle)
    Vapor_radiobutton.grid(column=1, padx=20, pady=5, row=4, sticky="w")

    preview_header_label = ttk.Label(preview_frame)
    preview_header_label.configure(text='Preview')
    preview_header_label.grid(column=0, columnspan=8, row=0)

    preview_clock_in_label = ttk.Label(preview_frame)
    preview_clock_in_label.configure(text='Clock In :')
    preview_clock_in_label.grid(column=0, row=1)

    preview_clock_in_time_display_1 = ttk.Entry(preview_frame)
    preview_clock_in_time_display_1.configure(justify="center", state="normal", textvariable=clock_in_time, width=14, font=("Helvetica, 12"))
    preview_clock_in_time_display_1.grid(column=1, padx=5, pady=20, row=1)

    preview_clock_in_time_display_3 = ttk.Entry(preview_frame)
    preview_clock_in_time_display_3.configure(justify="center", textvariable=clock_in_time, width=14, font=("Helvetica, 12"))
    preview_clock_in_time_display_3.grid(column=2, padx=5, pady=5, row=1)
    preview_clock_in_time_display_3.state(['invalid'])

    preview_clock_in_button = ttk.Button(preview_frame, text='Grab Time')
    preview_clock_in_button.grid(column=3, row=1)

def ca_assoc_toggle():
    if not ca_toggle.get():
        alarm_menu.entryconfigure('Clock Out (Lunch) Alarm Toggle', state=DISABLED)
        timers_menu.entryconfigure('Lunch By Timer', state=DISABLED)
        lunch_alarm_var.set(False)
        lunch_by_timer.set(False)
        container_frame_2_outer.grid_forget()
        container_frame_2.grid_forget()
    elif ca_toggle.get():
        alarm_menu.entryconfigure('Clock Out (Lunch) Alarm Toggle', state=NORMAL)
        timers_menu.entryconfigure('Lunch By Timer', state=NORMAL)
        lunch_alarm_var.set(True)
        lunch_by_timer.set(True)
        container_frame_2_outer.grid(row=2)
        container_frame_2.grid(row=1)
    write_config("menu")

def convert_to_us_timezones(input_time, zone):
    time_string = input_time
    time_datetime = datetime.strptime(time_string, "%I:%M:%S %p")
    today_date = datetime.today()
    combined_datetime = datetime.combine(today_date, time_datetime.time())

    # Define the Hawaii time zone
    hawaii_timezone = pytz.timezone('Pacific/Honolulu')

    if zone == 'US/Hawaii':
        # Determine if daylight saving time is in effect for Hawaii
        is_dst = hawaii_timezone.localize(combined_datetime).dst()
        
        # Adjust the time format based on DST
        if is_dst:
            converted_time = combined_datetime.astimezone(hawaii_timezone).strftime("%I:%M:%S %p")
        else:
            converted_time = combined_datetime.astimezone(hawaii_timezone).strftime("%I:%M:%S %p")
    else:
        # For other time zones, use the provided time zone
        tz = pytz.timezone(zone)
        
        # Check if the provided zone is 'US/Mountain' and adjust for DST
        if zone == 'US/Mountain':
            is_dst = tz.localize(combined_datetime).dst()
            if is_dst:
                converted_time = combined_datetime.astimezone(tz).strftime("%I:%M:%S %p")
            else:
                converted_time = combined_datetime.astimezone(tz).strftime("%I:%M:%S %p")
        else:
            # For other time zones, don't adjust for DST
            converted_time = combined_datetime.astimezone(tz).strftime("%I:%M:%S %p")

    return converted_time

def time_zone_toggle():
    write_config('menu')
    if tz_toggle.get() == True:
        tz_pane.grid(row=5, sticky='nsew', padx=0, pady=[0,10])
    else:
        tz_pane.grid_forget()

def tz_on_enter(event, label_id):
    variables = [clock_in_time,
    clock_out_lunch_time,
    clock_in_lunch_time,
    clock_out_time,
    lunch_by_time,
    minimum_lunch,
    add_time_1,
    add_time_2
    ]
    for variable in variables:
        variable.set(format_time(convert_to_us_timezones(variable.get(), labels[label_id])))
    
def tz_on_leave(event, label_id):
    read_config()

def add_entries_toggle():
    write_config('menu')
    if not ae_toggle.get():
        container_frame_3_outer.grid_forget()
        container_frame_3.grid_forget()
    elif ae_toggle.get():
        container_frame_3_outer.grid(row=3)
        container_frame_3.grid(row=1)

def toast_alarm():
    # Path to your custom sound file (in .wav format)
    sound_file_path = f'./alarm_sounds/{selected_sound.get()}.wav'

    # Define a callback function to handle click events
    def on_notification_click(activated_args=None):
        pygame.mixer.quit()

    def play_sound():
        pygame.mixer.init()
        
        if not pygame.mixer.music.get_busy() and not selected_sound.get() == "Off":
            sound = pygame.mixer.Sound(sound_file_path)
            sound.play(loops=-1, fade_ms=1000)
    
    def show_notification():
        if selected_sound.get() == "Off":
            toast('Time to clock out!', 'Click to silence', duration='long', on_click=on_notification_click)
        else:
            toast('Time to clock out!', 'Click to silence', duration='long', audio={'silent': 'true'}, on_click=on_notification_click)

    # Create two threads for playing sound and showing the notification
    sound_thread = threading.Thread(target=play_sound)
    notification_thread = threading.Thread(target=show_notification)
    sound_thread.daemon = True
    notification_thread.daemon = True

    # Start the threads
    sound_thread.start()
    notification_thread.start()

def open_link(link):
    webbrowser.open(link)

def calc_view():
    if calc_view_toggle.get() == True:
        calc_pane.grid(row=0, sticky='w', padx=0, pady=[10,0])
    else:
        calc_pane.grid_forget()
    calculate_clock_in_time()

def calculate_clock_in_time():
    # Parse clock-out time
    clock_out_time = datetime.strptime(calc_clock_out.get(), "%I:%M:%S %p")

    # Parse lunch break duration into hours and minutes
    lunch_hours, lunch_minutes = map(int, calc_lunch_break.get().split(':'))
    lunch_break_duration = timedelta(hours=lunch_hours, minutes=lunch_minutes)

    # Calculate clock-in time by subtracting lunch break duration from clock-out time
    clock_in_time = clock_out_time - (timedelta(hours=8) + lunch_break_duration)

    calc_time.set("Clock in at: " + format_time(clock_in_time)) # Return clock-in time in HH:MM format

def handle_calc_keypress(event, entry_id):
    # Function to be called when any key is pressed
    # Use regex to extract the time from the grabbed text
    # Update the corresponding time based on the button index
    if entry_id == "clock out time":
        time = calc_clock_out.get().strip()
        if re.match(r"\d{1,2}:\d{2}:\d{2} [APM]+",time):
            calc_clock_out.set(format_time(time))
            calculate_clock_in_time()
    elif entry_id == "lunch break":
        time = calc_lunch_break.get().strip()
        if re.match(r"\d{1,2}:\d{2}", time):
            calculate_clock_in_time()

# Create the main window
window = ttk.Window(resizable=[False,False], title="TimeTracker", themename="cosmo")
window.bind_all("<Button-1>", lambda event: event.widget.focus_set())

# Style
style = Style()

# Create time variables with default values
calc_view_toggle = tk.BooleanVar()
calc_clock_out = tk.StringVar(value="5:00:00 PM")
calc_lunch_break = tk.StringVar(value="1:00")
calc_time = tk.StringVar()
clock_in_time = tk.StringVar(value="8:00:00 AM")
clock_out_lunch_time = tk.StringVar(value="12:00:00 PM")
clock_in_lunch_time = tk.StringVar(value="1:00:00 PM")
clock_out_time = tk.StringVar(value="5:00:00 PM")
lunch_by_time = tk.StringVar(value="1:00:00 PM")
minimum_lunch = tk.StringVar(value="12:30:00 PM")
add_time_1 = tk.StringVar(value="12:00:00 PM")
add_time_2 = tk.StringVar(value="12:00:00 PM")
time_out = tk.StringVar(value=0.0)
pto_check = tk.BooleanVar(value=True)
alarm_var = tk.BooleanVar(value=False)
lunch_alarm_var = tk.BooleanVar(value=False)
selected_sound = tk.StringVar(value="rick")
window_mode = tk.StringVar(value="cosmo")
lunch_by_timer = tk.BooleanVar(value=True)
clock_out_timer = tk.BooleanVar(value=True)
font_size = tk.IntVar(value=12)
custom_sound = tk.StringVar()
sound_name = tk.StringVar()
custom_sound_name = tk.StringVar()
label_var = tk.StringVar()
selection = tk.StringVar()
added_keys = set()
task_view_toggle = tk.BooleanVar()
task_name = tk.StringVar()
task_timer = tk.BooleanVar()
start_time = tk.StringVar()
task_time = tk.StringVar()
task_description = tk.StringVar()
task_category = tk.StringVar()
default_color = tk.StringVar()
current_time = tk.StringVar()
ca_toggle = tk.BooleanVar(value=False)
ae_toggle = tk.BooleanVar(value=False)
tz_toggle = tk.BooleanVar(value=False)

# -------------------------------------------------------------------------------------------- #

menu_bar = ttk.Menu(window)
window.config(menu=menu_bar)

file_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open Configuration File", command=open_config)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

alarm_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Alarm", menu=alarm_menu)
alarm_menu.add_command(label="Test Alarm", command=toast_alarm)
alarm_menu.add_command(label="Silence Alarm", command=pygame.mixer.quit)
alarm_menu.add_checkbutton(label="Clock Out Alarm Toggle", variable=alarm_var, command=lambda i="menu": write_config(i))
alarm_menu.add_checkbutton(label="Clock Out (Lunch) Alarm Toggle", indicatoron=True, variable=lunch_alarm_var, command=lambda i="menu": write_config(i))

sound_menu = ttk.Menu(alarm_menu, tearoff=0)
alarm_menu.add_cascade(label="Sounds", menu=sound_menu)
sound_menu.add_radiobutton(label="Off (Silent)", variable=selected_sound, value="Off", command=lambda i="menu": write_config(i))
sound_menu.add_separator()
sound_menu.add_command(label="Add Sound", command=custom_alarm)
sound_menu.add_separator()

remove_menu = ttk.Menu(alarm_menu, tearoff=0)
alarm_menu.add_cascade(label="Remove Sounds", menu=remove_menu)

window_menu = ttk.Menu(menu_bar, tearoff=0)
theme_menu = ttk.Menu(window_menu, tearoff=0)
light_themes = ttk.Menu(theme_menu, tearoff=0)
dark_themes = ttk.Menu(theme_menu, tearoff=0)
menu_bar.add_cascade(label="Window", menu=window_menu)
window_menu.add_cascade(label="Themes", menu=theme_menu)
# window_menu.add_command(label="Choose Theme", command=choose_theme)
theme_menu.add_cascade(label="Light Themes", menu=light_themes)
theme_menu.add_cascade(label="Dark Themes", menu=dark_themes)
window_menu.add_command(label="Save position", command=save_position)
window_menu.add_command(label="Center window", command=lambda i=window: center(i))
window_menu.add_checkbutton(label="CA Associates", variable=ca_toggle, command=ca_assoc_toggle)
window_menu.add_checkbutton(label="Additional Entries", variable=ae_toggle, command=add_entries_toggle)
window_menu.add_checkbutton(label="Time Zones", variable=tz_toggle, command=time_zone_toggle)
window_menu.add_checkbutton(label="Clock In Time Calculator", variable=calc_view_toggle, command=calc_view)
light_themes.add_radiobutton(label="Ferguson Light", variable=window_mode, value="fergusonlight", command=window_mode_toggle)
light_themes.add_radiobutton(label="Build Light", variable=window_mode, value="buildlight", command=window_mode_toggle)
light_themes.add_radiobutton(label="Teams Light", variable=window_mode, value="teamslight", command=window_mode_toggle)
light_themes.add_radiobutton(label="Cosmo", variable=window_mode, value="cosmo", command=window_mode_toggle)
light_themes.add_radiobutton(label="Morph", variable=window_mode, value="morph", command=window_mode_toggle)
light_themes.add_radiobutton(label="Flatly", variable=window_mode, value="flatly", command=window_mode_toggle)
light_themes.add_radiobutton(label="Journal", variable=window_mode, value="journal", command=window_mode_toggle)
light_themes.add_radiobutton(label="Litera", variable=window_mode, value="litera", command=window_mode_toggle)
light_themes.add_radiobutton(label="Lumen", variable=window_mode, value="lumen", command=window_mode_toggle)
light_themes.add_radiobutton(label="Minty", variable=window_mode, value="minty", command=window_mode_toggle)
light_themes.add_radiobutton(label="Pulse", variable=window_mode, value="pulse", command=window_mode_toggle)
light_themes.add_radiobutton(label="Sandstone", variable=window_mode, value="sandstone", command=window_mode_toggle)
light_themes.add_radiobutton(label="United", variable=window_mode, value="united", command=window_mode_toggle)
light_themes.add_radiobutton(label="Yeti", variable=window_mode, value="yeti", command=window_mode_toggle)
light_themes.add_radiobutton(label="Simplex", variable=window_mode, value="simplex", command=window_mode_toggle)
light_themes.add_radiobutton(label="Cerculean", variable=window_mode, value="cerculean", command=window_mode_toggle)

dark_themes.add_radiobutton(label="Ferguson Dark", variable=window_mode, value="fergusondark", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Build Dark", variable=window_mode, value="builddark", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Teams Dark", variable=window_mode, value="teamsdark", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Cyborg", variable=window_mode, value="cyborg", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Darkly", variable=window_mode, value="darkly", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Solar", variable=window_mode, value="solar", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Superhero", variable=window_mode, value="superhero", command=window_mode_toggle)
dark_themes.add_radiobutton(label="Vapor", variable=window_mode, value="vapor", command=window_mode_toggle)

entries_menu = ttk.Menu(menu_bar, tearoff=0)
highlight_menu = ttk.Menu(entries_menu, tearoff=0)
menu_bar.add_cascade(label="Entries", menu=entries_menu)
entries_menu.add_cascade(label="Highlight Entries", menu=highlight_menu)
highlight_menu.add_command(label="Clock In", command=lambda i="Clock In": highlight_entry(i))
highlight_menu.add_command(label="Clock Out for Lunch", command=lambda i="Clock Out for Lunch": highlight_entry(i))
highlight_menu.add_command(label="Clock In from Lunch", command=lambda i="Clock In from Lunch": highlight_entry(i))
highlight_menu.add_separator()
highlight_menu.add_command(label="All", command=lambda i="All": highlight_entry(i))

timers_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Timers", menu=timers_menu)
timers_menu.add_checkbutton(label="Lunch By Timer", variable=lunch_by_timer, command=lambda i="menu": write_config(i))
timers_menu.add_checkbutton(label="Clock Out Timer", variable=clock_out_timer, command=lambda i="menu": write_config(i))

task_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Tasks", menu=task_menu)
task_menu.add_checkbutton(label="Toggle Task View", variable=task_view_toggle, command=task_view)
task_menu.add_command(label="View Tasks", command=view_tasks)
task_menu.add_command(label="Open Tasks Folder", command=open_task_folder)
task_menu.add_command(label="Create Chart", command=create_chart)

help_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Open SharePoint SOP", command=lambda i="https://mydigitalspace.sharepoint.com/sites/BwFDataTraining/SitePages/Time-Tracker.aspx": open_link(i))

# -------------------------------------------------------------------------------------------- #

task_pane = ttk.Frame(window, height=20, padding=10)
task_pane_1 = ttk.Frame(task_pane)
task_pane_1.grid(row=0, column=0, columnspan=99, sticky='w')
task_pane_2 = ttk.Frame(task_pane)
task_pane_2.grid(row=1, column=0, columnspan=99, sticky='w')
task_pane.tk_focusPrev().focus_set()

task_category_label = ttk.Label(task_pane_1, text="Category")
task_category_label.grid(row=0, column=0, padx=5, pady=5)
task_category_entry = ttk.Combobox(task_pane_1, state='readonly', textvariable=task_category, font=('Helvetica' ,12))
task_category_entry['values'] = sorted(['Project','Side Task','Support','Meeting','Consultation'])
task_category_entry.grid(row=0, column=1, padx=5, pady=5)

task_name_label = ttk.Label(task_pane_1, text='Name:')
task_name_label.grid(row=0, column=2, padx=5, pady=5)
task_name_entry = ttk.Entry(task_pane_1,textvariable=task_name, justify='left')
task_name_entry.grid(row=0, column=3, padx=5, pady=5)

task_description_label = ttk.Label(task_pane_2,text="Description:")
task_description_label.grid(row=0, column=0, padx=5, pady=5)
task_description_entry = ttk.Entry(task_pane_2, textvariable=task_description, justify='left', width=50)
task_description_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2, sticky='ew')

task_start_button = ttk.Button(task_pane_2, text='Start', command=start_task)
task_start_button.grid(row=0, column=3, padx=5, pady=5, sticky='w')

task_stop_button = ttk.Button(task_pane_2, text='Stop', state='disabled', command=stop_task)
task_stop_button.grid(row=0, column=4, padx=5, pady=5, sticky='w')

task_time_label = ttk.Label(task_pane_2, textvariable=task_time, width=len("Time Logged"))
task_time_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')

# -------------------------------------------------------------------------------------------- #

calc_pane = ttk.Frame(window, height=20, padding=10)
calc_pane_1 = ttk.Frame(calc_pane)
calc_pane_1.grid(row=0, column=0, columnspan=99, sticky='w')
calc_pane.tk_focusPrev().focus_set()

calc_clock_out_time_label = ttk.Label(calc_pane_1, text="Clock Out Time: ")
calc_clock_out_time_label.grid(row=0, column=0, padx=5, pady=5)
calc_clock_out_time_entry = ttk.Entry(calc_pane_1, textvariable=calc_clock_out, font=('Helvetica' ,12), width=14)
calc_clock_out_time_entry.grid(row=0, column=1, padx=5, pady=5)
calc_clock_out_time_entry.bind("<KeyRelease>", lambda event: handle_calc_keypress(event, "clock out time"))

calc_lunch_break_label = ttk.Label(calc_pane_1, text='Lunch Break: ')
calc_lunch_break_label.grid(row=0, column=2, padx=5, pady=5)
calc_lunch_break_entry = ttk.Entry(calc_pane_1,textvariable=calc_lunch_break, justify='left', width=14)
calc_lunch_break_entry.grid(row=0, column=3, padx=5, pady=5)
calc_lunch_break_entry.bind("<KeyRelease>", lambda event: handle_calc_keypress(event, "lunch break"))

calc_time_label = ttk.Label(calc_pane_1, textvariable=calc_time, width=len("Clock in at: 8:00:00 AM"))
calc_time_label.grid(row=0, column=5, padx=5, pady=5, sticky='w')

# -------------------------------------------------------------------------------------------- #

tz_pane = ttk.Frame(window, height=20, padding=10)
for i in range(7):
    tz_pane.grid_columnconfigure(i, weight=1)

labels = ['US/Hawaii', 'US/Alaska', 'US/Pacific', 'US/Arizona', 'US/Mountain', 'US/Central', 'US/Eastern', 'UTC']

label_widgets = []

# Create three labels with different IDs
for i, label_text in enumerate(labels):
    label = ttk.Label(tz_pane, text=label_text, font=("Helvetica", font_size.get()), relief="solid", borderwidth=1, padding=10)
    label.grid(row=1, column=i)
    label_widgets.append(label)

# Bind events for each label with their respective IDs
for i, label in enumerate(label_widgets):
    label.bind("<Enter>", lambda event, label_id=i: tz_on_enter(event, label_id))
    label.bind("<Leave>", lambda event, label_id=i: tz_on_leave(event, label_id))

# -------------------------------------------------------------------------------------------- #

outer_frame = ttk.Frame(window, padding=10)
outer_frame.grid(row=1)

container_frame_1_outer = ttk.Frame(outer_frame, padding=10)
container_frame_1_outer.grid(row=1)

container_frame = ttk.Frame(container_frame_1_outer, padding=10, relief="solid", borderwidth=1)
container_frame.grid(row=1)

container_frame_2_outer = ttk.Frame(outer_frame, padding=10)
container_frame_2_outer.grid(row=2)

container_frame_2 = ttk.Frame(container_frame_2_outer, padding=10, relief="solid", borderwidth=1)
container_frame_2.grid(row=1)

container_frame_3_outer = ttk.Frame(outer_frame, padding=10)
container_frame_3_outer.grid(row=3)

container_frame_3 = ttk.Frame(container_frame_3_outer, padding=10, relief="solid", borderwidth=1)
container_frame_3.grid(row=1)

# Create labels and buttons for standard time clock entries
# -------------------------------------------------------------------------------------------- #

# Time Clock Entries
time_clock_entries_label = ttk.Label(container_frame, text="Time Clock Entries", justify='center')
time_clock_entries_label.grid(row=0, column=1, padx=5, pady=5, columnspan=8)

# Clock In Label
clock_in_label = ttk.Label(container_frame, text="Clock In :", anchor="e")
clock_in_label.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Clock In Display
clock_in_time_display = ttk.Entry(container_frame, name='clock_in_time_display', textvariable=clock_in_time, width=14)
clock_in_time_display.grid(row=2, column=2, padx=5, pady=5)
clock_in_time_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "Entry 1"))
clock_in_time_display['justify'] = "center"

# Clock In Button
clock_in_button = ttk.Button(container_frame,text="Grab Time", command=lambda i="clock_in": grab_text(i))
clock_in_button.grid(row=2, column=3, padx=5, pady=5)

# -------------------------------------------------------------------------------------------- #

# Clock Out (Lunch) Label
clock_out_1_label = ttk.Label(container_frame, text="Clock Out (Lunch) :", anchor="e")
clock_out_1_label.grid(row=2, column=5, padx=5, pady=5, sticky="ew")

# Clock Out (Lunch) Display
clock_out_1_time_display = ttk.Entry(container_frame, name='clock_out_1_time_display', textvariable=clock_out_lunch_time, width= 14)
clock_out_1_time_display.grid(row=2, column=6, padx=5, pady=5)
clock_out_1_time_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "Entry 2"))
clock_out_1_time_display['justify'] = "center"

# Clock Out (Lunch) Button
clock_out_1_button = ttk.Button(container_frame, text="Grab Time", command=lambda i="clock_out": grab_text(i))
clock_out_1_button.grid(row=2, column=7, padx=5, pady=5)

# -------------------------------------------------------------------------------------------- #

# Clock In (Lunch) Label
clock_in_2_label = ttk.Label(container_frame, text="Clock In (Lunch) :", anchor="e")
clock_in_2_label.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Clock In (Lunch) Display
clock_in_2_time_display = ttk.Entry(container_frame, name='clock_in_2_time_display', textvariable=clock_in_lunch_time, width= 14)
clock_in_2_time_display.grid(row=3, column=2, padx=5, pady=5)
clock_in_2_time_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "Entry 3"))
clock_in_2_time_display['justify'] = "center"

# Clock In (Lunch) Button
clock_in_2_button = ttk.Button(container_frame, text="Grab Time", command=lambda i="clock_in_2": grab_text(i))
clock_in_2_button.grid(row=3, column=3, padx=5, pady=5)

# -------------------------------------------------------------------------------------------- #

# Clock Out Label
clock_out_2_label = ttk.Label(container_frame, text="Clock Out :", anchor="e")
clock_out_2_label.grid(row=3, column=5, padx=5, pady=5, sticky="ew")

# Clock Out Display
clock_out_2_time_display = ttk.Entry(container_frame, name='clock_out_2_time_display', textvariable=clock_out_time, width= 14, justify='center')
clock_out_2_time_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "readonly"))
clock_out_2_time_display.grid(row=3, column=6, padx=5, pady=5)

# Time Til Clock Out Label
time_label = ttk.Label(container_frame, anchor="e")
time_label.grid(row=3, column=7, padx=5, pady=5)

# -------------------------------------------------------------------------------------------- #

# Header Label
ca_employees_label = ttk.Label(container_frame_2, text="CA Associates")
ca_employees_label.grid(row=1, column=1, padx=5, pady=5, columnspan=6)

# Lunch By Label
lunch_by_label = ttk.Label(container_frame_2, text="Lunch By :")
lunch_by_label.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Lunch By Display
lunch_by_time_display = ttk.Entry(container_frame_2, name='lunch_by_time_display', textvariable=lunch_by_time, width= 14, justify='center')
lunch_by_time_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "readonly"))
lunch_by_time_display.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

# Time Til Clock Out For Lunch Label
lunch_time_label = ttk.Label(container_frame_2, anchor="e")
lunch_time_label.grid(row=3, column=3, padx=5, pady=5)

# 30 Minute Lunch Label
minimum_lunch_label = ttk.Label(container_frame_2, text="Minimum Lunch :", anchor="e")
minimum_lunch_label.grid(row=3, column=4, padx=5, pady=5, sticky="ew")

# 30 Minute Lunch Display
minimum_lunch_display = ttk.Entry(container_frame_2, name='minimum_lunch_display', textvariable=minimum_lunch, width= 14, justify='center')
minimum_lunch_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "readonly"))
minimum_lunch_display.grid(row=3, column=5, padx=5, pady=5, sticky="ew")

# Info button
tooltip_button = ttk.Button(container_frame_2,text='?',width=2,command=tooltip_button_clicked)
tooltip_button.grid(row=3, column=6, padx=5, pady=5, sticky='w')

# -------------------------------------------------------------------------------------------- #

# Additional Time Label
add_time_label = ttk.Label(container_frame_3, text="Additional Entries", justify='center')
add_time_label.grid(row=1, column=1, padx=5, pady=5, columnspan=7)

# Clock Out Label
add_clock_out_label = ttk.Label(container_frame_3, text="Clock Out :", anchor="e")
add_clock_out_label.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Additional Time 1 Display
add_time_1_display = ttk.Entry(container_frame_3, name='add_time_1_display', textvariable=add_time_1, width= 14)
add_time_1_display.grid(row=3, column=2, padx=5, pady=5)
add_time_1_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "Entry 4"))
add_time_1_display['justify'] = "center"

# Additional Time 1 Button
add_time_1_button = ttk.Button(container_frame_3, text="Grab Time", command=lambda i="add_time_1": grab_text(i))
add_time_1_button.grid(row=3, column=3, padx=5, pady=5)

# Clock In Label
add_clock_in_label = ttk.Label(container_frame_3, text="Clock In :", anchor="e")
add_clock_in_label.grid(row=3, column=5, padx=5, pady=5, sticky="ew")

# Additional Time 2 Display
add_time_2_display = ttk.Entry(container_frame_3, name='add_time_2_display', textvariable=add_time_2, width= 14)
add_time_2_display.grid(row=3, column=6, padx=5, pady=5)
add_time_2_display.bind("<KeyRelease>", lambda event: handle_keypress(event, "Entry 5"))
add_time_2_display['justify'] = "center"

# Additional Time 2 Button
add_time_2_button = ttk.Button(container_frame_3, text="Grab Time", command=lambda i="add_time_2": grab_text(i))
add_time_2_button.grid(row=3, column=7, padx=5, pady=5)

# Clear Times Button
clear_times_button = ttk.Button(container_frame_3, text= "Clear",command=clear_add_times)
clear_times_button.grid(row=4, column=7, padx=5, pady=5)

# Display additional time clocked out in decimal form
time_out_label = ttk.Label(container_frame_3, text="Time Out:", anchor="e")
time_out_label.grid(row=4, column=2, padx=5, pady=5, sticky="ew")
time_out_display = ttk.Label(container_frame_3, textvariable=time_out, anchor='w')
time_out_display.grid(row=4, column=3, padx=5, pady=5, sticky="ew")

# Check box to opt for PTO instead of incrementing clock out time
pto_check_label = ttk.Label(container_frame_3, text= "PTO", width=10, anchor='e')
pto_check_label.grid(row=4, column=5, padx=5, pady=5, sticky="ew")
pto_check_box = ttk.Checkbutton(container_frame_3, variable=pto_check, command=update)
pto_check_box.grid(row=4, column=6, padx=5, pady=5, sticky="w")

# # Tool tips
time_label_tooltip = ToolTip(time_label,"Time until clock out")
lunch_by_label_tooltip = ToolTip(lunch_by_label,"The latest time you should be clocking out for lunch")
lunch_time_lablel_tooltip = ToolTip(lunch_time_label,"Time until 'Lunch By'")
minimum_lunch_label_tooltip = ToolTip(minimum_lunch_label,"The earliest time you should be clocking in from a 30 minute lunch")

# Import times fromm config file, if file exists
if os.path.exists(config_file_path):
    read_config()

window.after(0,
             read_config(),
             update(),
             update_time(),
             font_change(window),
             set_position(),
             get_sounds(),
             create_sound_menu_entries(),
             calculate_clock_in_time()
             )

# Run the GUI main loop
window.mainloop()