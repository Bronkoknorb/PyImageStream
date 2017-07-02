#!/usr/bin/env python3

# Configuration
JPEG_QUALITY = 70
CAMERA_INDEX = 0
WEBSERVER_PORT = 8888
WIDTH = 1920
HEIGHT = 1080

# Delay stopping the camera after all clients have disconnected
DELAY_CAMERA_STOP_SECONDS = 7

import tornado.ioloop
import tornado.web
import tornado.websocket

import os

import io
from PIL import Image

import pygame.camera
import pygame.image


class Camera:

    def __init__(self):
        print("Initializing camera...")
        pygame.camera.init()
        camera_name = pygame.camera.list_cameras()[CAMERA_INDEX]
        self._cam = pygame.camera.Camera(camera_name, (WIDTH, HEIGHT))
        print("Camera initialized")
        self.is_started = False
        self.stop_requested = False

    def request_start(self):
        if self.stop_requested:
            print("Camera continues to be in use")
            self.stop_requested = False
        if not self.is_started:
            self._start()

    def request_stop(self):
        if self.is_started and not self.stop_requested:
            self.stop_requested = True
            print("Stopping camera in " + str(DELAY_CAMERA_STOP_SECONDS) + " seconds...")
            tornado.ioloop.IOLoop.current().call_later(DELAY_CAMERA_STOP_SECONDS, self._stop)

    def _start(self):
        print("Starting camera...")
        self._cam.start()
        print("Camera started")
        self.is_started = True

    def _stop(self):
        if self.stop_requested:
            print("Stopping camera now...")
            self._cam.stop()
            print("Camera stopped")
            self.is_started = False
            self.stop_requested = False

    def get_jpeg_image_bytes(self):
        img = self._cam.get_image()
        imgstr = pygame.image.tostring(img, "RGB", False)
        pimg = Image.fromstring("RGB", img.get_size(), imgstr)
        with io.BytesIO() as bytesIO:
            pimg.save(bytesIO, "JPEG", quality=JPEG_QUALITY, optimize=True)
            return bytesIO.getvalue()


camera = Camera()


class ImageWebSocket(tornado.websocket.WebSocketHandler):
    clients = set()

    def open(self):
        ImageWebSocket.clients.add(self)
        print("WebSocket opened from: " + self.request.remote_ip)
        camera.request_start()

    def on_message(self, message):
        jpeg_bytes = camera.get_jpeg_image_bytes()
        self.write_message(jpeg_bytes, binary=True)

    def on_close(self):
        ImageWebSocket.clients.remove(self)
        print("WebSocket closed from: " + self.request.remote_ip)
        if len(ImageWebSocket.clients) == 0:
            camera.request_stop()


script_path = os.path.dirname(os.path.realpath(__file__))
static_path = script_path + '/static/'

app = tornado.web.Application([
        (r"/websocket", ImageWebSocket),
        (r"/(.*)", tornado.web.StaticFileHandler, {'path': static_path, 'default_filename': 'index.html'}),
    ])
app.listen(WEBSERVER_PORT)

print("Starting server: http://localhost:" + str(WEBSERVER_PORT) + "/")

tornado.ioloop.IOLoop.current().start()
