import re 
import bs4
import platform
import subprocess
import pymailcheck
import os, os.path
import pandas as pd 
from screen import Screen
from menu_formatter import MenuFormatBuilder

FileName=''
Status="Main"
datalist=None
SubMenuList = []
if platform.system() == 'Windows':
	if not os.path.exists('C:/ContactousInputFiles'):
		os.makedirs('C:/ContactousInputFiles')
		os.makedirs('C:/ContactousOutputFiles')
	InputPath="C:/ContactousInputFiles"
	OutputPath="C:/ContactousOutputFiles/"
else:
	if not os.path.exists('/var/www/html/ContactousInputFiles'):
		os.makedirs('/var/www/html/ContactousInputFiles')
		os.makedirs('/var/www/html/ContactousOutputFiles')
	InputPath="/var/www/html/ContactousInputFiles"
	OutputPath="/var/www/html/ContactousOutputFiles/"
MainMenuList = ['1) Read Directory Files', '2) Menu 2', '3) Menu 3', '4) Exit']
ActionMenuList=['1) Check Email','2) Data Duplication','3) Data Cleaning','4) Return to previous menu','5) Return to main menu']

# Draw the menus
def draw(Lists):
	MainMenu="*********************************************************************"
	if Status=="Main":
		MainMenu="***************************<<MAIN MENU>>*****************************"
	formatter = MenuFormatBuilder()
	screen = Screen()
	screen.printf(formatter.format(title="CONTACT TO US",subtitle="Please Select Any Of Them To Perform Task",items=Lists,
		prologue_text=MainMenu,epilogue_text="*********************************************************************"))

# Ends the program
def Quit():
  	print('Please come again')
  	quit()

# clear the Screen
def clear():
	if platform.system() == 'Windows':
		subprocess.check_call('cls', shell=True)
	else:
		print(subprocess.check_output('clear').decode())


# Creates the selection logic for the main menu
def doOperation(selection):
	global Status
	if selection == '1':
		clear()
		SubMenuList.clear()
		i=0
		for r, d, files in os.walk(InputPath):   #/New folder
			if i==0:
				count=len(files)
				if count > 0:
					files.append('Return to main menu')
					for file in files:
						SubMenuList.append(str(files.index(file)+1) + ") " + file)
					Status="Sub"
					draw(SubMenuList)
					i=i+1
				else:
					draw(MainMenuList)
					if platform.system() == 'Windows':
						print("Don't Have any file kindly add some files on 'C:/ContactousInputFiles'")
					else:
						print("Don't Have any file kindly add some files on '/var/www/html/ContactousInputFiles'")
	elif selection == '2':
		clear()
		draw(MainMenuList)
		print("To be continued...")
	elif selection == '3':
		clear()
		draw(MainMenuList)
		print("To be continued...")
	elif selection == '4':
		clear()
		Quit()
	else:
		clear()
		draw(MainMenuList)
		print('Please choose 1, 2, 3 or 4 next time')


# Creates the selection logic for the sub menu
def doSubOperation(selection,lists):
	global Status
	global datalist
	global FileName
	count=len(lists)
	for data in lists:
		if selection >= '1' and selection <= str(count-1):
			clear()
			Status="Action"
			datalist = pd.read_csv(InputPath+'/'+ str(lists[int(selection)-1])[3:])
			FileName = str(lists[int(selection)-1])[3:]
			draw(ActionMenuList) 
			break
		elif selection == str(count):
			clear()
			Status="Main"
			draw(MainMenuList)
			break
		else:
			clear()
			draw(SubMenuList)
			s=''
			for d in lists:
				if lists.index(d)+1 < count-1:
					s += str(lists.index(d)+1) + ", "
				elif lists.index(d)+1 == count-1:
					s += str(lists.index(d)+1)
				elif lists.index(d)+1 == count:
					s += ' or ' + str(lists.index(d)+1)
			print('Please choose ' + s + ' next time')
			break	

