#Inbuilt
import os
import time
from datetime import datetime
import csv
import json
from pathlib import Path
import re
#Custom
from CustomPackages import OCRModule as OCRM
from CustomPackages import jwtdecoding as JWTD
from CustomPackages import DatabaseInteraction as DBI


pdffolder = "./OriginFolder"
outputfolder = "./OutputFolder"
requirementsfile = "settings.json"

def ParseLines(file):
    print(":::::::::::::::::Extracting Field::::::::::::::")
    tempdict = {}
    rf = open(requirementsfile)
    data = json.load(rf)
    for x in data['extractdata']:
        text = OCRM.GenerateOCR(file)
        print(text)
        regexp = x['regexexp'] + x['dataregex']
        try:
            regdata = re.search(regexp,text,re.MULTILINE)
        except:
            print("No such field in text") 
        print(regdata)
        try:
            actualdata = re.search(x['dataregex'],regdata.group(0))
            finaldata = actualdata.group(0)
        except:
            finaldata = ""
        tempdict[x['visualname']] = finaldata
    return tempdict    




def DecryptQR(OriginFolder=pdffolder,OutputFolder=outputfolder):
    start_time = time.time()
    

    now = datetime.now()

    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    print(":::::::::::::::::::::::::::::::::: Process Initiated at "+str(dt_string)+" ::::::::::::::::::::::::::::::::::")

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
    for z in data['extractdata']:
        if z:
            fieldnames.append(z["visualname"])

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
        
        extracteddata = ParseLines(f)
        if extracteddata:
            print("Extracted Data :::::::::::: ")
            print(extracteddata)
            writedata.update(extracteddata)
        if writedata:
            writer.writerow(writedata)
            DBI.commitToDB(writedata,f)

    
        

    for f in fileset:
        try:
            os.remove(f)
        except:
            print("Cannot Remove File")

    csv_file.close()
    print ("Time taken to Work on "+str(len(fileset))+" files : " + str(time.time() - start_time))
    nowend = datetime.now()
    dt_stringend = now.strftime("%d-%m-%Y_%H-%M-%S")
    print(":::::::::::::::::::::::::::::::::: Process Ended at "+str(dt_stringend)+" ::::::::::::::::::::::::::::::::::")
    return True

#DecryptQR()