import os
import numpy as np
import cv2
import tkinter
from tkinter import filedialog

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
print("Loading..")
import tensorflow.keras


main_win = tkinter.Tk()
main_win.geometry("300x100")

main_win.sourceFile = ''


def chooseFile():
    main_win.sourceFile = filedialog.askopenfilename(
        parent=main_win, initialdir=os.getcwd() + '/test', title='Please select a file')
    if main_win.sourceFile:
        main_win.destroy()


b_chooseFile = tkinter.Button(
    main_win, text="Choose File", width=20, height=3, command=chooseFile)
b_chooseFile.place(x=75, y=20)
b_chooseFile.width = 100

main_win.mainloop()

if main_win.sourceFile:
    print("File: " + main_win.sourceFile)
    imgpath = main_win.sourceFile
else:
    print("Invalid File!")
    exit()

labels = ['yes',
          'no']

print("Please wait...")
np.set_printoptions(suppress=True)
model = tensorflow.keras.models.load_model('keras_model.h5', compile=False)
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)


def detect(img):
    img = cv2.resize(img, (224, 224))
    image_array = np.asarray(img)
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    # print(prediction)
    prediction_new = prediction[0].tolist()
    detected_action = prediction_new.index(max(prediction_new))
    print("Tumor Detected: " + labels[detected_action])
    detected_acc = max(prediction_new)
    print("Accuracy of Neural Network: " + str(detected_acc))
    return labels[detected_action], str(round(detected_acc, 2))


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged


def segment_img():
    image = cv2.imread(imgpath)
    image = cv2.resize(image, (224, 224))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY, 0.7)
    cv2.imshow("Grayscale Image", gray)

    (T, thresh) = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY)
    cv2.imshow("Threshold Image", thresh)

    (T, threshInv) = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("Inverted Threshold Image", threshInv)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cv2.imshow("Morphological transformed Image", closed)

    closed = cv2.erode(closed, None, iterations=14)
    closed = cv2.dilate(closed, None, iterations=13)
    cv2.imshow("Closed segmented Image", closed)

    ret, mask = cv2.threshold(closed, 155, 255,
                              cv2.THRESH_BINARY)  # apply AND operation on image and mask generated by thrresholding
    final = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow("bitwise AND segmented Image", final)

    canny = auto_canny(closed)
    cv2.imshow("Canny segmented Image", canny)

    (cnts, _) = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image, cnts, -1, (0, 0, 255), 2)
    cv2.imshow("Final segmented image", image)


def do_start():
    frame = cv2.imread(imgpath)
    frame = cv2.flip(frame, 1, 1)
    frame = cv2.resize(frame, (224, 224))

    detected_label, _ = detect(frame)
    text = ('Tumor detected' if detected_label == 'yes' else 'Tumor not detected')
    cv2.putText(frame, text, (2, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, ((0, 0, 255) if detected_label == 'yes' else (0, 255, 0)), 2)

    cv2.imshow("Classification", frame)

    if detected_label == 'yes':
        segment_img()

    cv2.waitKey(1000)
    input("")
    cv2.destroyAllWindows()


if __name__ == '__main__':
    do_start()
