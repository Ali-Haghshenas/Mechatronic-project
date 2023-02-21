from skimage.metrics import structural_similarity as ssim
import imutils
import cv2
from PIL import Image
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import ctypes
from pathlib import Path
import os
import numpy as np

source_path = Path(__file__).resolve().parent
global img1_gray
global img2_gray


root = Tk()

root.title("The Mechatronic1 project")
root.iconphoto(True, PhotoImage(file= str(source_path) + '\\microscope-icon.png'))

frame = tk.Frame(root, bg='#45aaf2')

first_label = tk.Label(frame, text='Please select TWO pictures to compare:', padx=25, pady=25, font=('verdana',16), bg='#45aaf2')

# Pic 1:
lbl_pic1_path = tk.Label(frame, text='Image1(referenced image) Path:', padx=25, pady=25,
                        font=('verdana',10), bg='#45aaf2')
lbl_show_pic1 = tk.Label(frame, bg='#45aaf2')
entry_pic1_path = tk.Entry(frame, font=('verdana',10))
btn_browse1 = tk.Button(frame, text='Select Image 1 (referenced image)', bg='grey', fg='#ffffff',
                       font=('verdana',10))

# Pic 2:
lbl_pic2_path = tk.Label(frame, text='Image2(microscopic image) Path:', padx=25, pady=25,
                        font=('verdana',10), bg='#45aaf2')
lbl_show_pic2 = tk.Label(frame, bg='#45aaf2')
entry_pic2_path = tk.Entry(frame, font=('verdana',10))
btn_browse2 = tk.Button(frame, text='Select Image 2 (microscopic image)', bg='grey', fg='#ffffff',
                       font=('verdana',10))

btn_comp = tk.Button(frame, text='Send to compare', bg='gray', fg='#ffffff', font=('verdana',10))
tk.Label(root, text="Designed by : ALI HAGHSHENAS with the cooperation of Mr. MOHAMMAD REZA GHANE, as the project of Mecahtronics I courses", font=('verdana',8)).pack()

def selectPic1():
    global img1
    filename1 = filedialog.askopenfilename(initialdir="/images", title="Please Select First Image",
                           filetypes=(("png images","*.png"),("jpg images","*.jpg")))
    img1 = Image.open(filename1)
    img1 = img1.resize((200,200), Image.LANCZOS)
    img1 = ImageTk.PhotoImage(img1)
    lbl_show_pic1['image'] = img1
    entry_pic1_path.delete(0, END)
    entry_pic1_path.insert(0, filename1)
    
def selectPic2():
    global img2
    filename2 = filedialog.askopenfilename(initialdir="/images", title="Please Select Second Image",
                           filetypes=(("png images","*.png"),("jpg images","*.jpg")))
    img2 = Image.open(filename2)
    img2 = img2.resize((200,200), Image.LANCZOS)
    img2 = ImageTk.PhotoImage(img2)
    lbl_show_pic2['image'] = img2
    entry_pic2_path.delete(0, END)
    entry_pic2_path.insert(0, filename2)

