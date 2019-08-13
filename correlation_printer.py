import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import statistics
from matplotlib.widgets import Slider

#________________Class___________________
#________________EndClass___________________
#________________Function___________________
def creatThePointsGraph(annotation_file):
	counterPickingUpAction = np.zeros(len(annotation_file))
	counterReceivingAction =  np.zeros(len(annotation_file))
	counterOrderingAction =  np.zeros(len(annotation_file))
	counterPayingAction =  np.zeros(len(annotation_file))

	counterArmROverTheDesk =  np.zeros(len(annotation_file))
	counterArmLOverTheDesk =  np.zeros(len(annotation_file))
	counterArmOverTheDesk =  np.zeros(len(annotation_file))

	frameCount = 0
	for frame in annotation_file:	 #pour chaque frame
		current_frame = annotation_file[frame]['annotations'] #l'image actuelle
		for anno in range(len(current_frame)): #pour chaque annotation dans la frame actuelle
			current_annotations = current_frame[anno] #annotation actuelle
			if('arm_over_the_desk' in current_annotations): #si il existe le champ arm_over_the_desk
				if(current_annotations['arm_over_the_desk']['arm_left']): #si le bras gauche est au dessus
					counterArmLOverTheDesk[frameCount] = 1 #on met un 1 au num de la frame en cours du bras gauche
					counterArmOverTheDesk[frameCount] = 1 #on met un 1 au num de la frame en cours du bras
				if(current_annotations['arm_over_the_desk']['arm_right']):#pareil à droite
					counterArmROverTheDesk[frameCount] = 1
					counterArmOverTheDesk[frameCount] = 1
				
			if(current_annotations['category'] == "ordering"):#si la catégorie est ordering
				counterOrderingAction[frameCount] = 1.5

			if(current_annotations['category'] == "paying"):
				counterPayingAction[frameCount] = 1.5

			if(current_annotations['category'] == "receiving"):
				counterReceivingAction[frameCount] = 1.5

			if(current_annotations['category'] == "picking_up"):
				counterPickingUpAction[frameCount] = 1.5

		frameCount += 1
	return {"frameCount":frameCount,"counterArmROverTheDesk":counterArmROverTheDesk,"counterArmLOverTheDesk":counterArmLOverTheDesk,"counterOrderingAction":counterOrderingAction,"counterPayingAction":counterPayingAction,"counterReceivingAction":counterReceivingAction,"counterPickingUpAction":counterPickingUpAction}

def changeYourDict(yourDict,yourField,yourNum):
	if (yourNum == None):
		yourDict[yourField] = yourDict[yourField]+1
	else:
		yourDict[yourField] = yourNum
	return yourDict

def creatStatistics(annotation_file,details):
	DetectedActions = {"DetectedOrdering": 0,"DetectedPaying": 0,"DetectedReceiving": 0,"DetectedPicking_up": 0}
	categoryCounter = {"counter_ord":0,"counter_pay":0,"counter_pic":0,"counter_rec":0}
	for action in details["category"]: #pour chaque action on prend start frame et end frame
		startFrame = action["start_frame"]
		end_frame = action["end_frame"]
		category = action["category"]
		# A chaque action nous comptons cette action dans le dict correspondant
		if(category =='ordering'):
			myfield = "counter_ord"
		if(category =='paying'):
			myfield = "counter_pay"
		if(category =='picking_up'):
			myfield = "counter_pic"
		if(category =='receiving'):
			myfield = "counter_rec"
		categoryCounter=changeYourDict(categoryCounter,myfield,None)
		false_positive = 0
		false_negative = 0
		true_negative = 0
		indicator = False
		#Pour chaque action nous parcourons le jsonFile d'annotations pour savoir si l'action a été détectée
		for i in range(startFrame,end_frame+1):#pour les frames allant de start a end de l'action
			for anno in annotation_file[frame_NumberToName(annotation_file,i)]['annotations']:#pour les annotations de la frame
				if ('arm_over_the_desk' in anno):#si le champ est existant
					#Si la categorie est ordering et qu'un bras est au dessus du comptoir alors +1 au compteur de detection
					if(anno["category"] == category and (anno["arm_over_the_desk"]["arm_left"] == True or anno["arm_over_the_desk"]["arm_right"] == True)):
						indicator = True
		if(category == "ordering" and indicator == True):
			DetectedActions["DetectedOrdering"]+=1
		if(category == "paying" and indicator == True):
			DetectedActions["DetectedPaying"]+=1
		if(category == "receiving" and indicator == True):
			DetectedActions["DetectedReceiving"]+=1
		if(category == "picking_up" and indicator == True):
			DetectedActions["DetectedPicking_up"]+=1
	for frame in annotation_file:
		for annotation in annotation_file[frame]["annotations"]:
			if ('arm_over_the_desk' in annotation):
				if(annotation["category"] == "" and (annotation["arm_over_the_desk"]["arm_left"] == True or annotation["arm_over_the_desk"]["arm_right"] == True)):
					false_positive += 1
				if(annotation["category"] == "" and (annotation["arm_over_the_desk"]["arm_left"] == False and annotation["arm_over_the_desk"]["arm_right"] == False)):
					true_negative += 1
				if(annotation["category"] != "" and (annotation["arm_over_the_desk"]["arm_left"] == False and annotation["arm_over_the_desk"]["arm_right"] == False)):
					false_negative += 1
	return {"num_actions":categoryCounter,"TruePositive":DetectedActions,"FalsePositive":false_positive,"true_negative":true_negative,"FalseNegative":false_negative,"percentTruePositive":percentageTP(categoryCounter,DetectedActions)}

