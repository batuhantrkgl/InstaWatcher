# InstaWatcher: Unethical Way to Stalk

> [!CAUTION]  
> This project is for educational purposes only. You are responsible for all risks that may occur. You have been warned.

> [!WARNING]  
> This project is absolutely unethical. Any factors, physical or emotional consequences resulting from its use are your sole responsibility. You have been warned.

> [!IMPORTANT]  
> Your Instagram account may be suspended as a result of this project. I recommend using another account instead of your own. Again, you have been warned.

---

## What Does This Script Really Do?

First, it opens a browser tab in the background on your device. Then it logs into your account with the username and password you specified in the script.

Then it completes simple things, like the question to save the information and the notification permission.

After making sure you are logged in, it opens the page of the Instagram account you specified. Then, it saves the number of followers, number of followings, biography, name, and profile picture. It also downloads and saves the Instagram page itself.

After saving, it waits 360 seconds for new data. It saves the incoming data and compares it with the old data. If there is a difference, it saves it in a file.

---

## How to Use It?

I assume you have a basic knowledge of Python. After installing the necessary dependencies with pip, you need to edit the file.

1. **Edit the Script**:
   - Replace `LOGIN_USERNAME` with the username of your account.
   - Replace `PASSWORD` with the password of your account.
   - Replace `INSTAGRAM_USER_NAME` with the username of the Instagram account you will be stalking.

2. **Download Geckodriver**:
   - Download geckodriver from [this link](https://github.com/mozilla/geckodriver/releases) and extract it with the `tar -xvf <file name>` command.
   - Replace `GECKODRIVER_PATH` with the location of the file we just extracted (For example: `/home/batuhantrkgl/Downloads/geckodriver`).

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

4. Run the Script:
    ```bash
    python3 watcher.py
    ```