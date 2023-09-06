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
import pygame
import subprocess
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import shutil

# Global Variables
message_box_shown = False
lunch_message_box_shown = False
current_date = datetime.today()

# sound_file_path = pathlib.Path.home() / 'Desktop' /'Projects' / 'Python' / 'TimeTracker' /'rick.wav'
# sound_file_path = 'alarm_sounds/alarm.wav'

# Create a configparser object
config = configparser.ConfigParser()

# Get the path to the user's documents folder
documents_path = pathlib.Path.home() / 'Documents'

# Construct the path to the config.ini file
config_file_path = documents_path / 'TimeTracker.ini'

# Construct the path to the tasks folder
task_file_path = documents_path / 'TimeTracker_Tasks'
script_directory = os.path.dirname(os.path.abspath(__file__))

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

    if "WindowPosition" in config:
        stored_coordinates = (int(config["WindowPosition"]["X"]), int(config["WindowPosition"]["Y"]))

        # Apply stored coordinates if the stored screen matches the current screen
        window.geometry(f"+{stored_coordinates[0]}+{stored_coordinates[1]}")

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
        'lunch_by_timer','clock_out_timer','alarm_var', 'lunch_alarm_var', 'top_var', 'window_mode', 
        'selected_sound', 'font_size'
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
            config['Times']['clock_out_time']: clock_out_time.get()
            config['Times']['lunch_by_time']: lunch_by_time.get()
            config['Times']['add_time_1']: add_time_1.get()
            config['Times']['add_time_2']: add_time_2.get()
            config['Times']['time_out']: time_out.get()
            config['Times']['pto_check']: str(pto_check.get())
            config['Times']['min_lunch']: minimum_lunch.get()
    elif index == 'menu':
        config['Menu'] = {
            'alarm_var': str(alarm_var.get()),
            'lunch_alarm_var': lunch_alarm_var.get(),
            'top_var': str(top_var.get()),
            'window_mode': window_mode.get(),
            'selected_sound': selected_sound.get(),
            'lunch_by_timer': lunch_by_timer.get(),
            'clock_out_timer': clock_out_timer.get(),
            'font_size': font_size.get(),
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

        time_window = pyautogui.getWindowsWithTitle('Time Tracker')[0]
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
            message_box("Warning", "Unable to find a valid time in the grabbed text.")

    except Exception as e:
        message_box("Error", str(e))

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

# Convert time variable back to string and remove leading zeros from hour
def format_time(time):
    # Assuming you have a datetime object called `clock_out`
    # Convert the datetime object to a string
    try:
        time_str = time.strftime('%I:%M:%S %p')
    except:
        time_str = time

    # Remove leading zeros from the hour component
    time_parts = time_str.split(':')
    hour = str(int(time_parts[0])).strip()

    # Construct the updated time string
    updated_time_str = f"{hour}:{time_parts[1]}:{time_parts[2]}"

    return updated_time_str

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
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def play_sound(file_path):
    sound = pygame.mixer.Sound(file_path)
    sound.play(loops=-1,fade_ms=1000)

def alarm_window():
    global selected_sound
    sound_file_path = f'./alarm_sounds/{selected_sound.get()}.wav'
    pygame.mixer.init()
    
    if not pygame.mixer.music.get_busy() and not selected_sound.get() == "Off":
        play_sound(sound_file_path)
    else:
        pass

    response = message_box('Clock Out Reminder', 'Time to clock out!')
    if response:
        pygame.mixer.quit()

def message_box(title, message):

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

    # Create a temporary label to calculate the width and height needed for the message
    temp_label = ttk.Label(window, text=message)
    temp_label.update_idletasks()  # Update to ensure accurate measurements

    padding = 10

    # Calculate the required width and height based on the message length
    width = temp_label.winfo_reqwidth() + 2 * padding  # Add padding
    height = temp_label.winfo_reqheight() + 80  # Add padding and space for the OK button

    # Calculate the position of the message box in relation to the main window
    x_window = window.winfo_x()
    y_window = window.winfo_y()
    gui_width = window.winfo_width()
    gui_height = window.winfo_height()

    x = x_window + (gui_width - width) // 2
    y = y_window + (gui_height - height) // 2

    top = ttk.Toplevel(window)
    top.title(title)
    top.geometry(f"{width}x{height}+{x}+{y}")

    label = ttk.Label(top, text=message, wraplength=width - 2 * padding)
    label.pack(padx=padding, pady=padding, side='top')

    ok_button = ttk.Button(top, text="OK", command=on_ok)
    ok_button.pack(pady=10, side='bottom')

    top.focus_set()

    top.protocol("WM_DELETE_WINDOW", on_close)

    top.transient(window)  # Associate the messagebox with the main window
    top.grab_set()  # Make the messagebox modal
    top.wait_window()  # Wait for the Toplevel window to be destroyed

    return result

def update_time():
    global message_box_shown
    global lunch_message_box_shown

    # sound_thread = threading.Thread(target=play_sound(sound_file_path))
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
                    time_label.config(foreground='red')
                    if alarm_var:
                        alarm_window()
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
                    lunch_time_label.config(foreground='red')
                    if lunch_alarm_var:
                        alarm_window()
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
    message_box('Lunch By / Minimum Lunch', 'This section is for employees who reside in California. \n\n\
    Lunch By - The time displayed reflects the latest time you should be clocking out for lunch.\n\n\
    Minimum Lunch - The time displayed reflects the earliest time you should be clocking in from a 30 minute lunch. \n\n\
    If taking a 30 minute lunch - be especially mindful to clock in at a minimum of exactly 30 minutes. If you are short by even 1 second, this will result in a CAML.')

def open_config():
    if config_file_path:
        try:
            subprocess.run(["notepad++", config_file_path])
        except Exception:
            try:
                subprocess.run(["notepad", config_file_path])  # Open with the default text editor on Windows
            except Exception as e:
                print("An error occurred:", e)

def open_configfolder():
    if documents_path:
        try:
            subprocess.run(["Explorer", documents_path])
        except Exception as e:
            print("An error occurred:", e)

def always_on_top():
    if top_var.get():
        window.attributes("-topmost", 1)
    else:
        window.attributes("-topmost", 0)
    write_config('menu')

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

def update_app():

    return

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
            message_box("Error", "You must enter a valid name.")
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
            message_box("Error", e)
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
        message_box("Error", f"Invalid directory: {invalid_path}")

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
    for item in config['Sounds'].items():
        if selected_sound.get() == item[1]:
            sound_in_file = True
            break
    if sound_in_file:
        pass
    else:
        selected_sound.set('Rick')

def remove_sound(sound):

    result = message_box("Confirm", "This will also delete the file, are you sure?")

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
            message_box('Success','Sound successfully removed')
        except Exception as e:
            message_box('Error', e)
    else:
        message_box("Error","The file does not exist")

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
            f.write(task_category.get()+": "+task_name.get()+": "+task_time.get()+": "+task_description.get())
        else:
            f.write("\n\n"+task_category.get()+": "+task_name.get()+": "+task_time.get()+": "+task_description.get())
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
    

# Create the main window
window = ttk.Window(resizable=[False,False], title="Time Tracker", themename="cosmo")
window.bind_all("<Button-1>", lambda event: event.widget.focus_set())

# Style
style = Style()

# Create time variables with default values
clock_in_time = tk.StringVar(value="8:00:00 AM")
clock_out_lunch_time = tk.StringVar(value="12:00:00 PM")
clock_in_lunch_time = tk.StringVar(value="1:00:00 PM")
clock_out_time = tk.StringVar(value="5:00:00 PM")
lunch_by_time = tk.StringVar(value="1:00:00 PM")
add_time_1 = tk.StringVar(value="12:00:00 PM")
add_time_2 = tk.StringVar(value="12:00:00 PM")
time_out = tk.StringVar(value=0.0)
pto_check = tk.BooleanVar()
minimum_lunch = tk.StringVar(value="12:30:00 PM")
alarm_var = tk.BooleanVar()
lunch_alarm_var = tk.BooleanVar()
top_var = tk.BooleanVar()
selected_sound = tk.StringVar(value="rick")
window_mode = tk.StringVar(value="cosmo")
lunch_by_timer = tk.BooleanVar()
clock_out_timer = tk.BooleanVar()
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

# -------------------------------------------------------------------------------------------- #

menu_bar = ttk.Menu(window)
window.config(menu=menu_bar)

file_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open Configuration File", command=open_config)
file_menu.add_command(label="Open Configuration File Folder", command=open_configfolder)
file_menu.add_checkbutton(label="Window Always On Top", variable=top_var, command=always_on_top)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=window.quit)

