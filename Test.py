#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:02:24 2023

@author: yinghuang
"""

import copy
import pandas as pd

# Read the Sudoku input from the file

def read_input(filename):
    try:
        with open(filename, 'r') as file:
            sudoku_input = file.read().replace('|', '').replace('-', '').replace('+', '').replace(',', '').replace('\n', '')
    
        sudoku_array = [[0] * 9 for _ in range(9)]
    
        for i in range(9):
            for j in range(9):
                sudoku_array[i][j] = int(sudoku_input[i * 9 + j])
    
        return sudoku_array
    except FileNotFoundError:
            # Error check: Input file not found
            print("Error: Input file not found.")
            return None
        
def format_sudoku(sudoku_array):
    formatted_sudoku = ""

    for i in range(9):
        if i > 0 and i % 3 == 0:
            formatted_sudoku += "---+---+---\n"

        for j in range(9):
            if j > 0 and j % 3 == 0:
                formatted_sudoku += "|"
            
            value = sudoku_array[i][j]
            formatted_sudoku += "0" if value == 0 else str(value)

        formatted_sudoku += "\n"
        with open('output.txt','w') as f:
           f.write(formatted_sudoku)

    return formatted_sudoku
    

# Find all substructure of our Sudoku
def column_maker(array):
    Data_Frame= pd.DataFrame(array) 
    columns= []
    for col in range(len(Data_Frame.axes[1])): 
        individual_columns=Data_Frame.iloc[:,col].tolist() 
        columns.append(individual_columns) 
    return columns
    
def Box_maker(array):
    grid_size= len(array)
    size_box = int(grid_size**0.5)
    boxes = []
    for box_i in range(0, size_box):
        for box_j in range(0, size_box):
            box = []
            for i in range(0, size_box):
                for j in range(0, size_box):
                    box.append(array[size_box*box_i + i][size_box*box_j + j]) 
            boxes.append(box)
    return boxes

# 
def markupmaker(array):
    grid_size= len(array)
    columns=column_maker(array)
    boxes=Box_maker(array)
    size_box = int(grid_size**0.5)
    markup=[]
    for q in range(grid_size):## Adds an empty list for each row to the markup
        markup_row=[]
        markup.append(markup_row)
        for w in range(grid_size):## adds an empty list for each cell in the markup
            markup_column=[]
            markup[q].append(markup_column)
## Adding values to the markup for each cell
    for i in range(1,grid_size+1):##loop through numbers 1 to 9
        for j in range(grid_size):##loop through rows
            for k in range(grid_size):##loop through cells
                if array[j][k] == 0:
                    if i not in array[j]:## check not in row
                        if i not in columns[k]:## check not in column
                           if i not in boxes[((j//size_box)*size_box)+(k//size_box)]:
                               markup[j][k].append(i)
    return markup

def markup_single(markup,array):
    grid_size=len(array)
    for i in range(grid_size): #going through row of markup
        for j in range(grid_size): #going through cell in markup
            if len(markup[i][j])==1: #checks if markup for cell is single
                array[i][j]=markup[i][j][0] #if it is then fill in the array with that single
                return array
    return array #if no elements of the markup are single then return the array

def markup_minimise(array1):
    count = 0
    while count == 0:
        #markup1 = MarkupSoloFiller2(array1)
        markup1=markupmaker(array1) #create an initial markup for an array
        array2 = markup_single(markup1, array1)#creates a new array with singles filled in from markup
        markup2 = markupmaker(array2)#creates new markup from new array with singles added
        if markup1 == markup2:#checks if new markup is same as initial markup
            count +=1 
        else:
            array1 = array2
    return array2

#############################Guess process####################################

def Is_Error(markup,array):
    grid_size= len(array)
    for i in range(grid_size):
        for j in range(grid_size):
            if array[i][j]==0 and len(markup[i][j])==0: 
                return True
    return False
            
def Is_Solution(array):
    grid_size= len(array)
    for i in range(grid_size):
        for j in range(grid_size):
            if array[i][j] == 0: #if there any cells in the array still not filled in then not a solution so return False
                return False
    return True

def takeThird(elem):
    return elem[2] #just returns third element of list

def Random_Guesser(inputarray):   
    markup=markupmaker(inputarray)
    grid_size= len(inputarray) # Loop through cells in row
    possMarkups=[]
    for i in range(grid_size):
        for j in range(grid_size):
            if len(markup[i][j])!=0:
                possMarkups.append((i,j,len(markup[i][j]))) #make a list of all non mepty markups
    possMarkups.sort(key=takeThird) #sort by their length
    if len(possMarkups)==0: #if there are no possible amrkups then either array is already solved or there is an incorrect input, either way random guesser can do nothing
        return inputarray,False
    i,j=possMarkups[0][0],possMarkups[0][1] #define i and j as coordinate of smallest markup
    k=len(markup[i][j]) #length of smallest markup
    for position in range(k): # Position in markup < amount of numbers in markup
        gArray=copy.deepcopy(inputarray) #create a seperate deep copy going through each element of arrays within arrays to guess from
        gArray[i][j]=markup[i][j][position]# Add chosen number to array
        gArray = markup_minimise(gArray) # Go through trying to solve it with this guess in place
        gMarkup=markupmaker(gArray) #make a markup for guess
        if Is_Solution(gArray):
            return gArray,True #if array is the solution then return True and top of recursion will reutrn the array
        elif not Is_Error(gMarkup,gArray): #if there is not an error with the guess
            gArray,flag=Random_Guesser(gArray) #maker another guess
            if flag: #if flag is true then pass to previous layer of recursion to be passed all the way to the first layer of recursion
                return gArray,flag
        
    return gArray,False #if there is an error then flag false and go back to previous layer till a different guess can be made

# errorCheck part
def errorCheck(array):
    cols=column_maker(array)
    boxes=Box_maker(array)
    grid_size=len(array)
    for i in range(grid_size):#Takes each row
        for j in range(1,grid_size+1):# For each possible entry
            if array[i].count(j)>1 or cols[i].count(j)>1 or boxes[i].count(j)>1:#If any number appears more than once in row i, column i, or box i.
                raise Exception('Input has duplicate values in sub-structure')#Returns an Error message and stops code running.
    if grid_size**(1/2)!=int(grid_size**(1/2)):#Checks the length of the array is a square number.
        raise Exception('length of grid must be a square number')
    for i in range(grid_size):
        if len(array[i])!=grid_size:#Checks each row is of the same length as the columns.
            raise Exception('input not a square')
        for j in range(grid_size):#Cycles through every cell.
            if type(array[i][j])!=int:#Checks inupts are integers.
                raise TypeError(f'Input contains non integer at row {i+1} column {j+1}')#Returns position of error in input and stops code running.
            elif array[i][j]>grid_size or array[i][j]<0:#Checks all inputs are in the correct numerical range for the sudoku.
                raise TypeError(f'Input not in range of expected possible input values at row {i+1} column {j+1}')#Returns location of error and stops code from running.



def solver(filename):
    array = read_input(filename)
    grid_size = len(array)
    global grid_size
    errorCheck(array)
    array1=markup_minimise(array)
    if Is_Solution(array1):
        format_sudoku(array1)
        return array1
    else:
        Sol,Error=Random_Guesser(array1)
        if Error:
            format_sudoku(Sol)
            return Sol
        else:
            raise Exception('Input is not solvable')
# Example array

sudoku_array = solver('input.txt')


