import os
import numpy
from matplotlib import pyplot as plt

fileName = "mmn_queue.py"
fileNamePriority = "mmn_queue_priority.py"
lambdas = [0.5, 0.9, 0.95, 0.99]
choices = [1, 2, 5, 10]
    

class MisurationLamba:
    def __init__(self,lambaData,misurations):
        super().__init__()
        self.lambaData = lambaData
        self.misurations = misurations

    def normalizeMesures(self):
        listOfIndex = [] 
        for i in range(1, 15):
            listOfIndex.append(i) 
        misurationsAdded = []
        for misureByReference in listOfIndex:
            misurationsAdded.append(sum((x >= misureByReference) for x in self.misurations))
            misurationsNormalized = [(float(k)/max(misurationsAdded))*self.lambaData for k in misurationsAdded]
                
        print("Dati normalizzati:",misurationsNormalized)
        return misurationsNormalized

class MisurationGraphics:
    def __init__(self,choice):
       super().__init__()
       self.choice = choice
       self.misurations=[]

def creazioneCsv():
    for i in choices:
        for j in lambdas:
            os.system(f"python {fileName} --lambd {j} --max-t 1000 --d {i} --createCsv mesuresQueue/{i}_{j}.csv")
            # os.system(f"python {fileNamePriority} --lambd {j} --max-t 1000 --d {i} --createCsv mesuresQueuePriority/{i}_{j}.csv")

def getListPlot():
    listOfChoices = []
    for i, choice in enumerate(choices):
        graphic =  MisurationGraphics(choice)
        for j, lanbda in enumerate(lambdas):
            ms = numpy.loadtxt(f"mesuresQueue/{choice}_{lanbda}.csv", delimiter=',')
            # ms = numpy.loadtxt(f"mesuresQueuePriority/{choice}_{lanbda}.csv", delimiter=',')
            misure = MisurationLamba(lanbda,ms)
            graphic.misurations.append(misure)
        listOfChoices.append(graphic)
    return listOfChoices

def plotGraph():
    styles = ['-', '--', ':', '-.']
    titleChoices = [f'{choice} choices' for choice in choices]
    print("TITOLO ", titleChoices)
    figura = plt.figure(figsize=(13, 10))
    grafico = []
    listPlot = getListPlot()
    listOfIndex = [] 
    for i in range(1, 15):
        listOfIndex.append(i) 
    for f, frame in enumerate(listPlot):
        grafico.append(figura.add_subplot(2, 2, f+1))
        for j, data in enumerate(lambdas):
            grafico[f].plot(listOfIndex, listPlot[f].misurations[j].normalizeMesures(), styles[j], label = f'λ = {data}')
            grafico[f].set_title(titleChoices[f])
            grafico[f].title.set_size(10)
            grafico[f].legend()
            grafico[f].set_xlim([0, 14])
            grafico[f].set_ylim([0, 1])
            grafico[f].set_xlabel('Queue lenght')
            grafico[f].set_ylabel('Fraction of queue with at least that size')
        grafico[f].grid()
    plt.subplots_adjust(hspace=0.3)
    plt.show()

def main():
    creazioneCsv()
    plotGraph()

if __name__ == '__main__':
    main()