#Inbuilt
import os
import time
from datetime import datetime
import csv
import json
from pathlib import Path
#Custom
from CustomPackages import OCRModule as OCRM
from CustomPackages import jwtdecoding as JWTD
from CustomPackages import DatabaseInteraction as DBI


pdffolder = "./OriginFolder"
outputfolder = "./OutputFolder"
requirementsfile = "settings.json"



def DecryptQR(OriginFolder=pdffolder,OutputFolder=outputfolder):
    start_time = time.time()
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    #JSON File Opening
    settings = open(requirementsfile) 
    data = json.load(settings)

    print("--------Started Working---------")
    fileexists = os.path.isfile(OutputFolder+"/Generated"+dt_string+"_DATA.csv")
    csv_file = open(OutputFolder+"/Generated"+dt_string+"_DATA.csv",mode='a')
    
    #FieldName Updation
    fieldnames = ['PDFName']
    for y in data['qrdata']:
        if y:
            fieldnames.append(y["visualname"])


    writer = csv.DictWriter(csv_file,fieldnames)
    if not fileexists:
        writer.writeheader()
    
    
    fileset = []
    for file in os.listdir(OriginFolder):
        if file.endswith(".pdf") or file.endswith(".PDF"):
            fileset.append(os.path.join(OriginFolder, file))

    for f in fileset:
        writedata = {}
        writedata["PDFName"] = str(Path(f).stem)+".PDF"
        qrdata = OCRM.ParseOCR_QRcode(f)
        if qrdata != "":
            qrdataset = JWTD.jwtdecode(qrdata,requirementsfile,f)
            writedata.update(qrdataset)
        if writedata:
            writer.writerow(writedata)
            DBI.commitToDB(writedata)
           
    csv_file.close()
    print ("Time taken to Work on "+str(len(fileset))+" files : " + str(time.time() - start_time))
    return True

#DecryptQR()