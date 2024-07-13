from setuptools import setup, find_packages

setup(
    name='yt-dlp-gradio',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'yt-dlp-gradio=yt_dlp_gradio.app:app',
        ],
    },
    install_requires=[
        "gradio==4.36.1",
        "yt-dlp"
    ],
)
