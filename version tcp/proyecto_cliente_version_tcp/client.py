import cv2
import numpy as np
import socket
import struct
from io import BytesIO

cap = cv2.VideoCapture(0,cv2.CAP_V4L2)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.1.60',8080))

while cap.isOpened():
	_, frame = cap.read()
	memfile = BytesIO()
	np.save(memfile, frame)
	memfile.seek(0)
	data = memfile.read()
	##################################
	#print(data)
	#print(len(data))
	#cv2.imshow("frame mandado",frame)
	##################################
	client_socket.sendall(struct.pack("<L", len(data))+data)
		
	if cv2.waitKey(1) & 0xFF == ord('q'):
			break

cap.release()
