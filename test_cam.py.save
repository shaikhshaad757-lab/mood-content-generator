import cv2
cap = cv2.VideoCapture(0)
print("Opened:", cap.isOpened())

ret, frame = cap.read()
print("Captured:", ret)

if ret:
    print("Frame shape:", frame.shape)
    cv2.imwrite("cam_test.jpg", frame)

cap.release()

