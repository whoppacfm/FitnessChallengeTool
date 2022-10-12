#imports
import numpy as np
import matplotlib.pyplot as plt

from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import sqlite3
from sqlite3 import Error

import tkinter as tk
#from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror
import tkinter.font as font

import datetime
from datetime import date


#TrackerView
#select tracker.tracker_date, tracker_type.name, tracker.value from tracker
#INNER JOIN tracker_type
#ON tracker.tracker_type_id = tracker_type.tracker_type_id


#global variables
root = None
frame = None
dbconn = None
trackertype_input_var = None
tracker_input_var = None
tracker_type_picklist = None
tracker_types_name_list = []
tracker_types_id_list = []
selected_tracker_type=None
selected_tracker_type_name=None

tracker_type_max_values_list = []
tracker_type_sum_values_list = []


#functions
def create_tracker_button_clicked():
    try:
        database = r".\data.db"
        conn = create_connection(database)
        
        #tracker value
        global tracker_input_var 
        test1 = tracker_input_var.get()

        #current date
        date_today = date.today()

        #tracker type
        global tracker_types_name_list
        global tracker_types_id_list
        global selected_tracker_type_name
        
        tracker_type_index = tracker_types_name_list.index(selected_tracker_type_name)
        selected_tracker_type_id = tracker_types_id_list[tracker_type_index]

        #create tracker value
        tracker_id = create_tracker_value(conn, selected_tracker_type_id, date_today.strftime("%Y%m%d"), tracker_input_var.get()) #tracker_type_id,tracker_date,value
        print("New tracker value created successfully")
    except ValueError as error:
        showerror(title='Error', message=error)


def create_tracker_value(conn, tracker_type_id,tracker_date,value):
    sql = ''' INSERT INTO tracker(tracker_type_id,tracker_date,value)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (tracker_type_id,tracker_date,value))
    conn.commit()
    return cur.lastrowid

"""
def create_tracker_value(conn, tracker_type):
    sql = ''' INSERT INTO tracker(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, (tracker_type,))
    conn.commit()
    return cur.lastrowid
