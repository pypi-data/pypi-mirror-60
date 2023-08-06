import os
import sys
import argparse

import cv2


class ImageCroquis:

    def __init__(self, inp, otp_dir):
        self.inp_img = inp
        self.output_dir = otp_dir

    def run(self):
        #read image
        image = cv2.imread(self.inp_img)

        #check if images exists
        if image is None:
            print("can not find image")
            sys.exit()

        #convert to gray scale
        output = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Apply gaussian blur
        output = cv2.GaussianBlur(output, (3,3), 1)

        #detect edges in the image
        output = cv2.Laplacian(output, -1, ksize=5)

        #invert the binary image
        output = 255 - output

        #binary thresholding
        ret, output = cv2.threshold(output, 150, 255, cv2.THRESH_BINARY)

        # Store the image
        outp_filep = os.path.join(self.output_dir, 'img.jpeg')
        cv2.imwrite(outp_filep, output)
        print("Output image is saved in the specified path")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--img-path",
            help="Specify the image path")
    parser.add_argument("-o", "--output-dir",
            help="Directory where you want to the output")
    args = parser.parse_args()

    process = ImageCroquis(args.img_path, args.output_dir)
    process.run()

if __name__ == "__main__":
    main()
