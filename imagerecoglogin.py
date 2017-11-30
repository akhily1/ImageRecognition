import cv2
import numpy as np
from PIL import Image, ImageTk
import Tkinter as tk
from google.cloud import storage
from firebase import firebase
import struct
import urllib
import urllib2
import cookielib
import json
from bs4 import BeautifulSoup
import requests
import re
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="images-0e7b0b33f965.json"

name = ""

#uses the name to search for an image of the person
#also fetches information from firebase
class Profile():
                window = 0
                idNum = 0
                name = ""
                number = 0
                country = ""
                position = ""
                def __init__(self, master, idNum):
                                self.window = tk.Toplevel(root)
                                self.window.geometry("815x825")
                                self.idNum = idNum
                                userAtts = firebase.get('/' + str(self.idNum), None)
                                userID = userAtts.get('ID')
                                tempName = ""
                                if userID == self.idNum:
                                                self.name = userAtts.get('Name')
                                                tempName = self.name
                                                self.position = userAtts.get('Position')
                                                self.number = userAtts.get('Number')
                                                self.country = userAtts.get('Country')
                                print(self.idNum)
                                self.getOnlineImages()
                                img = ImageTk.PhotoImage(Image.open('Pictures/' + tempName + '/image_3.jpg'))
                                label = tk.Label(self.window, image = img)
                                label.pack()
                                label2 = tk.Label(self.window, text = tempName)
                                label2.pack()
                                label3 = tk.Label(self.window, text = self.position + " # " + self.number + " of " + self.country)
                                label3.pack()
                                self.window.mainloop()
                                
                def getOnlineImages(self):
                                original = self.name
                                image_type="image"
                                self.name= self.name.split()
                                self.name='+'.join(self.name)
                                url="https://www.google.co.in/search?q="+self.name+"&source=lnms&tbm=isch"
                                print url
                                DIR="Pictures"
                                header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
                                }
                                soup = self.parseData(url,header)
                                ActualImages=[]
                                for a in soup.find_all("div",{"class":"rg_meta"}):
                                                link, Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
                                                ActualImages.append((link,Type))
                                if not os.path.exists(DIR):
                                                os.mkdir(DIR)
                                DIR = os.path.join(DIR, original)

                                if not os.path.exists(DIR):
                                                os.mkdir(DIR)
                                for i , (img , Type) in enumerate( ActualImages[0:10]):
                                                try:
                                                                req = urllib2.Request(img, headers={'User-Agent' : header})
                                                                raw_img = urllib2.urlopen(req).read()
                                                                cntr = len([i for i in os.listdir(DIR) if image_type in i]) + 1

                                                                if len(Type)==0:
                                                                                f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+".jpg"), 'wb')
                                                                else :
                                                                                f = open(os.path.join(DIR , image_type + "_"+ str(cntr)+"."+Type), 'wb')

                                                                f.write(raw_img)
                                                                f.close()
                                                except Exception as e:
                                                                print e

                def parseData(self, url, header):
                                return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)),'html.parser')                               
                
#tests recognition algorithm
#identifies face captured by camera
class FaceRecognize():
                idNum = 0
                def __init__(self, master):
                                numValues = []
                                recognizer.read('imageData.yml')
                                cascadePath = "haarcascade_frontalface_default.xml"
                                faceCascade = cv2.CascadeClassifier(cascadePath);
                                cam = cv2.VideoCapture(0)
                                while True:
                                                currentVal = 0
                                                ret, im =cam.read()
                                                gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
                                                faces=faceCascade.detectMultiScale(gray, 1.2,5)
                                                for(x,y,w,h) in faces:
                                                                cv2.rectangle(im,(x,y),(x+w,y+h),(0, 0, 255),2)
                                                                self.idNum, conf = recognizer.predict(gray[y:y+h,x:x+w])
                                                                currentVal = self.idNum
                                                                numValues.append(self.idNum)
                                                                cv2.waitKey(100)
                                                                print(self.idNum)
                                                cv2.imshow('im',im)
                                                if (cv2.waitKey(1) == ord('q')):
                                                                break
                                                elif numValues.count(currentVal) > 7:
                                                                break
                                cam.release()
                                cv2.destroyAllWindows()
                                self.startNewWindow()

                def startNewWindow(self):
                                profile = Profile(root, self.idNum)

