import sys
import MainHandler

inputfolder = sys.argv[1]
outputfolder = sys.argv[2]

print(inputfolder)
print(outputfolder)

MainHandler.DecryptQR(inputfolder,outputfolder)