alarm_menu = ttk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Alarm", menu=alarm_menu)
alarm_menu.add_command(label="Test Alarm", command=alarm_window)
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
theme_menu.add_cascade(label="Light Themes", menu=light_themes)
theme_menu.add_cascade(label="Dark Themes", menu=dark_themes)
window_menu.add_command(label="Save position", command=save_position)
window_menu.add_command(label="Center window", command=lambda i=window: center(i))
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

outer_frame = ttk.Frame(window, padding=10)
outer_frame.grid(row=1)

container_frame = ttk.Frame(outer_frame, padding=10, relief="solid", borderwidth=1)
container_frame.grid(row=1)

container_frame_2_outer = ttk.Frame(outer_frame, padding=10)
container_frame_2_outer.grid(row=2)

container_frame_2 = ttk.Frame(container_frame_2_outer, padding=10, relief="solid", borderwidth=1)
container_frame_2.grid(row=1)

container_frame_3 = ttk.Frame(outer_frame, padding=10, relief="solid", borderwidth=1)
container_frame_3.grid(row=3)

# Create labels and buttons for standard time clock entries
# -------------------------------------------------------------------------------------------- #

# Time Clock Entries
time_clock_entries_label = ttk.Label(container_frame, text="Time Clock Entries", justify='center')
time_clock_entries_label.grid(row=0, column=1, padx=5, pady=5, columnspan=8)