# Creates the selection logic for the Action menu
def doActionOperation(selection):
	global Status
	global datalist
	global FileName
	if selection == '1':
		clear()
		draw(ActionMenuList)
		CheckEmailDataList=datalist
		for i, row in CheckEmailDataList[['Email']].iterrows():
			if checkemail(CheckEmailDataList.at[i,'Email'])==True:
				if pymailcheck.suggest(CheckEmailDataList.at[i,'Email'])!=False:
					CheckEmailDataList.at[i,'Email'] = pymailcheck.suggest(CheckEmailDataList.at[i,'Email'])["full"]
		CheckEmailDataList.to_csv(OutputPath+"CheckEmail_"+FileName, index=False)
		print("CheckEmail_"+FileName+" is Created Sucessfully.")
	elif selection == '2':
		clear()
		draw(ActionMenuList)
		DeDuplicationDataList=datalist
		ColumnNameList=[]
		i=1
		for col in DeDuplicationDataList.columns:
			ColumnNameList.append(str(i) + ") "+col) 
			i+=1
		clear()
		draw(ColumnNameList)
		print("Enter Comma-Seperated Column Index to Clear Duplication")
		while True:
			res = input('Your choice Comma-Seperated : ')
			if len(res) == 1 and res.isnumeric() and int(res) >= 1 and int(res) <= len(ColumnNameList):
				break
			if res.isnumeric() and int(res) >= 1 and int(res) <= len(ColumnNameList):
				break
			elif len(res) >1 and ',' in res:
				temp=res.split(",")
				s=True
				for t in temp:
					if not t.isnumeric():
						s=False
					if t.isnumeric():
						if int(t) < 1 or int(t) > len(ColumnNameList):
							s=False
				if s:
					break
				else:
					clear()
					draw(ColumnNameList)
					print("Enter a valid Choice With Comma-Seperated : ")
			else:
				clear()
				draw(ColumnNameList)
				print("Enter a valid Choice With Comma-Seperated : ")
		ListOfColumn = list(dict.fromkeys(res.split(",")))
		mylist=[]
		for l in ListOfColumn:
			if int(l)+1>=10:
				mylist.append(str(ColumnNameList[int(l)-1])[4:])
			else:
				mylist.append(str(ColumnNameList[int(l)-1])[3:])
		
		clear()
		draw(ActionMenuList)
		# print(DeDuplicationDataList.drop_duplicates(subset=mylist, keep='first', inplace = False))
		DeDuplicationDataList=DeDuplicationDataList.drop_duplicates(subset=mylist)
		DeDuplicationDataList.to_csv(OutputPath+"DeDuplication_"+FileName, index=False)
		print("DeDuplication_"+FileName+" is Created Sucessfully.")
	elif selection == '3':
		clear()
		draw(ActionMenuList)
		DataCleaningDataList=datalist
		# print(DataCleaningDataList.head())
		i=0
		for col in DataCleaningDataList.columns:
			i+=1
			clear()
			draw(ActionMenuList)
			print('\r\n'+'Cleaning...  process '+'{:.2f}'.format(i/len(DataCleaningDataList.columns)*100)+'%')
			DataCleaningDataList[str(col)].fillna("", inplace = True)
			DataCleaningDataList[str(col)] = DataCleaningDataList[str(col)].astype(str)
			DataCleaningDataList[str(col)] = DataCleaningDataList[str(col)].apply(lambda x: bs4.BeautifulSoup(x, 'lxml').get_text())
		DataCleaningDataList.to_csv(OutputPath+"DataCleaning_"+FileName, index=False)
		clear()
		draw(ActionMenuList)
		print("DataCleaning_"+FileName+" is Created Sucessfully.")
	elif selection == '4':
		clear()
		Status="Sub"
		draw(SubMenuList)
	elif selection == '5':
		clear()
		Status="Main"
		draw(MainMenuList)
	else:
		clear()
		draw(ActionMenuList)
		print('Please choose 1, 2, 3, 4 or 5 next time')
    
# Define a function for 
# for validating an Email 
def checkemail(email):
	regex = r"[A-Za-z0-9-_]+(.[A-Za-z0-9-_]+)*@[A-Za-z0-9-]+(.[A-Za-z0-9]+)*(.[A-Za-z]{2,})"  
	if re.match(regex,str(email),re.IGNORECASE):
		return True
	else:
		return False

clear()
draw(MainMenuList)

# Loop that continues the doOperation() function until quit()
while True:
	response = input('Your choice : ')
	if Status=="Main":
		doOperation(response.upper())
	elif Status=="Sub":
		doSubOperation(response.upper(),SubMenuList)
	elif Status=="Action":
		doActionOperation(response.upper())
	