"""


def create_trackertype_button_clicked():
    """  Handle convert button click event 
    """
    try:
        database = r".\data.db"
        conn = create_connection(database)
        
        global trackertype_input_var 
        test1 = trackertype_input_var.get()
        tracker_type_id = create_tracker_type(conn, trackertype_input_var.get())
        
        updateTrackerTypes()
        loadTrackerTypes()
        print("New tracker type created successfully")
        
    except ValueError as error:
        showerror(title='Error', message=error)


def updateTrackerTypes():
    global dbconn
    cur = dbconn.cursor()
    cur.execute("SELECT * FROM tracker_type")

    rows = cur.fetchall()

    for row in rows:
        print(row[1])
        
    #tracker_type_picklist.configure(window, user_choice, *updated_list)


def show_chart():
    x = np.array([80, 85, 90, 95, 100, 105, 110, 115, 120, 125])
    y = np.array([240, 250, 260, 270, 280, 290, 300, 310, 320, 330])

    plt.plot(x, y)

    plt.xlabel("Average Pulse")
    plt.ylabel("Calorie Burnage")

    plt.show()


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def loadTrackerTypes():
    database = r".\data.db"
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tracker_type order by name asc")
    rows = cur.fetchall()
    type_list = []
    
    for row in rows:
        #print(row)
        tracker_types_id_list.append(row[0])
        tracker_types_name_list.append(row[1])
        type_list.append(row[1])

    variable = tk.StringVar(frame)
    
    if(len(tracker_types_name_list)>0):
        variable.set(tracker_types_name_list[0]) # default value
        global selected_tracker_type_name
        selected_tracker_type_name = tracker_types_name_list[0]
        global tracker_type_picklist
        tracker_type_picklist = tk.OptionMenu(frame, variable, *type_list, command=onSetTrackerType)
        options = {'padx': 5, 'pady': 5}
        tracker_type_picklist.grid(column=1, row=0, sticky='W', **options)

        #get total values
        global tracker_type_sum_values_list
        cur = conn.cursor()
        cur.execute("""SELECT tracker_type.tracker_type_id, SUM(tracker.value) FROM tracker
                INNER JOIN tracker_type
                ON tracker.tracker_type_id = tracker_type.tracker_type_id
                GROUP BY tracker_type.tracker_type_id
                ORDER BY tracker_type.name asc;""")
        rows = cur.fetchall()
        #for row in rows:
        #    tracker_type_sum_values_list.append(row[0])
        tracker_type_sum_values_list = rows

        #get max values
        global tracker_type_max_values_list
        cur = conn.cursor()
        cur.execute("""select tracker_type.tracker_type_id, MAX(tracker.value) as Value from tracker
                    INNER JOIN tracker_type
                    ON tracker.tracker_type_id = tracker_type.tracker_type_id
                    group by tracker_type.tracker_type_id
                    order by tracker_type.name asc""")
        rows = cur.fetchall()
        #for row in rows:
        #    tracker_type_max_values_list.append(row[0])
        tracker_type_max_values_list=rows


def onSetTrackerType(newTrackerType):
    global selected_tracker_type_name
    selected_tracker_type_name = newTrackerType


def on_click_set_type(typestr):
    print("selected: " + typestr)
    global selected_tracker_type_name
    selected_tracker_type_name=typestr
    #global tracker_type_picklist
    #tracker_type_picklist.set(typestr)


def initGui():
    # root window
    global root
    root = tk.Tk()
    root.title('Fitness Challenge Tool')
    root.geometry('1920x1280')
    root.resizable(True, True)
    
    # frame
    #frame = ttk.Frame(root)
    global frame
    frame = ttk.Frame(root)
    #frame.grid_columnconfigure(5, weight=1)
    frame_b = ttk.Frame(root)
    
    #set theme
    style1 = ttk.Style(root)
    themes = style1.theme_names()
    style1.theme_use(themes[5])


    # field options
    options = {'padx': 5, 'pady': 5}
    
    # calist label
    calist_label = ttk.Label(frame, text='Tracker Types')
    calist_label.grid(column=1, row=0, sticky='W', **options)
    #calist_label.pack()

    create_tracker_label = ttk.Label(frame, text='Tracker')
    create_tracker_label.grid(column=1, row=1, sticky='W', **options)

    # tracker_type_entry
    global trackertype_input_var
    trackertype_input_var = tk.StringVar()
    tracker_type_entry = ttk.Entry(frame, textvariable=trackertype_input_var)
    tracker_type_entry.grid(column=2, row=0, **options)
    #tracker_type_entry.pack()
    tracker_type_entry.focus()

    # tracker entry
    global tracker_input_var
    tracker_input_var = tk.StringVar()
    tracker_entry = ttk.Entry(frame, textvariable=tracker_input_var)
    tracker_entry.grid(column=2, row=1, **options)
    #tracker_type_entry.pack()
    tracker_entry.focus()

    #menu_button1 = ttk.Button(frame, text='New Tracker')
    #menu_button1.grid(column=0, row=0, sticky='W', **options)
    #menu_button1.configure(command=train_button_clicked)
    
    #picklist
    loadTrackerTypes()

    #create tracker type button
    create_trackertype_button = ttk.Button(frame, text='Create new type')
    create_trackertype_button.grid(column=3, row=0, sticky='W', **options)
    #create_trackertype_button.pack()
    create_trackertype_button.configure(command=create_trackertype_button_clicked)

    #create tracker button
    create_tracker_button = ttk.Button(frame, text='Create new value')
    create_tracker_button.grid(column=3, row=1, sticky='W', **options)
    #create_tracke_button.pack()
    create_tracker_button.configure(command=create_tracker_button_clicked)

    chart_button = ttk.Button(frame, text='Chart')
    chart_button.grid(column=4, row=0, sticky='W', **options)
    #chart_button.pack()
    chart_button.configure(command=show_chart)
    

    #buttons
    global tracker_types_name_list
    #global tracker_types_id_list
    #global selected_tracker_type_name
    #tracker_type_index = tracker_types_name_list.index(selected_tracker_type_name)
    #selected_tracker_type_id = tracker_types_id_list[tracker_type_index]
    #cfm
    tcol=1
    trow=2
    toptions = {'ipadx': 10, 'ipady': 10,'padx': 5, 'pady': 5}
    tcount=0
    for ttype in tracker_types_name_list:
        sum_value=0
        max_value=0
        type_id = tracker_types_id_list[tcount]
        #print(ttype + " == " + str(type_id))
        for typesum in tracker_type_sum_values_list:
            if typesum[0] == type_id:
                sum_value = typesum[1]
        for typemax in tracker_type_max_values_list:
            if typemax[0] == type_id:
                max_value = typemax[1]

        #print(ttype + " id: " + str(type_id) + " sum: " + str(sum_value) + " max: " + str(max_value))
        helv36 = font.Font(family='Helvetica', size=15, weight=font.BOLD)
        #btn1 = Button(text='btn1', font=helv36)
        #myFont = font.Font(size=20)
        t_button = tk.Button(frame, text=ttype + ' \nSum: ' +str(sum_value) + ', \nMax: ' + str(max_value), font=helv36, bg='#0052cc', fg='#ffffff', width=20)
        #t_button['font'] = myFont
        t_button.grid(column=tcol, row=trow, sticky='W', **toptions)
        t_button.configure(command=lambda ttype=ttype:on_click_set_type(ttype))
        
        tcol=tcol+1
        if tcol > 5:
            trow=trow+1
            tcol=1
        tcount=tcount+1


    # result label
    result_label = ttk.Label(frame)
    result_label.grid(row=2, columnspan=5, **options)
    #result_label.pack()
    
    # add padding to the frame and show it
    frame.grid(padx=10, pady=10)
    #frame.pack()
    #frame.pack(side="top", fill="both", expand=True)
    #frame.grid_columnconfigure(2, weight=1)
    #frame.grid_rowconfigure(5, weight=1)
    
    # chart data
    """
    data1 = {'Country': ['US','CA','GER','UK','FR'],
             'GDP_Per_Capita': [45000,42000,52000,49000,47000]
            }
    df1 = DataFrame(data1,columns=['Country','GDP_Per_Capita'])
    
    #chart 1
    figure1 = plt.Figure(figsize=(6,5), dpi=100)
    ax1 = figure1.add_subplot(111)
    bar1 = FigureCanvasTkAgg(figure1, frame_b)
    bar1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
    df1 = df1[['Country','GDP_Per_Capita']].groupby('Country').sum()
    df1.plot(kind='bar', legend=True, ax=ax1)
    ax1.set_title('Country Vs. GDP Per Capita')
    
    #chart 2
    figure2 = plt.Figure(figsize=(6,5), dpi=100)
    ax2 = figure2.add_subplot(111)
    bar2 = FigureCanvasTkAgg(figure1, frame_b)
    bar2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
    df1.plot(kind='bar', legend=True, ax=ax2)
    ax2.set_title('Country Vs. GDP Per Capita')
    
    #frame.pack(side=tk.TOP,fill=tk.X)
    #frame_b.pack(side=tk.BOTTOM,fill=tk.X)
    frame.pack(fill=tk.X)
    frame_b.pack(fill=tk.X)
    """

    return root


def create_category_type(conn, category_type):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO category_type(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, (category_type,))
    conn.commit()
    return cur.lastrowid


def create_tracker_type(conn, tracker_type):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO tracker_type(name)
              VALUES(?) '''
    cur = conn.cursor()
    cur.execute(sql, (tracker_type,))
    conn.commit()
    return cur.lastrowid


def create_task(conn, task):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """
    sql = ''' INSERT INTO tasks(name,priority,status_id,project_id,begin_date,end_date)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    return cur.lastrowid


def update_task(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE tasks
              SET priority = ? ,
                  begin_date = ? ,
                  end_date = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()


def initDataTables():
    database = r".\data.db"
    
    # Category_Type (name:text)
    # Data_Unit_Type (name:text)
    # Tracker_Type (name:text)
    # Tracker (tracker_date, category_type, tracker_type, value:integer)
    # Tracker_Value (id, tracker, value:integer)
    
    #sql_create_category_type_table = """ CREATE TABLE IF NOT EXISTS category_type (
    #                                    id integer PRIMARY KEY,
    #                                    name text NOT NULL
    #                                ); """
    
    #sql_create_data_unit_type_table = """ CREATE TABLE IF NOT EXISTS data_unit_type (
    #                                    id integer PRIMARY KEY,
    #                                    name text NOT NULL
    #                                ); """
    
    sql_create_tracker_type_table = """ CREATE TABLE IF NOT EXISTS tracker_type (
                                        tracker_type_id integer PRIMARY KEY,
                                        name text NOT NULL
                                    ); """
    
    sql_create_tracker_table = """ CREATE TABLE IF NOT EXISTS tracker (
                                        tracker_id integer PRIMARY KEY,
                                        tracker_type_id integer NOT NULL,
                                        tracker_date text NOT NULL,
                                        value integer NOT NULL
                                    ); """
                                    #FOREIGN KEY (tracker_type_id) REFERENCES tracker_type (id)
    
    #sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
    #                                    id integer PRIMARY KEY,
    #                                   name text NOT NULL,
    #                                    begin_date text,
    #                                    end_date text
    #                                ); """
    
    #sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
    #                                id integer PRIMARY KEY,
    #                                name text NOT NULL,
    #                                priority integer,
    #                                status_id integer NOT NULL,
    #                                project_id integer NOT NULL,
    #                                begin_date text NOT NULL,
    #                                end_date text NOT NULL,
    #                                FOREIGN KEY (project_id) REFERENCES projects (id)
    #                            );"""
    
    # create a database connection
    conn = create_connection(database)
    
    # create tables
    if conn is not None:
        #print("Create Table category_type")
        #create_table(conn, sql_create_category_type_table)
        #print("Create Table data_unit_type")
        #create_table(conn, sql_create_data_unit_type_table)
        print("Create Table tracker_type")
        create_table(conn, sql_create_tracker_type_table)
        print("Create Table tracker")
        create_table(conn, sql_create_tracker_table)
    else:
        print("Error! cannot create the database connection.")
    
    return conn


def delete_task(conn, id):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = 'DELETE FROM tasks WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def delete_all_tasks(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM tasks'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE priority=?", (priority,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


#def createInitialData(dbconn):
        #with dbconn:
            # Category_Type (name:text)
            # Data_Unit_Type (name:text)
            # Tracker_Type (name:text, data_unit_type)
            # Tracker (datetime, category_type, tracker_type, value:integer)
            
            #category_type = ('Sport')
            #category_type_id = create_category_type(dbconn, category_type)
            
            #tracker_type = ('Liegestuetze')
            #tracker_type_id = create_tracker_type(dbconn, tracker_type)
            
            #tracker1 = (tracker_type_id, datetime.date.today(), 40)
            #tracker1_id = create_tracker(dbconn, tracker1)
            
            # create a new project
            # project = ('Cool App with SQLite & Python', '2015-01-01', '2015-01-30')
            # project_id = create_project(dbconn, project)
            
            # tasks
            # task_1 = ('Analyze the requirements of the app', 1, 1, project_id, '2015-01-01', '2015-01-02')
            # task_2 = ('Confirm with user about the top requirements', 1, 1, project_id, '2015-01-03', '2015-01-05')
            
            # create tasks
            # create_task(dbconn, task_1)
            # create_task(dbconn, task_2)
            
            #update task
            # update_task(dbconn, (2, '2015-01-04', '2015-01-06', 2))
            
            #query
            # select_task_by_priority(dbconn, 1)
            # select_all_tasks(dbconn)
            
            
def main():
    global root

    root = initGui()

    global dbconn    
    dbconn = initDataTables()
    #createInitialData(dbconn)
    
    if root is not None:
        print("Start mainloop")
        root.mainloop()
    else:
        print("Error! Root is none.")


    
# start the app
main()































