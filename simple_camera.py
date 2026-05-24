# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import argparse
import time

import cv2

""" 
gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of each camera pane in the window on the screen
Default 1920x1080 displayd in a 1/4 size window
"""

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def show_camera(display_height, max_fps):
    window_title = "CSI Camera"
    display_width = int(display_height * 16 / 9)
    frame_interval = 1.0 / max_fps

    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    pipeline = gstreamer_pipeline(
        flip_method=0,
        display_width=display_width,
        display_height=display_height,
    )
    print(pipeline)
    video_capture = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    if video_capture.isOpened():
        try:
            window_handle = cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            last_frame_time = 0.0
            while True:
                ret_val, frame = video_capture.read()

                now = time.monotonic()
                if now - last_frame_time < frame_interval:
                    keyCode = cv2.waitKey(1) & 0xFF
                    if keyCode == 27 or keyCode == ord('q'):
                        break
                    continue
                last_frame_time = now

                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, frame)
                else:
                    break 
                keyCode = cv2.waitKey(1) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSI Camera viewer")
    parser.add_argument("--height", type=int, default=540,
                        help="Display height in pixels (width scales to 16:9). Default: 540")
    parser.add_argument("--fps", type=int, default=15,
                        help="Max display refresh rate in frames per second. Default: 15")
    args = parser.parse_args()
    show_camera(args.height, args.fps)
