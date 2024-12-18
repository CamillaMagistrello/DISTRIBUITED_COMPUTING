import os
import numpy
from matplotlib import pyplot as plt

nomeFile = "mmn_queue_sim/mmn_queue.py"
listaLambda = [0.5, 0.9, 0.95, 0.99]
listD = [1, 2, 5, 10]
listaSomme = []


def creazioneCsv():
    for i in listD:
        for j in listaLambda:
            os.system(f"python {nomeFile} --lambd {j} --max-t 1000 --d {i} --createCsv mmn_queue_sim/misure/{i}{j}.csv")

def getListPlot():
    listaLunghezze = []
    for i in listD:
        listaTemp = []
        for j in listaLambda:
            ms = numpy.loadtxt(f"mmn_queue_sim/misure/{i}{j}.csv", delimiter=',')
            listaTemp.append(ms)
        listaLunghezze.append(listaTemp)
    return listaLunghezze

def plotGraph():
    # legenda = [f"lamd = {i} " for i in listaLambda]
    # stili = ['-', '--', '.', '*']
    figura = plt.figure(figsize=(13, 10))
    grafico = []
    listPlot = getListPlot()
    for f, frameSingleD in enumerate(listPlot):
        grafico.append(figura.add_subplot(2, 2, f+1))
        for j, frameSingleLambda in enumerate(frameSingleD):
            listaNomalizzata = []
            listaIndici = [] 
            for i in range(0, 15):
                listaIndici.append(i) 
            for i in listaIndici:
                listaNomalizzata.append(sum((x >= i) for x in frameSingleLambda))
            lineNorm = [float(k)/max(listaNomalizzata) for k in listaNomalizzata]
        print(listaIndici[1:])
        grafico[f].plot(listaIndici[1:], lineNorm[1:])
        grafico[f].set_xlim([0, 14])
        grafico[f].set_ylim([0, 1])
        
    plt.show()

def main():
    creazioneCsv()
    plotGraph()

if __name__ == '__main__':
    main()