# Clock In Label
clock_in_label = ttk.Label(container_frame, text="Clock In :", anchor="e")
clock_in_label.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Clock In Display
clock_in_time_display = ttk.Entry(container_frame, textvariable=clock_in_time, width= 14)
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
clock_out_1_time_display = ttk.Entry(container_frame, textvariable=clock_out_lunch_time, width= 14)
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
clock_in_2_time_display = ttk.Entry(container_frame, textvariable=clock_in_lunch_time, width= 14)
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
clock_out_2_time_display = ttk.Entry(container_frame, textvariable=clock_out_time, state='readonly', width= 14, justify='center')
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
lunch_by_time_display = ttk.Entry(container_frame_2, textvariable=lunch_by_time, state='readonly', width= 14, justify='center')
lunch_by_time_display.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

# Time Til Clock Out For Lunch Label
lunch_time_label = ttk.Label(container_frame_2, anchor="e")
lunch_time_label.grid(row=3, column=3, padx=5, pady=5)

# 30 Minute Lunch Label
minimum_lunch_label = ttk.Label(container_frame_2, text="Minimum Lunch :", anchor="e")
minimum_lunch_label.grid(row=3, column=4, padx=5, pady=5, sticky="ew")

# 30 Minute Lunch Display
minimum_lunch_display = ttk.Entry(container_frame_2, textvariable=minimum_lunch, state='readonly', width= 14, justify='center')
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
add_time_1_display = ttk.Entry(container_frame_3,textvariable=add_time_1, width= 14)
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
add_time_2_display = ttk.Entry(container_frame_3, textvariable=add_time_2, width= 14)
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
pto_check_box = ttk.Checkbutton(container_frame_3, variable=pto_check, command=lambda i="times": write_config(i))
pto_check_box.grid(row=4, column=6, padx=5, pady=5, sticky="w")

# # Tool tips
tooltip = ToolTip(time_label,"Time until clock out")
tooltip = ToolTip(lunch_time_label,"Time until '"'Lunch By'"'")
# tooltip = Tooltip(minimum_lunch_label,"The earliest time you should be clocking in from a 30 minute lunch")
# tooltip = Tooltip(lunch_by_label,"The latest time you should be clocking out for lunch")

# Import times fromm config file, if file exists
if os.path.exists(config_file_path):
    read_config()

window.after(0,update(),
             update_time(),
             font_change(window),
             set_position(),
             always_on_top(),
             get_sounds(),
             create_sound_menu_entries()
             )

# Run the GUI main loop
window.mainloop()