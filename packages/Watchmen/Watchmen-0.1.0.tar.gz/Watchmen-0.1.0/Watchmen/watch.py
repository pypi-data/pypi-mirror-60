import cv2 as cv
from skimage.metrics import structural_similarity
import imutils
import os
import time
from robot.libraries.BuiltIn import BuiltIn


def compare_two_image(path1, path2):
    if os.path.exists('../Save Image'):
        print('*INFO* Folder /Save Image exists')
    else:
        os.mkdir('../Save Image')
        print('*INFO* Folder /Save Image crated')
    if os.path.exists(path1) and os.path.exists(path2):
        # load img
        img1 = cv.imread(path1, 1)
        img2 = cv.imread(path2, 1)

        # convert to grey
        gray_img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
        gray_img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

        # SSIM diff img
        (score, diff) = structural_similarity(gray_img1, gray_img2, full=True)
        diff = (diff * 255).astype('uint8')
        print('*INFO* SSIM: {}'.format(score))

        # Threshold diff img
        thresh = cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
        cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # Create frame in diff area
        for c in cnts:
            (x, y, w, h) = cv.boundingRect(c)
            cv.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Show image
        print(score)
        if int(score) < 1.0:
            robotlib = BuiltIn().get_library_instance('BuiltIn')
            cv.imwrite('../Save Image/img' + str(time.time()) + '.png', img2)
            robotlib.fail('*INFO* Save file with difference')
    else:
        raise AssertionError("Path doesnt exists")


def compare_screen(path1):
    if os.path.exists('../Save Image'):
        print('Folder exists')
    else:
        os.mkdir('../Save Image')
    seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
    seleniumlib.capture_page_screenshot('../Save Image/testscreen.png')
    path2 = '../Save Image/testscreen.png'
    if os.path.exists(path1):
        if os.path.exists(path2):
            # load img
            img1 = cv.imread(path1, 1)
            img2 = cv.imread(path2, 1)

            # convert to grey
            gray_img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
            gray_img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

            # SSIM diff img
            (score, diff) = structural_similarity(gray_img1, gray_img2, full=True)
            diff = (diff * 255).astype('uint8')
            print('SSIM: {}'.format(score))

            # Threshold diff img
            thresh = cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
            cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # Create frame in diff area
            for c in cnts:
                (x, y, w, h) = cv.boundingRect(c)
                cv.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # Show image
            print(score)
            if int(score) < 1.0:
                robotlib = BuiltIn().get_library_instance('BuiltIn')
                cv.imwrite('../Save Image/img' + str(time.time()) + '.png', img2)
                robotlib.fail('*INFO* Save file with difference')
        else:
            raise AssertionError("New screen doesnt exist anymore")
    else:
        raise AssertionError("You put bad path")
    if os.path.exists('../Save Image/testscreen.png'):
        os.remove('../Save Image/testcreen.png')


def compare_making_area(x1, y1, x2, y2):
    if os.path.exists('../Create area'):
        print('Folder exists')
    else:
        os.mkdir('../Create area')
    seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
    seleniumlib.capture_page_screenshot('../Create area/testscreen.png')
    img = '../Create area/testscreen.png'
    img_crop = cv.imread(img)
    crop_img = img_crop[int(x1):int(y2), int(y1):int(x2)]  # Crop from {x, y, w, h } => {0, 0, 300, 400}
    cv.imwrite('../Create area/img' + str(time.time()) + '.png', crop_img)


def compare_making_rescreens(*resolution):
    if os.path.exists('../Create rescreens'):
        print('folder exists')
    else:
        os.mkdir('../Create rescreens')
    seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
    robotlib = BuiltIn().get_library_instance('BuiltIn')
    time.sleep(2)
    leng_reso = len(resolution)
    if leng_reso % 2 == 0:
        robotlib.log_to_console(resolution)

        x = leng_reso / 2
        i = 0
        a = 0
        while i < x:
            width = int(resolution[0 + a])
            height = int(resolution[1 + a])

            seleniumlib.set_window_size(width, height)
            time.sleep(1)
            seleniumlib.capture_page_screenshot(
                '../Create rescreens/rescreen_' + str(width) + 'x' + str(height) + '.png')
            a += 2
            i += 1
    else:
        raise AssertionError("Bad numbers of resolution")


