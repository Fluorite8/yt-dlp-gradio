# A gradio web server of yt-dlp.

Supported platforms:

- Linux

- Android (via termux)


## Usage - Linux

Make sure you have python and git avaliable, then install this project:

```bash
pip install git+https://github.com/Fluorite8/yt-dlp-gradio.git
```

Run server:

```bash
yt-dlp-gradio
```

Now you can access the yt-dlp service by visiting http://127.0.0.1:7860.

## Usage - Android(termux)

### Tmoe tools

Tmoe is an excellent script that allows for **one-click installation** of Linux distributions, while also automatically mapping the storage of an Android device to the Linux system. This method is **recommended** for use.

Install Ubuntu-22.04:

```bash
# Install from Github
curl -LO --compressed https://raw.githubusercontent.com/2moe/tmoe/2/2.awk; awk -f 2.awk

# Or from Gitee
curl -LO https://gitee.com/mo2/linux/raw/2/2.awk; awk -f 2.awk
```

Install dependencies:

```bash
sudo apt install git ffmpeg python3-pip python-is-python3
```

Next, simply follow the steps in the "Usage - Linux" section to set up the service on your Android phone.
