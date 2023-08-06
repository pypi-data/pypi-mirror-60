import StereoCapture as sc
import cv2
import numpy as np

class PickPlace3D():
    def __init__(self,stereo_camera):
        self.stereo_camera = stereo_camera

    def connect(self):
        return self.stereo_camera.connect()

    def run(self):
        while(True):
            res,imageL,imageR = self.stereo_camera.grab()
            if (res):
                stereo_image = np.concatenate((imageL, imageR), axis=1)
                stereo_image_resized = cv2.resize(stereo_image,(1280,480))
                cv2.imshow('Stereo Image', stereo_image_resized)
                k = cv2.waitKey(1)
                if k == ord('q'):
                    break

if __name__ == "__main__":
    stcam = sc.StereoCapture(sc.StereoCaptureCVDual(sc.CVCapture(0)))
    pp = PickPlace3D(stcam)
    pp.run()