def printStat(data):
	print("There is",data["FalsePositive"],"of false positive. (Detected Action but no action)")
	print("There is",data["FalseNegative"],"of false negative. (Undetected Action but action)")
	print("There is",data["true_negative"],"of true_negative. ")
	print("There is",data["TruePositive"]["DetectedOrdering"],"/",data["num_actions"]["counter_ord"],"of detected ordering. ")
	print("There is",data["TruePositive"]["DetectedPaying"],"/",data["num_actions"]["counter_pay"],"of detected paying. ")
	print("There is",data["TruePositive"]["DetectedReceiving"],"/",data["num_actions"]["counter_rec"],"of detected receiving. ")
	print("There is",data["TruePositive"]["DetectedPicking_up"],"/",data["num_actions"]["counter_pic"],"of detected picking_up. ")
	print("Conclusion :\n",data["percentTruePositive"]["ordering_percent"],"%","of ordering action are detected.")
	print(data["percentTruePositive"]["paying_percent"],"%","of paying action are detected.")
	print(data["percentTruePositive"]["receiving_percent"],"%","of receiving action are detected.")
	print(data["percentTruePositive"]["picking_up_percent"],"%","of picking_up action are detected.")

def percentageTP(categoryCounter,DetectedActions):
	if(categoryCounter["counter_ord"] != 0):
		ordering_percent = DetectedActions["DetectedOrdering"]/categoryCounter["counter_ord"]*100
	else :
		ordering_percent = None
	if(categoryCounter["counter_pay"] != 0):
		paying_percent = DetectedActions["DetectedPaying"]/categoryCounter["counter_pay"]*100
	else :
		paying_percent = None
	if(categoryCounter["counter_rec"] != 0):
		receiving_percent = DetectedActions["DetectedReceiving"]/categoryCounter["counter_rec"]*100
	else :
		receiving_percent = None
	if(categoryCounter["counter_pic"] != 0):
		picking_up_percent = DetectedActions["DetectedPicking_up"]/categoryCounter["counter_pic"]*100
	else :
		picking_up_percent = None
	return {"ordering_percent":ordering_percent,"paying_percent":paying_percent,"receiving_percent":receiving_percent,"picking_up_percent":picking_up_percent}

def frame_NumberToName(annotation_file,numFrame):
	if(type(numFrame)==int):
		frame_counter = 0
		frameName = "unknown"
		for frame in annotation_file:
			frame_counter+=1
			if (frame_counter == numFrame):
				frameName = frame
		return frameName
	else:
		print("Wrong type in frame_NumberToName function!")

def frame_NameToNumber(annotation_file,NameFrame):
	if(type(NameFrame)==str):
		frame_counter = 0
		numFrame = 0
		for frame in annotation_file:
			frame_counter+=1
			if (frame == NameFrame):
				numFrame = frame_counter
		return numFrame
	else:
		print("Wrong type in frame_NameToNumber function!")



#________________EndFunction___________________

parser = argparse.ArgumentParser()
parser.add_argument('category')
args = parser.parse_args()

annotation_file = json.load(open("AnnotationWithArmsOverTheDesk.json", 'r'))
details = json.load(open("detail.json", 'r'))

frameCount = creatThePointsGraph(annotation_file)["frameCount"]

df=pd.DataFrame({'x':range(0,frameCount),'RArm': creatThePointsGraph(annotation_file)["counterArmROverTheDesk"], 'LArm': creatThePointsGraph(annotation_file)["counterArmLOverTheDesk"], 'ordering': creatThePointsGraph(annotation_file)["counterOrderingAction"], 'paying': creatThePointsGraph(annotation_file)["counterPayingAction"], 'receiving': creatThePointsGraph(annotation_file)["counterReceivingAction"], 'picking_up': creatThePointsGraph(annotation_file)["counterPickingUpAction"] })


fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)

if args.category == 'ordering':
	plt.plot( 'x', 'ordering', data=df, marker='', color='gold', linewidth=2,label="ordering")
elif args.category == 'paying':
	plt.plot( 'x', 'paying', data=df, marker='', color='gold', linewidth=2,label="paying")
elif args.category == 'receiving':
	plt.plot( 'x', 'receiving', data=df, marker='', color='gold', linewidth=2,label="receiving")
elif args.category == 'picking_up':
	plt.plot( 'x', 'picking_up', data=df, marker='', color='gold', linewidth=2,label="picking_up")

plt.plot( 'x', 'RArm', data=df, marker='', color='red', linewidth=2,label="arm right")
plt.plot( 'x', 'LArm', data=df, marker='', color='blue', linewidth=2,label="arm left")
axpos = plt.axes([0.2, 0.1, 0.65, 0.03])

spos = Slider(axpos, 'Pos', 0.1, frameCount-1000)

def update(val):
  pos = spos.val
  ax.axis([pos,pos+1000,0,1.5])
  fig.canvas.draw_idle()

spos.on_changed(update)

plt.legend()
plt.show()
printStat(creatStatistics(annotation_file,details))