#identifies faces using cv2 CascadeClassifier function
class Fifth():
                idNum = ""
                def __init__(self, master, idNum):
                                self.idNum = idNum
                                IdVals, faces = self.startDataTraining()
                                recognizer.train(faces, np.array(IdVals))
                                recognizer.write('imageData.yml')
                                cv2.destroyAllWindows()
                                self.uploadRecognizer()

                def startDataTraining(self):
                                allFaces = []
                                allID = []
                                result = firebase.get('/', None)
                                print(len(result))
                                for idX in range(1, len(result)):
                                                for imageY in range(0, 64):
                                                                pathWay = 'dataSet/User.' + str(idX) + '.' + str(imageY)
                                                                print(pathWay)
                                                                imageBlob = bucket.blob(pathWay)
                                                                print(imageBlob)
                                                                url = imageBlob.public_url
                                                                req = urllib.urlopen(url)
                                                                arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
                                                                img = cv2.imdecode(arr,-1)
                                                                localID = idX
                                                                allFaces.append(img)
                                                                allID.append(localID)
                                                                cv2.imshow("image", img)
                                                                cv2.waitKey(10)
                                return allID, allFaces

                def uploadRecognizer(self):
                                imageBlob = bucket.blob("/info")
                                imageBlob.upload_from_filename("imageData.yml")

#asks user if they want to add more data or publish data to yml output file
class Choice():
                idNum = 1
                window = 0
                def __init__(self, master, idNum):
                                self.window = tk.Toplevel(root)
                                self.idNum = idNum
                                self.window.geometry("300x150")
                                button1 = tk.Button(self.window, text="Add More Data", width=15, height=3, command = self.addData)
                                button1.pack()
                                button2 = tk.Button(self.window, text="Finalize Data", width=15, height=3, command = self.finalize)
                                button2.pack()

                def addData(self):
                                self.window.destroy()
                                second = Second(root)

                def finalize(self):
                                self.window.destroy()
                                finalize = Fifth(root, self.idNum)

#reads images from camera and outputs to local storage
#also uploads images to firebase storage
class Fourth():
                idNum = 0
                path = 'dataSet'
                sampleNum = 0
                def __init__(self, master, idNum, sampleNum):
                                self.idNum = idNum
                                self.sampleNum = sampleNum
                                self.startCollection()
                                print("SampleNum is " + str(self.sampleNum))
                                #self.moveNext()
                                
                def startCollection(self):
                                sampleNum = self.sampleNum
                                print("First" + str(sampleNum))
                                highestValue = sampleNum
                                cam = cv2.VideoCapture(0)
                                while True:
                                                ret, image = cam.read()
                                                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                                                faces = faceDetect.detectMultiScale(gray, 1.3, 5)
                                                for (x, y, w, h) in faces:
                                                                sampleNum += 1
                                                                cv2.imwrite("dataSet/User."+str(self.idNum)+"."+ str(sampleNum)+".jpg", gray[y:y+h,x:x+w])
                                                                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                                                                cv2.waitKey(100)
                                                if cv2.waitKey(100) & 0xFF == ord('q'):
                                                                break
                                                elif sampleNum > highestValue + 15:
                                                                break
                                                cv2.imshow("Face", image)
                                                cv2.waitKey(1)
                                cam.release()
                                cv2.destroyAllWindows()
                                print("Second" + str(sampleNum))
                                if sampleNum > 58:
                                                self.uploadFirebase()
                                else:
                                                third = Third(root, self.idNum, sampleNum)

                def uploadFirebase(self):
                                imageBlob = bucket.blob("/")
                                imagePaths = [os.path.join(self.path, f) for f in os.listdir(self.path)]
                                num = 0
                                for imagePath in imagePaths:
                                                if "Store" not in imagePath:
                                                                numIDImage = int(os.path.split(imagePath)[-1].split('.')[1])
                                                                if numIDImage == self.idNum:
                                                                                imageBlob = bucket.blob("dataSet/User." + str(self.idNum) +"."+ str(num))
                                                                                imageBlob.upload_from_filename(imagePath)
                                                                                num += 1
                                self.moveNext()

                def moveNext(self):
                                choice = Choice(root, self.idNum)

