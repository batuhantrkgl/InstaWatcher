> [!CAUTION]
> This project is for educational purposes only. You are responsible for all risks that may occur. You have been warned.

> [!WARNING]
> This project is absolutely unethical. Any factors, physical or emotional consequences resulting from its use are your sole responsibility. you have been warned.

> [!IMPORTANT]
> Your Instagram account may be suspended as a result of this project. I recommend using another account instead of your own. Again, you have been warned.


## InstaWatcher, Unethical way to stalk

### What does this script really do?
First, it opens a firefox tab in the background on your device. Then it logs into your account with the username and password you specified in the script.<br>
<br>Then it completes simple things, like the question to save the information and the notification permission.<br>
<br>After making sure you are logged in, it opens the page of the instagram account you specified. Then, it saves the number of followers, number of followers, biography, name, and profile picture. it also downloads and saves the Instagram page itself.
<br><br>After saving, it waits 360 seconds for new data. It saves the incoming data and compares it with the old data. If there is a difference, it saves it in a file.

### How to use it?
<br>I assume you have a basic knowledge of python. After installing the necessary dependencies with pip, you need to edit the file. 

<br>At the top you need to replace LOGIN_USERNAME with the username of your account, PASSWORD with the password of your account and INSTAGRAM_USER_NAME with the username of the instagram account you will be stalking.

<br>Then you need to download geckodriver [from this link](https://github.com/mozilla/geckodriver/releases) and extract it with the `tar -xvf <file name>` command. 

<br>Then replace GECKODRIVER_PATH with the location of the file we just extracted (For example: /home/batuhantrkgl/Downloads/geckodriver)

<br>You have completed the installation part, now let's run it
``` bash
$ python3 watcher.py
```

## TO-DO
- [x] Windows and MacOS support
- [ ] More optimized code
- [x] Use the default browser instead of Firefox
- [x] More colorful and beautiful logs
- [ ] Fix log issues in old_stuff_but_usable folder.
