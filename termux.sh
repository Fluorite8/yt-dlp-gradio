#!/data/data/com.termux/files/usr/bin/bash
# Set up the termux as a environment with python-pip and aria2, then install yt-dlp and gradio in python

# Update Termux packages
pkg update && pkg upgrade -y

# Install Python and pip
pkg install -y python python-pip

# Install aria2
pkg install -y aria2

# Install yt-dlp
pip install yt-dlp

# Install gradio
pip install gradio

# Add app.py into .bashrc to run on startup
echo "python app.py" >> ~/.bashrc

echo "Setup complete!"
