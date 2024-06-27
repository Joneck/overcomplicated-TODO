import pymssql
import subprocess
from tkinter import *
from tkinter import messagebox

def AddTask(curs, task):
    curs.execute("IF NOT EXISTS (SELECT * FROM Tasks WHERE text = %s) BEGIN INSERT INTO Tasks VALUES(%s, 0) END;", (task,task))
    connection.commit()

def DeleteTask(curs,task):
    curs.execute("DELETE FROM Tasks WHERE text = %s", (task))
    connection.commit()
    pass

def MarkDoneTask(curs,task):
    curs.execute("UPDATE Tasks SET finished = 1 WHERE text = %s",(task))
    connection.commit()

def ReadTasks(curs):
    curs.execute('SELECT * FROM Tasks WHERE finished = 0')
    res = curs.fetchall()

    prologTransformation = lambda a: '\'' + str(a[0]) + '\','
    to_be_sorted = 'checkEachTask(['
    for i in res:
        to_be_sorted += prologTransformation(i)

    to_be_sorted = to_be_sorted.rstrip(',')
    to_be_sorted += '],X),mergesort(X,SORTED), write(SORTED).'
    return PrologSort(to_be_sorted)
    
def ReadCompletedTasks(curs):
    curs.execute('SELECT text FROM Tasks WHERE finished = 1')
    res = curs.fetchall()
    firstColumn = lambda x: x[0]

    ans = []
    for row in res:
        ans.append(firstColumn(row))
    return ans

def PrologSort(prolog_query):
    result = subprocess.run(['swipl', '-s', 'sort.pl', '-g', prolog_query, '-t', 'halt.' ], capture_output=True, text=True)
    sortedTasks = result.stdout.replace('[','')
    sortedTasks = sortedTasks.replace(']','')
    result = sortedTasks.split(',')
    sortedTasks = []
    for i in range(1,len(result),2):
        sortedTasks.append(result[i])
    return sortedTasks



def submitTask(text):#usuwa istniejące
    global currentLastRow
    currentLastRow = 2

    if len(text) > 45: #odrzucenie za długich tasków
        TaskInput.delete(0, END)
        messagebox.showwarning(message='Za długi tekst')
        return
    

    text = text.strip(' ')
    if text == '': #odrzucenie pustych tasków
        TaskInput.delete(0, END)
        messagebox.showwarning(message='Brak treści')
        return
    
    text = text.replace('ą','a')
    text = text.replace('ę','e')
    text = text.replace('ć','c')
    text = text.replace('ó','o')
    text = text.replace('ł','l')
    text = text.replace('ś','s')
    text = text.replace('ż','z')
    text = text.replace('ź','z')    

    AddTask(curs, text)    
    for i in reversed(unDone): 
        i.delete()
    for i in reversed(Done):
        i.delete()
        
    TaskInput.delete(0, END)

    Starter()

def Starter():
    global currentLastRow
    currentLastRow = 2

    sortedTasks = ReadTasks(curs)
    for element in sortedTasks:
        if element != '':
            unDone.append(UndoneTask(element,root,currentLastRow))
            currentLastRow += 1    

    MiddleLabel.grid(row=currentLastRow , columnspan= 3)
    currentLastRow += 1
    
    completedTasks = ReadCompletedTasks(curs)
    for element in completedTasks:
        Done.append(UndoneTask(element,root,currentLastRow,True))
        currentLastRow +=1


class UndoneTask:
    def __init__(self, tasksText, root,row,fin = False):
        self.finished = fin
        self.tasksText = tasksText
        self.lab = Label(root, text=tasksText)
        if self.finished == False:
            self.doneButton = Button(root, text='Mark as done', command= lambda: self.done())
        self.deleteButton = Button(root, text='Delete task', command= lambda: self.delete(True))
        self.lab.grid(row = row, column= 0, padx=30)
        if self.finished == False:
            self.doneButton.grid(row=row, column= 1)
        self.deleteButton.grid(row=row, column= 2, padx= 20)

    def delete(self, delete = False):
        self.lab.destroy()
        if self.finished == False:
            self.doneButton.destroy()
        self.deleteButton.destroy()

        if delete:
            DeleteTask(curs, self.tasksText)

        if self.finished:
            Done.remove(self)
        else:
            unDone.remove(self)
        

    def done(self):
        global currentLastRow
        self.finished = True
        #self.lab.destroy()
        #self.deleteButton.destroy()
        self.doneButton.destroy()
        self.lab.grid(row=currentLastRow, column=0)
        self.deleteButton.grid(row=currentLastRow,column=2)
        
        MarkDoneTask(curs, self.tasksText)
        unDone.remove(self)
        Done.append(self)
        currentLastRow += 1

#Connection setup
loginData = open("settings.conf", 'r')
srv = loginData.readline().strip('\n ')
user = loginData.readline().strip('\n ')
pwd = loginData.readline().strip('\n ')
dtbs = loginData.readline().strip('\n ')
loginData.close()

connection = pymssql.connect(server = srv, user = user, password = pwd, database = dtbs)
curs = connection.cursor()
curs.execute("IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Tasks') BEGIN CREATE TABLE Tasks (text VARCHAR(45), finished BIT);END;")
connection.commit()

#App setup
root = Tk() 
root.title('TODO app')
a = Label(root, text ="Tasks") 
a.grid(row=0, columnspan=3) 
#root.geometry()
TaskInput = Entry(root,width= 70, bd=5, relief='solid')
TaskInput.grid(row=1, column= 0,columnspan=2, padx = 20)
AddButton = Button(root,text='Add task', command= lambda: submitTask(TaskInput.get()))
AddButton.grid(row=1, column=2, padx= 10)
MiddleLabel = Label(root, text='Completed tasks')
MiddleLabel.grid(row=2 , columnspan= 3)

unDone = []
Done = []
currentLastRow = 2
Starter()
  
root.mainloop() 
connection.close()