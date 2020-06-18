import keyboard		#https://pypi.org/project/keyboard/
import time
import os
import json
import copy
import multiprocessing
from collections import namedtuple

#Functions

def ResetUserInput():
	keyboard.send('enter')
	input()

def obj_dict(obj):
    return obj.__dict__

def Record():
	print("Recording... Press [.] to stop recording.")
	recorded = keyboard.record(until='.')
	if len(recorded) > 0:
		recorded.pop()
	if len(recorded) > 0:
		recorded.pop(0)
	time.sleep(1)
	ClearConsole()
	print("Done. Don't forget to SAVE this record if you want to keep it.")
	return recorded

def LoadData():
	data = []
	if os.path.exists("bindings.json"):
		file = open("bindings.json", 'r')
		data = json.load(file, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
		file.close()
	return data
	
def ShowData(data, complex = False):
	if len(data) > 0:
		i = 1
		print("THE LIST OF SAVED BINDS:")
		for x in data:
			print("{}. quantity of saved events: {}".format(i, x if complex == True else len(x)))
			i += 1
			
def SaveData(data):
	if len(data) > 0:
		newData = []
		for x in range(0, len(data)):
			newData.append([])
			for y in range(0, len(data[x])):
				if isinstance(data[x][y], tuple):
					newData[x].append(keyboard.KeyboardEvent(data[x][y][0],data[x][y][1],data[x][y][6],data[x][y][2],data[x][y][3],data[x][y][5],data[x][y][4]))
				else:
					newData[x].append(data[x][y])
		with open("bindings.json", 'w') as file:
			json.dump(newData, file, default=obj_dict)

def SaveBind(data, objectToSave):
	data.append(objectToSave)

def RemoveBind(data, index):
	if index > 0 and index < len(data):
		del data[index]

def ClearConsole():
	os.system('cls')

def ShowOptions(bindings, recorded):
	if recorded != None:
		#Play
		print("[ , ] Play")
	#Start/Stop
	print("[ . ] Start/Stop recording")
	if recorded != None:
		#Save
		print("[ ; ] Save")
	if len(bindings) > 0:
		#Load
		print("[ ' ] Load")
		#Delete
		print("[ [ ] Delete")
	#Quit
	print("[ / ] Quit\n")
	
	ShowData(bindings)

def PlayFromProcessQueue(queue):
	keyboard.unhook_all()
	keyboard.add_hotkey(',', lambda: queue.put("stop"), args=())
	keyboard.play(queue.get(), speed_factor = 1)
	
def PlayFunc(bindings, recorded):
	if keyboard.is_pressed(',') == True and recorded != None:
		print("\nPlaying...")
		
		sharedData = multiprocessing.Queue()
		if isinstance(recorded[0], tuple):
			sharedData.put([keyboard.KeyboardEvent(x[0],x[1],x[6],x[2],x[3],x[5],x[4]) for x in recorded])
		else:
			sharedData.put(recorded)
		
		p = multiprocessing.Process(target=PlayFromProcessQueue, args=(sharedData,))
		p.start()
		time.sleep(1)
		print("Press [,] if would like stop playing recorded input...")
		while p.is_alive():
			if not sharedData.empty() and sharedData.get() == "stop":
				keyboard.unhook_all()
				p.terminate()
		p.join()
		time.sleep(1)
		
		ResetUserInput()
		
		ClearConsole()
		print("Done\n")
		ShowOptions(bindings, recorded)

def RecordingFunc(bindings, recorded):
	if keyboard.is_pressed('.') == True:
		ClearConsole()
		recorded = Record()
		ShowOptions(bindings, recorded)
		return recorded
	return None
	
def SaveFunc(bindings, recorded):
	if keyboard.is_pressed(';') == True and recorded != None:
		SaveBind(bindings, recorded)
		time.sleep(1)
		ClearConsole()
		print("Saved\n")
		ShowOptions(bindings, recorded)
		

def GetInput(type, promptMessage, defaultVal):
	result = input(promptMessage)
	try:
		result = type(result)
	except(ValueError, TypeError):
		result = defaultVal
	return result

def LoadFunc(bindings, recorded):
	if keyboard.is_pressed('\'') and len(bindings) > 0:
		ResetUserInput()
		ClearConsole()
		index = GetInput(int, "Enter number from 1 to {} and hit [Enter] to load bind:	".format(len(bindings)), -1)
		
		ClearConsole()
		
		if index >= 1 and index <= len(bindings):
			print("Done. Bind nr {} has been loaded.\n".format(index))
			recorded = bindings[index - 1]
		else:
			print("Error! Wrong value.")
			
		ShowOptions(bindings, recorded)
		return recorded
	return recorded
	
def DeleteFunc(bindings, recorded):
	if keyboard.is_pressed('[') and len(bindings) > 0:
		ResetUserInput()
		ClearConsole()
		index = GetInput(int, "Enter number from 1 to {} and hit [Enter] to delete bind:	".format(len(bindings)), -1)
		
		ClearConsole()
		
		if index >= 1 and index <= len(bindings):
			print("Done\n")
			RemoveBind(bindings, index - 1)
		else:
			print("Error! Wrong value.")
		ShowOptions(bindings, recorded)

def QuitFunc():
	if keyboard.is_pressed('/') == True:
		return True
	return False
	print("Nothing")
	
def MainFunc():
	bindings = LoadData()
	recorded = None
	end = False

	ShowOptions(bindings, recorded)
	
	while end == False:
		#Play
		PlayFunc(bindings, recorded)
		#Start/Stop
		rec = RecordingFunc(bindings, recorded)
		if rec != None:
			recorded = rec
		#Save
		SaveFunc(bindings, recorded)
		#Load
		recorded = LoadFunc(bindings, recorded)
		#Delete
		DeleteFunc(bindings, recorded)
		#Quit
		end = QuitFunc()
			
	SaveData(bindings)

#Entry point
if __name__ == '__main__':
	MainFunc()