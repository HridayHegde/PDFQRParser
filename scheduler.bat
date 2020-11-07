SET log_file=%cd%\logfile.txt
call D:\Anaconda\Scripts\activate.bat
python Scheduler.py "D:\Projects\Python\Sample Folder" "D:\Projects\Python\OutputFolder" >> %log_file%