![image](https://github.com/nathanwlarsen/TimeTracker/blob/master/2023-11-16%2008_00_28-TimeTracker.png)

# TimeTracker
A python app created for grabbing time entries from the Workday website, using either the Chrome or Microsoft Edge browser. The app will calculate Lunch By, Minimum Lunch, and Clock Out times as each time is updated. Lunch By and Minimum Lunch times are based on the California meal break laws - displaying these times ensures that employees are adhering to these meal break requirements.

# Menu
The following items can be found in the menu bar located at the top of the app

## File
The file menu features an option to open the configuration file for reviewing as well as an option to exit the app.

## Alarm
The app features two timers: the Lunch By timer and the Clock Out timer. When there is 1 minute left on a timer, the selected alarm sound will play and a messagebox will display, informing the user it is time to begin clocking out. Alarms sounds can be added and removed by placing new sound files in the alarm_sounds folder - located in the applications root directory. Currently this only accepts .wav files. The Clock Out alarm and the Clock Out (Lunch) alarm can be toggled in this menu as well, if the user feels they are not necessary. The Alarm will utilize a Windows toast notification. When the notification is clicked, the alarm will silence - if the user fails to click the notification within the notification timeout window, the user can silence the alarm either by selecting 'Silence Alarm' from the Alarm menu, or by simply restarting the application.

## Window
The window menu contains the themes setting - allowing the user to select either a light or dark theme for the app. There is also a setting to save the windows current position, to be loaded in that same position the next time the app is run. You can select the Center Window option to center the app on your main display (default). This menu also features 3 radiobuttons to toggle the visibility of different sections of the app. Currently these sections include the CA Associates, Additional Entries, and Time Zones sections. Note: if the CA Associates section is hidden, the Lunch By timer and Clock Out (Lunch) Alarm will be disabled and unable to be toggled back on until the section is toggled back on.

### Time Zones
The Time Zones section, when toggled on, will display all of the US time zones at the bottom of the application. When hovering over one of these labels, all of the times in the app will temporarily be converted to that time zone, providing some insight as to what their current schedule will look like to coworkers located in other parts of the US.

## Entries
The entries menu currently only allows you to highlight each of the first three times or all of them. This serves as a reminder that the respective time has not yet been updated. By defualt, when the app is opened, the entry boxes will be highlighted red if the times stored in the config file were not grabbed on the current day. Each entry box will return to the default state once updated.

## Timers
The timers menu features two radio buttons to toggle the Clock Out and Lunch By timers.

## Tasks
The Tasks menu is a newer feature currently being worked on. Toggle Task View will add a frame to the top of the app, allowing the user to Start and Stop a task with a provided Category, Name, and Description. When the task is stopped, the time spent on the task as well as all of the previously mentioned values, will be logged to a text file stored in a folder in the users Documents folder. The View Tasks option will open a window on top of the app, allowing you edit the tasks previously recorded and save the changes directly to the text file. Create Chart will use the matplotlib library to create a graph leveraging time spent in each category of task.

## Help
The help menu features one option - to open this README file. It is my hope that this file will answer all the questions anyone might have as far as the operation and features of the app.

# Upcoming Features
Task view will feature an entry widget allowing the user to specify time spent on a previously completed task. This will require a Log button to be added since the Start and Stop buttons will not be utilized.


# Using TimeTracker
TimeTracker is fairly straightforward to use. When clocking in first thing in the morning, 'Clock In' time should be updated to reflect the time displayed in Workday. The 'Grab Time' button to the right of each time clock entry can make this very seemless by switching over to the browser window and grabbing the time for you. A few caveats to this feature are as follows: 1) The Workday tab must be the active tab in the browser 2) Currently only Google Chrome and Edge are supported 3) The Workday tab must display "Checked in/out at" and whatever time was last clocked and finally 4) If using multiple browser windows, the last active browser window is what the app will attempt to grab the time from

As time clock entries are updated, the Clock Out time will update automatically. If you have the CA Associates section visible, the Lunch By and Minimum Lunch times will also automatically update, based on your intitial Clock In time and your Clock Out (Lunch) time.

The Additional Lunch section can be used just like the first section - times can be updated manually or grabbed from Workday. This section will not affect your Clock Out time unless you indicate that you do not intend to use PTO, in which case, your Clock Out time will adjust to ensure your time worked comes out to 8 hours. Once both Additional Entries have been updated, the 'Time Out' will update, representing the amount of time you were away, in decimal form - this is useful when requesting PTO through workday.