def compare_screen_area(x1, y1, x2, y2, path1):
    if os.path.exists('../Save Image area'):
        print('Folder exists')
    else:
        os.mkdir('../Save Image area')
    seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
    seleniumlib.capture_page_screenshot('../Save Image area/test_screen.png')
    path2 = '../Save Image area/test_screen.png'
    if os.path.exists(path1):
        if os.path.exists(path2):
            # load img
            img1 = cv.imread(path1, 1)
            img2 = cv.imread(path2, 1)

            # convert to grey
            gray_img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
            gray_img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

            # spliting area
            crop_img = gray_img2[int(x1):int(y2), int(y1):int(x2)]  # Crop from {x, y, w, h } => {0, 0, 300, 400}

            # SSIM diff img
            (score, diff) = structural_similarity(gray_img1, crop_img, full=True)
            diff = (diff * 255).astype('uint8')
            print('SSIM: {}'.format(score))

            # Threshold diff img
            thresh = cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
            cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # Create frame in diff area
            for c in cnts:
                (x, y, w, h) = cv.boundingRect(c)
                cv.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Show image
            print(score)
            if int(score) < 1.0:
                robotlib = BuiltIn().get_library_instance('BuiltIn')
                cv.imwrite('../Save Image area/img' + str(time.time()) + '.png', img2)
                robotlib.fail('*INFO* Save file with difference')
        else:
            raise AssertionError("New screen doesnt exist anymore")
    else:
        raise AssertionError("You put bad path")
    if os.path.exists('../Save Image area/test_screen.png'):
        os.remove('../Save Image area/test_screen.png')


def compare_screen_without_areas(path1, *args):
    if os.path.exists('../Save Image areas'):
        print('Folder exists')
    else:
        os.mkdir('../Save Image areas')
    seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
    seleniumlib.capture_page_screenshot('../Save Image areas/test_screen.png')
    path2 = '../Save Image areas/test_screen.png'
    if os.path.exists(path1) and os.path.exists(path2):
        lt = len(args)
        img1 = cv.imread(path1, 1)
        img2 = cv.imread(path2, 1)
        if lt % 4 == 0:
            robotlib = BuiltIn().get_library_instance('BuiltIn')
            x = lt / 4
            robotlib.log_to_console(x)
            i = 0
            a = 0
            while i < x:
                color = (0, 0, 0)
                x1 = int(args[0 + a])
                y1 = int(args[1 + a])
                x2 = int(args[2 + a])
                y2 = int(args[3 + a])

                cv.rectangle(img1, (x1, y1), (x2, y2), color, -1)
                cv.rectangle(img2, (x1, y1), (x2, y2), color, -1)
                a += 4
                i += 1
            cv.namedWindow("image", cv.WINDOW_NORMAL)

            # convert to grey
            gray_img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
            gray_img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

            # SSIM diff img
            (score, diff) = structural_similarity(gray_img1, gray_img2, full=True)
            diff = (diff * 255).astype('uint8')
            print('SSIM: {}'.format(score))

            # Threshold diff img
            thresh = cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
            cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            # Create frame in diff area
            for c in cnts:
                (x, y, w, h) = cv.boundingRect(c)
                cv.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Show image
            print(score)
            if int(score) < 1.0:
                robotlib = BuiltIn().get_library_instance('BuiltIn')
                cv.imwrite('../Save Image areas/img' + str(time.time()) + '.png', img2)
                robotlib.fail('*INFO* Save file with difference')
    else:
        raise AssertionError("Path doesnt exists")