#asks user to train data
class Third():
                window = 0
                name = ""
                idNum = 0
                sampleNum = 0
                def __init__(self, master, idNum, sampleNum):
                                self.window = tk.Toplevel(root)
                                self.name = name
                                self.idNum = idNum
                                self.sampleNum = sampleNum
                                self.window.geometry("300x150")
                                button1 = tk.Button(self.window, text="Train Data", width=15, height=3, command = self.trainData)
                                button1.pack()

                def trainData(self):
                                self.window.destroy()
                                fourth = Fourth(root, self.idNum, self.sampleNum)
                                
#allows user to enter information about person they are adding
#name, position, representative country, and number (position on list of presidents)
#stores information in firebase database
class Second():
                entry1 = '0'
                entry2 = '0'
                entry3 = '0'
                entry4 = '0'
                name = ""
                window = 0
                idNum = 0
                
                def __init__(self, master):
                                self.window = tk.Toplevel(root)
                                self.window.title("Enter Data")
                                self.window.geometry("300x150")
                                label1 = tk.Label(self.window, text = "Name")
                                self.entry1 = tk.Entry(self.window)
                                label1.grid(row=0)
                                self.entry1.grid(row=0, column=1)

                                label2 = tk.Label(self.window, text = "Position")
                                self.entry2 = tk.Entry(self.window)
                                label2.grid(row=1)
                                self.entry2.grid(row=1, column=1)

                                label3 = tk.Label(self.window, text = "Country")
                                self.entry3 = tk.Entry(self.window)
                                label3.grid(row=2)
                                self.entry3.grid(row=2, column=1)

                                label4 = tk.Label(self.window, text = "Number")
                                self.entry4 = tk.Entry(self.window)
                                label4.grid(row=3)
                                self.entry4.grid(row=3, column=1)
                                
                                buttonNext = tk.Button(self.window, text="Next", width = 7, height=1, command = self.submitData)
                                buttonNext.grid(columnspan=2)

                def submitData(self):
                                self.name = self.entry1.get() 
                                result = firebase.get('/', None)
                                self.idNum = -5
                                playerName = "0"
                                if result:
                                                for num in range(1, len(result)):
                                                                playerAtts = firebase.get('/' + str(num), None)
                                                                playerName = playerAtts.get('Name')
                                                                if playerName == self.name:
                                                                                self.idNum = playerAtts.get('ID')
                                if self.idNum == -5:                                               
                                                if not result:
                                                                self.idNum = 1
                                                else:
                                                                self.idNum = len(result) 
                                                                              
                                result = firebase.put('/', self.idNum, {'Name': self.entry1.get(), 'Position': self.entry2.get(), 'Country': self.entry3.get(), 'ID': self.idNum, 'Number': self.entry4.get()})
                                self.changeWindow()

                def changeWindow(self):
                                self.window.destroy()
                                sampleNum = 0
                                third = Third(root, self.idNum, sampleNum)

#sets up homepage for application
#provides options to add a persons info or check a persons info
#reroutes accordingly
class Home():
                def __init__(self, master):
                        root.geometry("300x150")
                        root.title("Homepage")
                        button1 = tk.Button(root, text="Add Person", width=15, height=3, command = self.changeWindow)
                        button1.pack()
                        button2 = tk.Button(root, text="Check Info", width=15, height=4, command=self.checkInfo)
                        button2.pack()

                def changeWindow(self):
                                second = Second(root)

                def checkInfo(self):
                                faceRec = FaceRecognize(root)
                                

if __name__ == '__main__':
                root = tk.Tk()
                firebase = firebase.FirebaseApplication('https://images-40999.firebaseio.com/')
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                client = storage.Client()
                bucket = client.get_bucket('images-40999.appspot.com')
                imageBlob = bucket.blob("recognizer/")
                faceDetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                first = Home(root)
                root.mainloop()
