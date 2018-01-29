# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import pygame
import os
import signal
import motors
import sys


class CollectTrainingData(object):
    def __init__(self):

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1
        self.temp_label = np.zeros((1, 4), 'float')

        os.environ["SDL_VIDEODRIVER"] = "dummy"
        signal.signal(signal.SIGINT, signal.default_int_handler)

        pygame.init()
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        pygame.display.init()

        pygame.joystick.quit()
        pygame.joystick.init()

        joystick_count = pygame.joystick.get_count()

        if joystick_count < 1:
            print("No joysticks found.")

            sys.exit()

        print("Found " + str(joystick_count) + " joysticks.")

        joy = pygame.joystick.Joystick(0)
        joy.init()

        self.collect_image()

    def collect_image(self):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print("Start collecting images...")
        e1 = cv2.getTickCount()
        image_array = np.zeros((1, 38400))
        label_array = np.zeros((1, 4), 'float')

        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 20
        raw_capture = PiRGBArray(camera, size=(640, 480))

        # allow the camera to warmup
        time.sleep(2)

        # capture frames from the camera
        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
            image = frame.array
            # select lower half of the image
            roi = image[120:240, :]
            # reshape the roi image into one row array
            temp_array = roi.reshape(1, 38400).astype(np.float32)

            cv2.imwrite('training_images/frame{:>05}.jpg'.format(frame), image)

            frame += 1
            total_frame += 1

            # show the frame
            cv2.imshow("Frame", image)
            key = cv2.waitKey(1) & 0xFF

            # get input from human driver

            # complex orders
            if joy.get_hat(0) == (1, 1):
                print("Forward Right")
                image_array = np.vstack((image_array, temp_array))
                label_array = np.vstack((label_array, self.k[1]))
                saved_frame += 1
                # motor forward right

            elif joy.get_hat(0) == (1, -1):
                print("Forward Left")
                image_array = np.vstack((image_array, temp_array))
                label_array = np.vstack((label_array, self.k[0]))
                saved_frame += 1

            elif joy.get_hat(0) == (-1, 1):
                print("Reverse Right")

            elif joy.get_hat(0) == (-1, -1):
                print("Reverse Left")

            # simple orders
            elif joy.get_hat(0) == (1, 0):
                print("Forward")
                saved_frame += 1
                image_array = np.vstack((image_array, temp_array))
                label_array = np.vstack((label_array, self.k[2]))

            elif joy.get_hat(0) == (-1, 0):
                print("Reverse")
                saved_frame += 1
                image_array = np.vstack((image_array, temp_array))
                label_array = np.vstack((label_array, self.k[3]))

            elif joy.get_hat(0) == (0, 1):
                print("Right")
                image_array = np.vstack((image_array, temp_array))
                label_array = np.vstack((label_array, self.k[1]))
                saved_frame += 1

            elif joy.get_hat(0) == (0, -1):
                print("Left")
                image_array = np.vstack((image_array, temp_array))
                label_array = np.vstack((label_array, self.k[0]))
                saved_frame += 1

            elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                print("exit")

        # save training images and labels
        train = image_array[1:, :]
        train_labels = label_array[1:, :]

        # save training data as a numpy file
        file_name = str(int(time.time()))
        directory = "training_data"
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            np.savez(directory + '/' + file_name + '.npz', train=train, train_labels=train_labels)
        except IOError as e:
            print(e)

        e2 = cv2.getTickCount()
        # calculate streaming duration
        time0 = (e2 - e1) / cv2.getTickFrequency()
        print("Streaming duration:", time0)

        print(train.shape)
        print(train_labels.shape)
        print("Total frame:", total_frame)
        print("Saved frame:", saved_frame)
        print("Dropped frame", total_frame - saved_frame)
