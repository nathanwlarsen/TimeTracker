![image](https://github.com/nathanwlarsen/TimeTracker/assets/21229245/f75b9f42-e21a-4ef1-b5e4-a936ff0c24d0)

# TimeTracker
A python app created for grabbing time entries from the Workday website, using either the Chrome or Microsoft Edge browser. The app will calculate Lunch By, Minimum Lunch, and Clock Out times as each time is updated. Lunch By and Minimum Lunch times are based on the California meal break laws - displaying these times ensures that employees are adhering to these meal break requirements.

# Menu
The following items can be found in the menu bar located at the top of the app

# File
The file menu allows you to open the configuration file as well as the folder where it is contained. It also has an Window Always On Top setting that can be toggled - allowing the window to remain above other windows when clicking away from the app. The file menu also features an Exit option which will kill the app.

## Alarm
The app features two timers: the Lunch By timer and the Clock Out timer. When there is 1 minute left on a timer, the selected alarm sound will play and a messagebox will display, informing the user it is time to begin clocking out. Alarms sounds can be added and removed from the alarm menu. Currently this only accepts .wav files. The Clock Out alarm and the Clock Out (Lunch) alarm can be toggled in this menu as well, if the user feels they are not necessary.

## Window
The window menu contains the themes setting - allowing the user to select either a light or dark theme for the app, utilizing ttkbootstrap. There is also a setting to save the windows current position, to be loaded in that same position the next time the app is run. You can select the Center Window option to center the app on your main display (default).

## Entries
The entries menu currently only allows you to highlight each of the first three times or all of them. This serves as a reminder that the respective time has not yet been updated. By defualt, when the app is opened, the entry boxes will be highlighted red if the times stored in the config file were not grabbed on that day. Each entry box will return to the default state once updated.

## Timers
The timers menu features two radio buttons to toggle the Clock Out and Lunch By timers.

## Tasks
The Tasks menu is a newer features currently being worked on. Toggle Task View will add a frame to the top of the app, allowing the user to Start and Stop a task with a provided Category, Name, and Description. When the task is stopped, the time spent on the task as well as all of the previously mentioned values, will be logged to a text file stored in a folder in the users Documents folder. The View Tasks option will open a window on top of the app, allowing you edit the tasks previously recorded and save the changes directly to the text file. Create Chart will use the matplotlib library to create a graph leveraging time spent in each category of task.

# Upcoming Features
Task view will feature an entry widget allowing the user to specify time spent on a previously completed task. This will require a Log button to be added since the Start and Stop buttons will not be utilized.
