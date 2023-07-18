# Pomodoro Timer

<img src="[screenshot.PNG](https://github.com/WWWonderer/Pomodoro/blob/main/screenshot.png)" alt="screenshot" width="500"/>

This is a pomodoro timer that automatically registers and visualize uninterrupted working times > 1 minute. Historical data can also be pulled and viewed.

## Platform
This app is built on Windows 10 for personal use. Does not support Linux or macOS. Untested on other Windows versions.

## Requirements
* Python (3.11.4)
* Python libraries: customtkinter==5.2.0, matplotlib==3.7.1, numpy==1.25.0, pillow==9.5.0, freezegun==1.2.2(for testing)

## Usage
After installing the requirements, just run ```src/pomodoro.py```, or to create a single executable as shown below.

## Create exe file
You can bundle all dependencies and create a single executable file with the help of pyinstaller:

```
pip install pyinstaller
cd src
pyinstaller --onefile --windowed -i ../resources/tomato.ico -add-data "../resources;resources" pomodoro.py
```

## Data format
Working time data are saved in ```appData``` with the following format:  
```yyyy.mmdd, daily_time1, daily_time2, ..., yyyy.mmdd, ...```  
where daily times are total number of minutes since midnight.

## Credits
* black and white tomato icon by [Freepik - Flaticon](https://www.flaticon.com/free-icon/tomato_167213), modified versions by me.
* audio files by [Mixkit](https://mixkit.co/free-sound-effects/), slightly edited by me.


## License
[MIT](https://choosealicense.com/licenses/mit/)
