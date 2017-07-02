PyImageStream - Python WebSocket Image Stream
=============================================

Streams images (JPEG) from a WebCam (USB camera or Raspberry Pi Camera Module) via a WebSocket to a Browser to show
video.

Prerequisites
-------------

### Install dependencies

Python 3

    sudo apt install python3

Tornado Web server

    sudo pip3 install tornado

Python Imaging Library

    sudo apt install python3-pil

Pygame (used for capturing images from a Webcam)

    sudo apt install python3-pygame

### Connect your Webcam

The Webcam has to compatible with Video4Linux2 and should appear as /dev/video0 in the filesystem.
Most USB Webcams support the UVC standard and should work just fine.
The Raspberry Pi Camera Module can be made available as a V4L2 device by loading a kernel module:

    sudo modprobe bcm2835-v4l2

Installation
------------

Clone the repository to some directory and change to that directory:

    git clone https://github.com/Bronkoknorb/PyImageWebSocket.git
    cd PyImageStream

Start using

    python3 main.py

The stream can then be watched on: http://YOUR_HOST:8888/ (where YOUR_HOST is your host name or IP address or localhost
on the same machine).
