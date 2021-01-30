import pytesseract

import os
import shutil
from pathlib import Path
import numpy as np

import re

import csv
import json
#import zxing

import fitz
import pdf2image
from PIL import Image
import time
from copy import deepcopy


import cv2

import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import ZBarSymbol

from unidecode import unidecode

from CustomPackages import DatabaseInteraction as DI
#IMAGE GENERATION VARIABLES
DPI = 600
OUTPUT_FOLDER = None
FIRST_PAGE = None
LAST_PAGE = None
FORMAT = 'jpg'
THREAD_COUNT = 1
USERPWD = None
USE_CROPBOX = False
STRICT = False




#FileSpecificlocation = "./ConvertedInvoices/"

def setfile(sessionid):
    FileSpecificlocation = "./ConvertedInvoices/"+sessionid+"/"
    try:
        shutil.rmtree(FileSpecificlocation)
    except OSError as e:
        print(e)
    try:
        os.mkdir(FileSpecificlocation)
    except OSError as e:
        print(e)
def save_images(pil_images,destination):

    x = destination+'temp/images/'
    try:
        print("MakingDIR")
        os.mkdir(destination+'temp/images')
    except OSError as e:
        print("OCRTEMPLATE:::::"+str(e))
    #This method helps in converting the images in PIL Image file format to the required image format
    index = 1
    for image in pil_images:
        image.save(x+"page_" + str(index) + ".jpg")
        index += 1
    return index

def GenerateImagesfromPDF(filepath,destination):
    
    start_time = time.time()
    pil_images = pdf2image.convert_from_path(filepath, dpi=DPI, output_folder=OUTPUT_FOLDER, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT,poppler_path='./poppler/bin')
    
    print ("Time taken : " + str(time.time() - start_time))
    index = save_images(pil_images,destination)
    return index
    


def GenerateOCR(filepath,sessionid):
    destinationpath = "./ConvertedInvoices/"+sessionid+"/"+Path(filepath).stem+'/'
    print("......Generating OCR.....")
    index = GenerateImagesfromPDF(filepath,destinationpath)
    text = ""
    for x in range(1,index):
        text += "\n" + pytesseract.image_to_string(Image.open(destinationpath+'temp/images/page_'+str(x)+'.jpg'),lang='eng',config="--psm 6")
    with open(destinationpath+'temp/'+"pytesseractextract.txt","w+") as x:
        text = unidecode(text)
        x.write(text)
    return text


def ParseOCR_QRcode(file,sessionid):
    FileSpecificlocation = "./ConvertedInvoices/"+sessionid+"/"
    setfile(sessionid)
    try:
        print("MakingDIR")
        os.mkdir(FileSpecificlocation+Path(file).stem)
    except OSError as e:
        print("OCRTEMPLATE:::::"+str(e))
    try:
        print("MakingDIR")
        os.mkdir(FileSpecificlocation+Path(file).stem+'/temp/')
    except OSError as e:
        print("OCRTEMPLATE:::::"+str(e))    
    try:
        print("MakingDIR")
        os.mkdir(FileSpecificlocation+Path(file).stem+'/temp/images')
    except OSError as e:
        print("OCRTEMPLATE:::::"+str(e))

    temploc = FileSpecificlocation+Path(file).stem+"/temp/images/"
    print(".....Parsing OCR QR data......")
    barcode_data = ""
    barcodeexists = False
    try:
        os.mkdir(temploc)
    except OSError as e:
        print(e)
    try:
        os.mkdir(temploc+'qrimages')
    except OSError as e:
        print(e)

    start_time = time.time()
    pil_images = pdf2image.convert_from_path(file, dpi=DPI, output_folder=OUTPUT_FOLDER, first_page=FIRST_PAGE, last_page=LAST_PAGE, fmt=FORMAT, thread_count=THREAD_COUNT, userpw=USERPWD, use_cropbox=USE_CROPBOX, strict=STRICT,poppler_path='./poppler/bin')
    print ("Time taken : " + str(time.time() - start_time))

    index = 1
    for image in pil_images:
        image.save(temploc+"qrimages/page_" + str(index) + ".jpg")
        index += 1
    for filename in os.listdir(temploc+"qrimages/"):
        image1 = cv2.imread(os.path.join(temploc+"qrimages/",filename))
        decodedobjects = pyzbar.decode(image1,symbols=[ZBarSymbol.QRCODE])
        if decodedobjects:
            print("YES")
            barcode_data = decodedobjects[0].data
            barcodeexists = True
            print(":::::::::::::::::::::::::::BARECODE DATA :::::::::::::::::::::::::::")
            print(barcode_data)
            print(":::::::::::::::::::::::::::BARECODE DATA END:::::::::::::::::::::::::::")
	
	#for i in range(1,index):
    #    reader = zxing.BarCodeReader()
    #    if os.path.isfile(temploc+"qrimages/page_" + str(index) + ".jpg"):
    #        image1 = cv2.imread(emploc+"qrimages/page_" + str(index) + ".jpg")
            
                
            #barcode = reader.decode(temploc+"qrimages/page_" + str(index) + ".jpg")
            #if barcode:
            #    barcodeexists = True
            #    barcode_data = barcode.raw
    
    if barcodeexists:
        return barcode_data
    else:
        return ""
