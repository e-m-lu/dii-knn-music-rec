#import os
import csv
import random
import math
import operator
import codecs

#cwd = os.getcwd()
#files = os.listdir(cwd)
#print("Files in '%s' : %s" % (cwd, files))

#os.chdir(r'C:\Users\Fei\Documents\Processing\kNN')
#file = open('iris.data.txt')

# Load input csv file
def loadDataset(filename, split, trainingSet=[] , testSet=[]):
  with open(filename, 'rb') as csvfile: #open in readmode as binary
      #lines = csv.reader(csvfile) 
      lines = csv.reader(codecs.open('sample-input.txt', 'rU', 'utf-16')) #remove null values
      dataset = list(lines) # prepare dataset
      #print len(dataset) # need a larger dataset
      for x in range(len(dataset)): # number of rows
          for y in range(3): # number of columns except the outcome to be predicted
              dataset[x][y] = float(dataset[x][y]) # convert datatype to float
          if random.random() < split: # split the dataset into trainigset and testset randomly
              trainingSet.append(dataset[x])
          else:
              testSet.append(dataset[x])

# Calculate the distance based on S(sqrt(instance1[i]-instance2[i]))
def euclideanDistance(instance1, instance2, length):
  distance = 0
  for x in range(length):
    distance += pow((instance1[x] - instance2[x]), 2)
  return math.sqrt(distance)
 
def getNeighbors(trainingSet, testInstance, k):
  distances = []
  length = len(testInstance)-1
  for x in range(len(trainingSet)):
    dist = euclideanDistance(testInstance, trainingSet[x], length)
    distances.append((trainingSet[x], dist))
  distances.sort(key=operator.itemgetter(1))
  neighbors = []
  for x in range(k):
    neighbors.append(distances[x][0])
  return neighbors
 
def getResponse(neighbors):
  classVotes = {}
  for x in range(len(neighbors)):
    response = neighbors[x][-1]
    if response in classVotes:
      classVotes[response] += 1
    else:
      classVotes[response] = 1
  sortedVotes = sorted(classVotes.iteritems(), key=operator.itemgetter(1), reverse=True)
  return sortedVotes[0][0]
 
def getAccuracy(testSet, predictions):
  correct = 0
  for x in range(len(testSet)):
    if testSet[x][-1] == predictions[x]:
      correct += 1
  return (correct/float(len(testSet))) * 100.0
  
def main():
  # prepare data
  trainingSet=[]
  testSet=[]
  split = 0.67
  loadDataset('sample-input.txt', split, trainingSet, testSet) #don't forget the extension
  print 'Train set: ' + repr(len(trainingSet))
  print 'Test set: ' + repr(len(testSet))
  # generate predictions
  predictions=[]
  k = 3
  for x in range(len(testSet)):
    neighbors = getNeighbors(trainingSet, testSet[x], k)
    result = getResponse(neighbors)
    predictions.append(result)
    print('> predicted=' + repr(result) + ', actual=' + repr(testSet[x][-1]))
  accuracy = getAccuracy(testSet, predictions)
  print('Accuracy: ' + repr(accuracy) + '%')
  
main()
