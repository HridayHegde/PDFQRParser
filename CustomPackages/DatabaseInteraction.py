import cx_Oracle
from CustomPackages import dbconfig1 as cfg
from datetime import datetime
import json

settingsfile = "settings.json"
def commitToDB(datadict,file):
    with open(file, 'rb') as f:
        file_as = f.read()
    pdfname = datadict["PDFName"]
    del datadict["PDFName"]
    print("----Writing To DB----")
    settings = open(settingsfile) 
    data = json.load(settings)
    visnames = []
    for x in data["qrdata"]:
        visnames.append(x["visualname"])
    for g in data["extractdata"]:
        visnames.append(g["visualname"])    

    dblist = ["PDFNAME"]
    for l in visnames:
        for x in data["qrdata"]:
            if x["visualname"] == l:
                dblist.append(x["dbname"])
        for t in data["extractdata"]:
            if t["visualname"] ==l:
                dblist.append(t["dbname"])
    
    datalist = [pdfname]
    print(visnames)
    for z in visnames:
        try:
            datalist.append(datadict[z])
        except:
            print("Input Field Error" + z)
            datalist.append("NA")


    dblist.append("CREATED_DATE")
    dblist.append("FILE_AS")
    creationdate = datetime.now()
    datalist.append(creationdate)

    dbliststring = ""
    for a in dblist:
        if dbliststring !="":
            dbliststring = dbliststring+", "+a
        else:
            dbliststring = dbliststring+a
    print("Database List String::: "+dbliststring)

    valuesliststring = ""
    for b in dblist:
        if valuesliststring !="":
            valuesliststring = valuesliststring+",:"+b.lower()
        else:
            valuesliststring = valuesliststring+":"+b.lower()
    print("Values List String::: "+valuesliststring)
    datalist.append(file_as)
    # construct an insert statement that add a new row to the billing_headers table
    #+',FILE_AS'
    #+',:file_as'
    #M_VENDOR_PDF_PARSING
    string1 = 'insert into M_VENDOR_PDF_PARSING('+dbliststring+') values('+valuesliststring+')'
    print(string1)
    for i,x in enumerate(datalist):
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        if i  < ((len(datalist))-1):
             print(x)
    sql = (string1)

    try:
        
        # establish a new connection
        with cx_Oracle.connect(cfg.username,
                            cfg.password,
                            cfg.dsn,
                            encoding=cfg.encoding) as connection:
            # create a cursor
            with connection.cursor() as cursor:

                # execute the insert statement
                cursor.execute(sql, datalist)
                # commit work
                connection.commit()
    except cx_Oracle.Error as error:
        print('Error occurred:')
        print(error)