def send():
    
    if((entry_pic1_path.get()=="")|(entry_pic2_path.get()=="")):
        ctypes.windll.user32.MessageBoxW(None, u"Image 1 or image 2 is not selected.", u"Error", 0x00000010)
    else:
        ctypes.windll.user32.MessageBoxW(None, u"For comparing, two images are converted to size : 400x400 pixcels", u"Note", 0x00000040)
        if (os.path.exists(str(source_path) + '\\files') == False):
            os.mkdir(str(source_path) + '\\files')
        elif (os.path.exists(str(source_path) + '\\files\\inputs') == False):
            os.mkdir(str(source_path) + '\\files\\inputs')
        elif (os.path.exists(str(source_path) + '\\files\\outputs') == False):
            os.mkdir(str(source_path) + '\\files\\outputs')
        elif (os.path.exists(str(source_path) + '\\files\\outputs\\results') == False):
            os.mkdir(str(source_path) + '\\files\\outputs\\results')
        img1 = Image.open(entry_pic1_path.get())
        img1 = img1.resize((400,400), Image.LANCZOS)
        img1.save(str(source_path) + '\\files\inputs\\0.png')
        img2 = Image.open(entry_pic2_path.get())
        img2 = img2.resize((400,400), Image.LANCZOS)
        img2.save(str(source_path) + '\\files\inputs\\1.png')
        
        #compare_images(img1, img2):
        # Loading the images and comparing them:
        img1 = np.array(img1)
        img2 = np.array(img2)
        
        # Convert images to grayscale
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(str(source_path) + '\\files\outputs\\0.png', img1_gray)
        cv2.imwrite(str(source_path) + '\\files\outputs\\1.png', img2_gray)
        
        # Compute SSIM between the two images
        (score, diff) = ssim(img1_gray, img2_gray, full=True)
        print("Image Similarity: {:.4f}%".format(score * 100))
        
        # The diff image contains the actual image differences between the two images
        # and is represented as a floating point data type in the range [0,1] 
        # so we must convert the array to 8-bit unsigned integers in the range
        # [0,255] before we can use it with OpenCV
        diff = (diff * 255).astype("uint8")
        diff_box = cv2.merge([diff, diff, diff])
        
        # Threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        
        mask = np.zeros(img1.shape, dtype='uint8')
        filled_after = img1.copy()

        for c in contours:
            area = cv2.contourArea(c)
            if area > 40:
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(img1, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.rectangle(img2, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.drawContours(mask, [c], 0, (255,255,255), -1)
                cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)

        #cv2.imshow('before', img1)
        #cv2.imshow('after', img2)
        #cv2.imshow('diff', diff)
        #cv2.imshow('diff_box', diff_box)
        #cv2.imshow('mask', mask)
        #cv2.imshow('filled after', filled_after)
        #cv2.waitKey()
        cv2.imwrite(str(source_path) + '\\files\outputs\\results\\0(difference).png', img1)
        cv2.imwrite(str(source_path) + '\\files\outputs\\results\\1(difference).png', img2)
        #cv2.imwrite(str(source_path) + '\\files\outputs\\results\\diff.png', diff)
        #cv2.imwrite(str(source_path) + '\\files\outputs\\results\\diff_box.png', diff_box)
        #cv2.imwrite(str(source_path) + '\\files\outputs\\results\\mask.png', mask)
        cv2.imwrite(str(source_path) + '\\files\outputs\\results\\filled_after.png', filled_after)
        
        # Page2 configuration :
        page2 = tk.Toplevel()
        #page2.geometry("750x500")
        page2['bg']="#ffffff"
        page2.title("Results")
        tk.Label(page2, text="Result:", padx=25, pady=25, font=('verdana',16), bg='#ffffff').grid(row=0, column=0, columnspan=3, sticky=W)
        tk.Label(page2, text="Similarity between two images: {:.4f}%".format(score * 100), padx=25, pady=25, font=('verdana',10), bg='#ffffff').grid(row=1, column=0, columnspan=3)       
        img1 = PhotoImage(file = str(source_path) + '\\files\outputs\\results\\0(difference).png')
        tk.Label(page2, bg='#00FF00', bd=0, width=400, height=400, image=img1).grid(row=2, column=0, ipadx=0, ipady=0)
        tk.Label(page2, text="Referenced picture \n place of what doesn't exist in this picture, showed", font=('verdana',10), pady=10).grid(row=3, column=0)
        img2 = PhotoImage(file = str(source_path) + '\\files\outputs\\results\\1(difference).png')
        tk.Label(page2, bg='#00FF00', bd=0, width=400, height=400, image=img2).grid(row=2, column=1, ipadx=0, ipady=0)
        tk.Label(page2, text="Microscopic picture \n the difference is demonstrated with the rectangular border", font=('verdana',10), pady=10).grid(row=3, column=1)
        filled_after = PhotoImage(file = str(source_path) + '\\files\outputs\\results\\filled_after.png')
        tk.Label(page2, bg='#00FF00', bd=0, width=400, height=400, image=filled_after).grid(row=2, column=2, ipadx=0, ipady=0)
        tk.Label(page2, text="Filled-difference picture \n the difference is filled by lime color", font=('verdana',10), pady=10).grid(row=3, column=2)
        #show_res1 = tk.Label(page2, bg='#ffffff')
        #img1 = Image.open(img1)
        #img1 = ImageTk.PhotoImage(img1)
        #show_res1['image'] = img1
        #cv2.imshow('show_pic1', img1_gray)
        #cv2.imshow('show_pic2', img2_gray)
        
        #show_gray_pic1 = tk.Label(page2)
        #gray_pic1 = ImageTk.PhotoImage(img1_gray)
        #show_gray_pic1['image'] = gray_pic1
        #show_gray_pic2 = tk.Label(page2)
        #gray_pic2 = ImageTk.PhotoImage(img2_gray)
        #show_gray_pic2['image'] = gray_pic2
        
        #show_gray_pic1.grid(row=1, column=0)
        #show_gray_pic2.grid(row=1, column=5)
        page2.mainloop()
        

btn_browse1['command'] = selectPic1

btn_browse2['command'] = selectPic2

btn_comp['command'] = send

frame.pack()

first_label.grid(row=0, column=0, columnspan=2)

lbl_pic1_path.grid(row=1, column=0)
entry_pic1_path.grid(row=1, column=1, padx=(0,20))
lbl_show_pic1.grid(row=2, column=0, columnspan="2")
btn_browse1.grid(row=3, column=0, columnspan="2", padx=10, pady=10)

lbl_pic2_path.grid(row=1, column=8)
entry_pic2_path.grid(row=1, column=10, padx=(0,20))
lbl_show_pic2.grid(row=2, column=8, columnspan="2")
btn_browse2.grid(row=3, column=8, columnspan="2", padx=20, pady=20)

btn_comp.grid(row=4, column=6, pady=20)

root.mainloop()