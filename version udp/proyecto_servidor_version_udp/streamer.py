from __future__ import print_function
import cv2
import pickle
import numpy as np
import socket
import struct
import threading

#import base64

MAX_DGRAM = 2**16

class Streamer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.ret_img = None
        self.s =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("192.168.1.60", 1337))
        # self.s = sock_connection
        self.back_sub = cv2.createBackgroundSubtractorMOG2(history=700, varThreshold=25,detectShadows=True)
        self.kernel = np.ones((20,20),np.uint8)

        print("-> waiting for connection")

    def run(self):
        dat = b''   
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            print(seg[0])
            if struct.unpack("B", seg[0:1])[0] == 1:
                print("finish emptying buffer")
                break
                
        while True:
            seg, addr = self.s.recvfrom(MAX_DGRAM)
            if struct.unpack("B", seg[0:1])[0] > 1:
                dat += seg[1:]
            else:
                dat += seg[1:]
                img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
                if img is None:
                    print("en este fallaria")
                else:
                    #cv2.imshow('frame', img)
                    fg_mask = self.back_sub.apply(img)
                    fg_mask = cv2.morphologyEx(fg_mask,cv2.MORPH_CLOSE,self.kernel)
                    fg_mask = cv2.medianBlur(fg_mask,5)
                    _,fg_mask = cv2.threshold(fg_mask,127,255,cv2.THRESH_BINARY)
                    fg_mask_bb = fg_mask
                    contours,hirarchy = cv2.findContours(fg_mask_bb,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
                    areas = [cv2.contourArea(c) for c in contours]
                    
                    if len(areas) > 0 :
                        max_index = np.argmax(areas)
                        cnt = contours[max_index]
                        x,y,w,h = cv2.boundingRect(cnt)
                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
                        x2 = x+int(w/2)
                        y2 = y+int(h/2)
                        cv2.circle(img,(x2,y2),4,(0,255,0),-1)
                        text = "x:"+str(x2)+",y:"+str(y2)
                        cv2.putText(img,text,(x2-10,y2-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
                        self.ret_img = cv2.imencode('.jpg',img)[1].tobytes()
                    
                dat = b''

        cv2.destroyAllWindows()
        s.close()

    def stop(self):
        self.running = False

    def get_jpeg(self):
        return self.ret_img
