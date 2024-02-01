import requests
from datetime import datetime
import os
import configparser

#------start globals-----------------

config_object = configparser.ConfigParser()

filelocation= os.getcwd() +'\\API_Data\\'
filepath=''
date_format_orgineel = ' %d/%m/%Y' #schijtspacie
date_format_inFile = '%d/%m/%Y'
date_format_filename = '%Y'
str_temp=''
last_date=''
HTTPS_Flag = 'True'
lastline_data=['1','2']
newfile=False

API_URL = 'https://eneco.be/Umbraco/Api/EnergySquareApi/GetFilteredHourlyPrices'

#------------------------------------

check_file =os.path.isfile('./config_api.ini')

if (check_file==False):
     with open("./config_api.ini","w") as file_object:
          config_object.add_section("database")
          config_object.set("database","url",API_URL)
          config_object.set("database","HTPPS",HTTPS_Flag)
          config_object.set("database","location_file",filelocation)
          config_object.write(file_object)
          file_object.close()
else:
    with open("./config_api.ini","r") as file_object:
         config_object.read_file(file_object)
         API_URL=config_object.get("database","url")
         filelocation=config_object.get("database","location_file")
         HTTPS_Flag=config_object.get("database","HTPPS")
         file_object.close()

 

if HTTPS_Flag=="True":
     response = requests.get(API_URL) #geen idee hoe ik het cert. deftig kan testen...

else:
     response = requests.get(API_URL, verify=False)

data = response.json() 
if os.path.exists(filelocation)==False:
     os.makedirs(filelocation)

for informatie in data:
      try:
            res = bool(datetime.strptime(informatie['Date'], date_format_orgineel)) #check of de schijtspacie er is
      except ValueError:
            res = False
      if res==True:
            date_obj = datetime.strptime(informatie['Date'], date_format_orgineel) #inladen als datum
            informatie['Date'] =datetime.strftime(date_obj,date_format_inFile) #uitschrijven als logische waarde
      date_str = informatie['Date']
      str_temp = str_temp + "\n" + str(informatie['Date']) +' '+ str(informatie['Time']) + ';' + str(informatie['Price'])
      last_date = str(informatie['Date']) + ' ' + str(informatie['Time']) #voor nadien de vergelijk te doen

filename = date_obj.strftime(date_format_filename) + '.csv'
filepath = filelocation+filename

#laatste lijn bekijken om te zien of datum al aanwezig is.
#check of file al besta
if os.path.isfile(filepath)==False:
    #file aanmaken
    with open(filepath, 'a') as csvfile:
        csvfile.write('Date Time;Price')
        csvfile.close()
        newfile=True

else:
#als file bestaat, lees laatste lijn in of de huidige datum reeds is toegevoegd.
    with open(filepath, 'rb') as csvfile:
        try:  # catch OSError in case of a one line file
            csvfile.seek(-2, os.SEEK_END)
            while csvfile.read(1) != b'\n':
                csvfile.seek(-2, os.SEEK_CUR)
        except OSError:
            csvfile.seek(0)
        last_line = csvfile.readline().decode()
        lastline_data = last_line.split(";")
        #print(lastline_data[0])#datum+tijd
        #print(last_date)
        csvfile.close()#eerste file sluiten voor we kunnen schrijven, nogal omslachtig imo.
    ##vergelijk huidige datum met laatste datum+tijd.

if((lastline_data[0]!=last_date) or (newfile==True)): #pas schrijven als de datum en tijd er nog niet in is geschreven.
    with open(filepath, 'a') as csvfile:
        csvfile.write(str_temp)
        csvfile.close()
