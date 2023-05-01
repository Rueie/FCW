# -*- coding: utf-8 -*-
import os
import time
import threading
import math
import inspect
import re
import traceback
import platform
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
from idlelib.tooltip import Hovertip
from threading import Thread
from bs4 import BeautifulSoup
from rnnmorph.predictor import RNNMorphPredictor

coding_xml="utf-8"
coding_other_files="utf-8"
file_name_with_param="Params.txt"
file_with_prom_comments="Prom_comments.txt"
if platform.system()=="Linux":
    file_path_with_params=os.path.dirname(os.path.abspath(__file__))+"/"+file_name_with_param
    file_path_with_prom_comments=os.path.dirname(os.path.abspath(__file__))+"/"+file_with_prom_comments
elif platform.system()=="Windows":
    file_path_with_params=os.path.dirname(os.path.abspath(__file__))+"\\"+file_name_with_param
    file_path_with_prom_comments=os.path.dirname(os.path.abspath(__file__))+"\\"+file_with_prom_comments
predictor = None

class controller:
    def __init__(self):
        self.list_of_commands=[]
        self.visual=visual(self)
        self.Model=Model(self)
        self.CheckCommands()
        return
    def AddCommand(self,new_command):
        self.list_of_commands.append(new_command)
    def CheckCommands(self):
        while True:
            if len(self.list_of_commands)>0:
                #print("In controller:",self.list_of_commands[0])
                if self.list_of_commands[0][0]=="Закончить работу":
                    self.visual.AddCommand("Закончить работу")
                    self.Model.AddCommand("Закончить работу")
                    break
                if self.list_of_commands[0][0]=="Visual":
                    self.visual.AddCommand(self.list_of_commands[0][1])
                if self.list_of_commands[0][0]=="Model":
                    self.Model.AddCommand(self.list_of_commands[0][1])
                self.list_of_commands.pop(0)
            else:
                time.sleep(0.1)
    def __del__(self):
        del self.Model
        del self.visual

class visual:
    def __init__(self,init_controller):
        self.number_of_opened_frames=3
        self.current_window=None
        self.current_widget=None
        
        self.controller=init_controller
        self.list_of_commands=[]
        self.thread1=Thread(target=self.Start,args=())
        self.thread1.start()
        
        self.size_of_text=11
        self.size_of_titles=self.size_of_text+4
        
        self.max_number_of_strings_in_row=1
        self.list_of_last_id_of_string=[]
        return
    def wrap(self,string,column_width):
        length=math.floor(column_width/self.size_of_text)
        result_sting=""
        counter=0
        number_of_rows=1
        for simv in string:
            if counter==length:
                counter=0
                number_of_rows+=1
                result_sting+='\n'
            result_sting+=simv
            counter+=1
        if self.max_number_of_strings_in_row<number_of_rows:
            self.max_number_of_strings_in_row=number_of_rows
        return result_sting
    def AddRow(self,message,tag):
        group=self.wrap(message[0],math.floor(int(self.table_with_comments.column("group","width"))*1.35))
        type=self.wrap(message[2],math.floor(int(self.table_with_comments.column("type","width"))*1.35))
        info=self.wrap(message[1],math.floor(int(self.table_with_comments.column("info","width"))*1.45))
        ids=""
        for id in message[3]:
            ids+=id+" "
        if ids=="":
            ids="None"
        ids=self.wrap(ids,math.floor(int(self.table_with_comments.column("ids","width"))*1.35))
        self.table_with_comments.insert("",END,values=(group,type,info,ids),tags=(tag))
        self.style.configure('Table.Treeview',rowheight=self.local_font.metrics('linespace')*self.max_number_of_strings_in_row)
        return
    def ShowSolutionWindow(self,event):
        for selected_item in self.table_with_comments.selection():
            item=self.table_with_comments.item(selected_item)
            data=item["values"]
            self.window_with_solution=Toplevel()
            self.window_with_solution.geometry(str(math.floor(self.main_window.winfo_screenwidth()/2))+"x"+str(math.floor(self.main_window.winfo_screenheight()/2)))
            self.window_with_solution.resizable(width=False,height=False)     
            
            self.window_with_solution_label1=Label(self.window_with_solution,text=data[0])
            self.window_with_solution_label1.pack(anchor=N)
            
            
            self.window_with_solution_label2=Label(self.window_with_solution,text=data[1].replace("\n","")+":")
            self.window_with_solution_label2.pack(anchor=NW)
            
            self.window_with_solution_text1=Text(self.window_with_solution,wrap="word",width=math.floor(self.window_with_solution.winfo_reqwidth()),height=self.max_number_of_strings_in_row)
            self.window_with_solution_text1.insert(END,data[2].replace("\n",""))
            self.window_with_solution_text1.pack(expand=False)
            self.window_with_solution_text1["state"]="disabled"
            
            
            self.window_with_solution_frame=Frame(self.window_with_solution,width=math.floor(self.window_with_solution.winfo_reqwidth()),height=math.floor(self.window_with_solution.winfo_reqheight()*0.85))
            self.window_with_solution_frame.pack(expand=False)
            
            columns=("name","id")
            self.window_with_solution_frame_table=ttk.Treeview(self.window_with_solution_frame,columns=columns,show="headings")
            self.window_with_solution_frame_table.pack(expand=True,fill=BOTH,side=LEFT)
            self.window_with_solution_frame_table.heading("name",text="Имя объекта")
            self.window_with_solution_frame_table.heading("id",text="ID объекта")
            self.window_with_solution_frame_table.column("0",stretch=False,width=math.floor(self.window_with_solution.winfo_reqwidth()*1.5),anchor=W)
            self.window_with_solution_frame_table.column("1",stretch=False,width=math.floor(self.window_with_solution.winfo_reqwidth()*2.5),anchor=CENTER)
            
            self.window_with_solution_frame_table.tag_configure("first",background="#FFFFFF")
            self.window_with_solution_frame_table.tag_configure("second",background="#EFEFEF")
            
            self.window_with_solution_frame_scrollbar=Scrollbar(self.window_with_solution_frame,orient="vertical",command=self.window_with_solution_frame_table.yview)
            self.window_with_solution_frame_scrollbar.pack(side=RIGHT,anchor=E,fill="y")
            self.window_with_solution_frame_table["yscrollcommand"] = self.window_with_solution_frame_scrollbar.set
            
            #print("<"+data[3]+">")
            #print("<"+data[3].replace("\n","")+">")
            list_of_ids=re.findall("([^ ]+)",data[3].replace("\n",""))
            self.controller.AddCommand(["Model",["Предоставить данные об объектах",list_of_ids]])
            
            self.window_with_solution_button1=Button(self.window_with_solution,text="Решить проблему",background="#A7D5B7",width=math.floor(self.window_with_solution.winfo_reqwidth()*0.2),height=math.floor(self.window_with_solution.winfo_reqheight()*0.01),command=lambda:self.GetSolution(selected_item,data[1].replace("\n",""),data[2].replace("\n",""),list_of_ids))
            self.window_with_solution_button1.pack(pady=math.floor(self.window_with_solution.winfo_reqheight()*0.05))
            
            self.window_with_solution.grab_set()
    def GetSolution(self,index_of_string,type_of_solution,info,list_of_ids):
        if self.table_with_comments.item(index_of_string)["tags"][0]!="success":
            self.list_of_last_id_of_string.append([index_of_string,self.table_with_comments.item(index_of_string)["tags"]])
            self.table_with_comments.item(index_of_string,tags="wait")
            self.controller.AddCommand(["Model",["Решение проблемы",[type_of_solution,info,list_of_ids]]])
        self.table_with_comments.selection_remove(index_of_string)
        self.window_with_solution.destroy()
    def Start(self):
        #само окно
        #print("Поток визаульного интерфейса:",threading.current_thread())
        self.main_window=Tk()
        self.main_window.title("Прокруст")
        self.main_window.attributes("-fullscreen", True)
        
        #шапка внутри окна
        self.login_frame=Frame(self.main_window)
        self.user_label=Label(self.login_frame, text="Режим пользователя")
        self.user_label.pack(side=LEFT)
        self.login_button=Button(self.login_frame, text="Авторизоваться",command=self.LogIn)
        self.login_button.pack(side=LEFT)
        self.exit_button=Button(self.login_frame, text="Выйти",command=self.ExitProrust)
        self.exit_button.pack(side=RIGHT)
        self.login_frame.pack()
        
        self.pages=ttk.Notebook(self.main_window)
        self.files_page=Frame(self.pages)
        self.result_page=Frame(self.pages)
        self.tracert_page=Frame(self.pages)
        self.pages.add(self.files_page,text="Анализируемый XML файл модели")
        self.pages.add(self.result_page,text="Результат анализа",state="disabled")
        self.pages.add(self.tracert_page,text="Трассировка модели",state="disabled")
        self.pages.pack(expand = True, fill ="both")

        #первая вкладка
        self.files_page_label1=Label(self.files_page, text="Выберите файл формата '.xml', содержащий данные модели:")
        self.files_page_label1.pack(anchor=N)

        self.files_page_file_path=Entry(self.files_page,justify=CENTER)
        self.files_page_file_path.pack(anchor=N,fill="x")
        self.files_page_file_path.insert(END,"Путь файла...")
        self.files_page_file_path['state']='disabled'

        self.files_page_get_path=Button(self.files_page,text="Выберите файл",command=self.GetPath)
        self.files_page_get_path.pack(anchor=N)

        self.files_page_text_from_file=Text(self.files_page,wrap="word")
        self.files_page_text_from_file.pack(expand=True,side=LEFT,fill="both")
        self.files_page_text_from_file.insert("0.0","Содержание файла...")
        self.files_page_text_from_file.configure(state="disabled")

        self.files_page_text_from_file_scrollbar=Scrollbar(self.files_page,orient="vertical",command = self.files_page_text_from_file.yview)
        self.files_page_text_from_file_scrollbar.pack(side=RIGHT,fill="y")
        self.files_page_text_from_file["yscrollcommand"] = self.files_page_text_from_file_scrollbar.set
        
        #вторая страница
        self.result_page_start_button=Button(self.result_page,text="Начать анализ модели",command=self.ChoiceMechanisms)
        self.result_page_start_button.pack(fill="x")

        self.result_page_label3=Label(self.result_page,text="Progressbar info")
        self.result_page_label3.pack()

        self.result_page_label4=Label(self.result_page,text="")
        self.result_page_label4.pack()

        self.result_page_progressbar=ttk.Progressbar(self.result_page,orient=HORIZONTAL,length=math.floor(self.main_window.winfo_screenwidth()/2))
        self.result_page_progressbar.pack()
        
        self.result_page_fone_progressbar=ttk.Progressbar(self.result_page,orient=HORIZONTAL,length=math.floor(self.main_window.winfo_screenwidth()/2),mode="indeterminate")
        self.result_page_fone_progressbar.pack()

        self.result_page_frame_result=Frame(self.result_page)
        self.result_page_frame_result.pack(expand=True,fill="both")
        
        self.result_page_label1=Label(self.result_page_frame_result,text="Рекомендации и предупреждения:")
        self.result_page_label1.pack(anchor=NW)

        self.style=ttk.Style()
        self.local_font=font.Font(family="Times",size=self.size_of_text)
        self.style.configure("Table.Treeview",font=(self.local_font,self.size_of_text),foreground="#000000", padding=0, background="#FFFFFF")

        self.columns_of_table_with_comments=("group","type","info","ids")
        self.table_with_comments=ttk.Treeview(self.result_page_frame_result,columns=self.columns_of_table_with_comments,show="headings",style="Table.Treeview")
        self.table_with_comments.pack(expand=True,fill=BOTH,side=LEFT)
        self.table_with_comments.heading("group",text="Группа")
        self.table_with_comments.heading("type",text="Тип")
        self.table_with_comments.heading("info",text="Содержание")
        self.table_with_comments.heading("ids",text="ID")
        self.table_with_comments.column("0",stretch=False,width=math.floor(self.main_window.winfo_screenwidth()/10)-10,anchor=CENTER)
        self.table_with_comments.column("1",stretch=False,width=math.floor(self.main_window.winfo_screenwidth()/10)-10,anchor=CENTER)
        self.table_with_comments.column("2",stretch=False,width=math.floor(self.main_window.winfo_screenwidth()/10*6)-10,anchor=W)
        self.table_with_comments.column("3",stretch=False,width=math.floor(self.main_window.winfo_screenwidth()/5)-10,anchor=CENTER)

        self.table_with_comments.tag_configure("first",background="#FFFFFF")
        self.table_with_comments.tag_configure("second",background="#EFEFEF")
        self.table_with_comments.tag_configure("wait",background="#E2E27E")
        self.table_with_comments.tag_configure("success",background="#A7D5B7")
        
        self.table_with_comments.bind("<<TreeviewSelect>>",self.ShowSolutionWindow)
        
        self.result_page_comments_table_scrollbar=Scrollbar(self.result_page_frame_result,orient="vertical",command=self.table_with_comments.yview)
        self.result_page_comments_table_scrollbar.pack(side=RIGHT,anchor=E,fill="y")
        self.table_with_comments["yscrollcommand"] = self.result_page_comments_table_scrollbar.set
        
        self.result_page_frame_tracert=Frame(self.result_page,height=math.floor(self.main_window.winfo_screenheight()/4),width=self.main_window.winfo_screenwidth())
        self.result_page_frame_tracert.pack(anchor=CENTER)
        self.result_page_frame_tracert.pack_propagate(False)

        self.result_page_label2=Label(self.result_page_frame_tracert,text="Трассировка работы:")
        self.result_page_label2.pack(anchor=NW)

        self.result_page_job_tracert=Text(self.result_page_frame_tracert,font="Times "+str(self.size_of_text))
        self.result_page_job_tracert.pack(side=LEFT,expand=True, fill="both")
        
        self.result_page_job_tracert_scrollbar=Scrollbar(self.result_page_frame_tracert,orient="vertical",command=self.result_page_job_tracert.yview)
        self.result_page_job_tracert_scrollbar.pack(side=LEFT,fill="y")
        self.result_page_job_tracert["yscrollcommand"] = self.result_page_job_tracert_scrollbar.set
        
        #третья страница
        self.tracert_page_label1=Label(self.tracert_page,text="Трассировка модели:")
        self.tracert_page_label1.pack(anchor=NW)

        self.tracert_page_frame=Frame(self.tracert_page)
        self.tracert_page_frame.pack(expand=True,fill="both")

        self.tracert_page_tree=ttk.Treeview(self.tracert_page_frame,show="tree")
        self.tracert_page_tree.heading("#0",text="Наша модель",anchor=NW)
        self.tracert_page_tree.pack(side=LEFT,expand=True, fill="both")

        self.tracert_page_tree_srcollbar=Scrollbar(self.tracert_page_frame,orient="vertical",command=self.tracert_page_tree.yview)
        self.tracert_page_tree_srcollbar.pack(side=RIGHT,fill="y")
        self.tracert_page_tree["yscrollcommand"] = self.tracert_page_tree_srcollbar.set

        self.main_window.after(100,self.CheckCommands)
        self.main_window.mainloop()
        return
    def AddCommand(self,new_command):
        self.list_of_commands.append(new_command)
        return
    def CheckCommands(self):
        if len(self.list_of_commands)>0:
            if self.list_of_commands[0]=="Закончить работу":
                del self
            if self.list_of_commands[0]=="Начался процесс чтения и анализа модели":
                self.result_page_fone_progressbar.start()
                self.result_page_progressbar.configure(maximum=100,value=1)
                self.result_page_start_button["state"]="disabled"
            elif self.list_of_commands[0]=="Закончился процесс чтения и анализа модели":
                self.result_page_fone_progressbar.stop()
            elif self.list_of_commands[0][0]=="Состояние прогресса":
                self.result_page_progressbar.configure(maximum=self.list_of_commands[0][2],value=self.list_of_commands[0][1])
            elif self.list_of_commands[0][0]=="Паттерны и механизмы":
                #print(self.list_of_commands[0][1])
                list_for_create=[]
                for i in range(0,len(self.list_of_commands[0][1])):
                    flag_exist=False
                    for j in range(0,len(list_for_create)):
                        if self.list_of_commands[0][1][i][0]==list_for_create[j][0]:
                            flag_exist=True
                            break
                    if flag_exist==False:
                        list_for_create.append([self.list_of_commands[0][1][i][0]])
                        list_for_create[len(list_for_create)-1].append([self.list_of_commands[0][1][i][1],self.list_of_commands[0][1][i][2],self.list_of_commands[0][1][i][4]])
                    else:
                        flag_exist=False
                        for k in range(1,len(list_for_create[j])):
                            if list_for_create[j][k]==self.list_of_commands[0][1][i][1]:
                                flag_exist=True
                                break
                        if flag_exist==False:
                            list_for_create[j].append([self.list_of_commands[0][1][i][1],self.list_of_commands[0][1][i][2],self.list_of_commands[0][1][i][4]])
                #print(list_for_create)
                for i in range(0,len(list_for_create)):
                    label=Label(self.window_with_mechanisms,text=list_for_create[i][0],font=("Times", 14))
                    label.pack(anchor=W)
                    for j in range(1,len(list_for_create[i])):
                        var=BooleanVar()
                        ckeck_btn=Checkbutton(self.window_with_mechanisms,text=list_for_create[i][j][0],variable=var,onvalue=True,offvalue=False)
                        if list_for_create[i][j][1]=="True":
                            ckeck_btn.select()
                            var.set(True)
                        ckeck_btn.pack(anchor=W)
                        self.list_of_patt_and_mech.append([ckeck_btn,var])
                        Hovertip(ckeck_btn, list_for_create[i][j][2], hover_delay=100)
                self.select_patt_and_mech=Button(self.window_with_mechanisms,text="Подтвердить выбор",command=self.SelectPattAndMech)
                self.select_patt_and_mech.pack()
            elif self.list_of_commands[0][0]=="Информация о процессе 1":
                if self.list_of_commands[0][2]=="Обычный":
                    self.result_page_label3.configure(text=self.list_of_commands[0][1],foreground="#000000")
                elif self.list_of_commands[0][2]=="Финальный":
                    self.result_page_label3.configure(text=self.list_of_commands[0][1],foreground="#317917")
            elif self.list_of_commands[0][0]=="Информация о процессе 2":
                if self.list_of_commands[0][2]=="Обычный":
                    self.result_page_label4.configure(text=self.list_of_commands[0][1],foreground="#000000")
                elif self.list_of_commands[0][2]=="Финальный":
                    self.result_page_label4.configure(text=self.list_of_commands[0][1],foreground="#317917")
            elif self.list_of_commands[0][0]=="Трассировка парсинга":
                self.result_page_job_tracert["state"]='normal'
                self.result_page_job_tracert.insert(END,self.list_of_commands[0][1]+"\n")
                self.result_page_job_tracert.yview_moveto('1.0')
                self.result_page_job_tracert["state"]='disabled'
            elif self.list_of_commands[0][0]=="Рекомендации и замечания":
                self.SetRecommendations(self.list_of_commands[0][1])
            elif self.list_of_commands[0][0]=="Модель":
                self.SetModel(self.list_of_commands[0][1])
                self.result_page_start_button["state"]="normal"
            elif self.list_of_commands[0][0]=="Установить объекты рекомендации":
                counter=False
                tag=""
                for object in self.list_of_commands[0][1]:
                    if counter==False:
                        counter=True
                        tag="first"
                    else:
                        counter=False
                        tag="second"
                    self.window_with_solution_frame_table.insert("",END,values=(self.wrap(object[0],int(self.window_with_solution_frame_table.column("name","width"))),self.wrap(object[1],int(self.window_with_solution_frame_table.column("id","width")))),tags=(tag))
            elif self.list_of_commands[0][0]=="Результат выполнения операции":
                if self.list_of_commands[0][1]=="Удача":
                    self.table_with_comments.item(self.list_of_last_id_of_string[0][0],tags=("success"))
                elif self.list_of_commands[0][1]=="Неудача":
                    self.table_with_comments.item(self.list_of_last_id_of_string[0][0],tags=(self.list_of_last_id_of_string[0][1]))
                    self.window_alert=Toplevel()
                    self.window_alert.geometry(str(math.floor(self.main_window.winfo_screenwidth()*0.25))+"x"+str(math.floor(self.main_window.winfo_screenheight()*0.1)))
                    self.window_alert.resizable(width=False,height=False)
                    
                    self.window_alert_label=Label(self.window_alert,text="Данный механизм не имеет реализации решения")
                    self.window_alert_label.pack(anchor=CENTER)
                    
                    self.window_alert.grab_set()
                elif self.list_of_commands[0][1]=="Ошибка":
                    self.table_with_comments.item(self.list_of_last_id_of_string[0][0],tags=(self.list_of_last_id_of_string[0][1]))
                    self.window_alert=Toplevel()
                    self.window_alert.geometry(str(math.floor(self.main_window.winfo_screenwidth()*0.25))+"x"+str(math.floor(self.main_window.winfo_screenheight()*0.1)))
                    self.window_alert.resizable(width=False,height=False)
                    
                    self.window_alert_label=Label(self.window_alert,text="В работе данного механизма возникла ошибка")
                    self.window_alert_label.pack(anchor=CENTER)
                    
                    self.window_alert.grab_set()
                self.list_of_last_id_of_string.pop(0)
            self.list_of_commands.pop(0)
        self.main_window.after(1,self.CheckCommands)
    def SetModel(self,list_of_objects):
        count=0
        self.tracert_page_tree.insert("",END,iid=count,text=list_of_objects[0])
        self.AddBranch(list_of_objects[1],count,count)
    def AddBranch(self,list_of_objects,parent_number,max_number):
        for i in range(0,len(list_of_objects)):
            if isinstance(list_of_objects[i], str):
                self.tracert_page_tree.insert(parent_number,END,text=list_of_objects[i])
            elif isinstance(list_of_objects[i], list):
                max_number+=1
                self.tracert_page_tree.insert(parent_number,END,iid=max_number,text=list_of_objects[i][0])
                max_number=self.AddBranch(list_of_objects[i][1],max_number,max_number)
        return max_number
    def SetRecommendations(self,list_of_recomendations):
        counter=False
        for group in list_of_recomendations:
            for recomendation in group[1]:
                curr_comment=[group[0]]
                curr_comment.append(recomendation[0])
                curr_comment.append(recomendation[1])
                curr_comment.append(recomendation[2])
                if counter==False:
                    counter=True
                    tag="first"
                else:
                    counter=False
                    tag="second"
                self.AddRow(curr_comment,tag)
    def LogIn(self):
        
        login_window=Toplevel()
        login_window.title("Окно ввода пароля")
        login_window.geometry(str(math.floor(self.main_window.winfo_screenwidth()/4))+'x'+str(math.floor(self.main_window.winfo_screenheight()/5)))
        #login_window.attributes('-toolwindow', True)
        login_window.protocol("WM_DELETE_WINDOW", self.LogOut)

        login_window_label_1=Label(login_window, text="Введите пароль:")
        login_window_label_1.pack(anchor=CENTER)

        login_window_entry_password=Entry(login_window,justify=CENTER)
        login_window_entry_password.pack(expand=True,anchor=CENTER,fill="both")
        login_window_button=Button(login_window, text="Войти в режим администратора", command=self.CheckPass)
        login_window_button.pack(anchor=CENTER)

        login_window.grab_set()
        self.current_window=login_window
        self.current_widget=login_window_entry_password
    def LogOut(self):
        self.current_window.grab_release()
        self.current_window.destroy()
        self.current_window=0
    def ExitProrust(self):
        self.controller.AddCommand(["Закончить работу"])
        self.main_window.quit()
    def CheckPass(self):
        params_file=open(file_path_with_params,"r",encoding=coding_other_files)
        while True:
            line=params_file.readline()
            if not line:
                break
            check=""
            for i in range (0,9):
                check+=line[i]
            if check=="Password:":
                check=""
                for i in range (9,len(line)-1):
                    check+=line[i]
                if check==self.current_widget.get():
                    self.LogOut()
                    self.login_button['state']='disabled'
                    self.user_label.configure(text="Режим администратора")
                    if self.number_of_opened_frames==2:
                        self.pages.tab(2,state="normal")
                else:
                    self.current_widget.delete(0,END)
                    self.current_widget.insert(END,"Неверный пароль")
                break
        params_file.close()
    def GetPath(self):
        self.result_page_progressbar.configure(value=0)
        self.result_page_label3.configure(text="Информация, связанная с процессом анализа модели",foreground="#000000")
        self.result_page_label4.configure(text="",foreground="#000000")
        file_path=filedialog.askopenfilename()
        self.files_page_file_path['state']='normal'
        self.files_page_file_path.delete(0,END)
        self.pages.tab(1,state="normal")
        self.result_page_job_tracert.configure(state="normal")
        self.result_page_job_tracert.delete("0.0",END)
        self.result_page_job_tracert.configure(state="disabled")
        self.pages.tab(1,state="disabled")
        self.pages.tab(2,state="normal")
        for i in self.tracert_page_tree.get_children():
            self.tracert_page_tree.delete(i)
        for item in self.table_with_comments.get_children():
            self.table_with_comments.delete(item)
        self.pages.tab(2,state="disabled")
        if file_path!="":
            check_format=""
            counter=0
            for i in range(len(file_path)-1,0,-1):
                if file_path[i]=='.':
                    counter=i+1
                    break
            for i in range(counter,len(file_path)):
                check_format+=file_path[i]
            if check_format=="xml":
                self.files_page_file_path.insert(END,file_path)
                self.files_page_text_from_file['state']='normal'
                self.files_page_text_from_file.delete("0.0",END)
                xml_file=open(file_path, "r",encoding=coding_xml)
                self.files_page_text_from_file.insert(END,xml_file.read())
                self.files_page_text_from_file["state"]='disabled'
                self.pages.tab(1,state='normal')
                self.number_of_opened_frames=2
                if self.login_button['state']=='disabled':
                    self.pages.tab(2,state='normal')
                    self.number_of_opened_frames=3
            else:
                self.files_page_file_path.insert(END,"Некорректный формат файла...")
                self.files_page_text_from_file['state']='normal'
                self.files_page_text_from_file.delete("0.0",END)
                self.files_page_text_from_file.insert("0.0","Содежимое файла...")
                self.files_page_text_from_file["state"]='disabled'
                self.pages.tab(1,state='disabled')
                self.pages.tab(2,state='disabled')
        else:
            self.files_page_text_from_file['state']='normal'
            self.files_page_text_from_file.delete("0.0",END)
            self.files_page_text_from_file.insert("0.0","Содержимое файла...")
            self.files_page_text_from_file["state"]='disabled'
            self.files_page_file_path.insert(END,"Некорректный путь...")
            self.pages.tab(1,state='disabled')
            self.pages.tab(2,state='disabled')
        self.files_page_file_path['state']='disabled'
    def ChoiceMechanisms(self):
        self.window_with_mechanisms=Toplevel()
        self.window_with_mechanisms.title("Механизмы и процедуры")
        self.window_with_mechanisms.geometry(""+str(math.floor(self.main_window.winfo_screenwidth()/2))+"x"+str(math.floor(self.main_window.winfo_screenheight()/2)))
         
        self.list_of_patt_and_mech=[]
        self.window_with_mechanisms.grab_set()
        self.controller.AddCommand(["Model","Получить паттерны и механизмы"])
        return
    def SelectPattAndMech(self):
        self.result_page_label3.configure(text="")
        self.result_page_label4.configure(text="")
        self.result_page_job_tracert["state"]="normal"
        self.result_page_job_tracert.delete('1.0', END)
        self.result_page_job_tracert["state"]="disabled"
        for i in self.tracert_page_tree.get_children():
            self.tracert_page_tree.delete(i)
        for item in self.table_with_comments.get_children():
            self.table_with_comments.delete(item)
        mess=["Выбранные паттерны и механизмы"]
        for i in range(0,len(self.list_of_patt_and_mech)):
            mess.append([self.list_of_patt_and_mech[i][0]["text"],self.list_of_patt_and_mech[i][1].get()])
        self.window_with_mechanisms.grab_release()
        self.window_with_mechanisms.destroy()
        self.controller.AddCommand(["Model",mess])
        self.controller.AddCommand(["Model",["Парсинг модели",self.files_page_file_path.get()]])
        return
    def __del__(self):
        if self.thread1.is_alive()==True:
            self.thread1.join()
    
class Object:
    def __init__(self):
        self.id="None"
        self.type="None"
        self.name="None"
        self.parents_id=[]#A list of strings
        return
    def Set_id(self,new_id):
        self.id=new_id
        return
    def Set_type(self,new_type):
        self.type=new_type
        return
    def Set_name(self,new_name):
        self.name=new_name
        return
    def Get_id(self):
        return self.id
    def Get_type(self):
        return self.type
    def Get_name(self):
        return self.name    
    def Add_parents(self,new_parent):
        self.parents_id.append(new_parent)
        return
    def Change_parent(self,number,new_id):
        if number>len(self.parents_id):
            return None
        else:
            self.parents_id[number]=new_id
        return
    def Get_parent(self,number_of_parent):
        if number_of_parent>=len(self.parents_id) or len(self.parents_id)==0:
            return None
        else:
            return self.parents_id[number_of_parent]
    def Get_parents_id(self):
        return self.parents_id
    def Delete_parent(self,number_of_perent):
        if number_of_perent<0 or (number_of_perent-1)>len(self.parents_id):
            return None
        else:
            del self.parents_id[number_of_perent]
        return
   
class Model(Object):
    def __init__(self,init_controller):
        self.xml_file_path=None
        self.xml_root=None
        self.model_root=None
        self.extension_root=None
        self.controller=init_controller
        self.list_of_commands=[]
        self.list_of_diagrams=[]#List of obj_Diagram type objects
        self.list_of_recomendations=[]#[[группа замечаний,[[замечание,тип замечания,[список id, совпадающий с объектами в кавычках]],...,[замечание,тип замечания,[[список id, совпадающий с объектами в кавычках]]]]],...,[группа замечаний,[...]]]
        self.list_of_patterns_and_mechanisms_from_file=[]
        file_with_params=open(file_path_with_params,"r",encoding=coding_other_files)
        while True:
            line=file_with_params.readline()
            if not line:
                break
            elif line[0:8]!="Password":
                words=re.search('(.*)/(.*)\((.*)\|(\d*)\):(.*)',line)
                new_mech_or_patt=[]
                new_mech_or_patt.append(words.group(1))
                new_mech_or_patt.append(words.group(2))
                new_mech_or_patt.append(words.group(5))
                new_mech_or_patt.append(int(words.group(4)))
                new_mech_or_patt.append(words.group(3))
                if new_mech_or_patt[2][len(new_mech_or_patt[2])-1]=='\n':
                    new_mech_or_patt[2]=new_mech_or_patt[2][0:len(new_mech_or_patt[2])-1]
                self.list_of_patterns_and_mechanisms_from_file.append(new_mech_or_patt)
        self.list_of_patterns_and_mechanisms_from_file=sorted(self.list_of_patterns_and_mechanisms_from_file,key=lambda pat_or_meh: pat_or_meh[3])
        file_with_params.close()
        self.thread1=Thread(target=self.CheckCommands,args=())
        self.thread1.start()
        return
    def SetRoots(self,root):
        self.xml_root=root
        self.model_root=self.xml_root.find("uml:Model")
        self.extension_root=self.xml_root.find("xmi:Extension")
    def ResetXMLFile(self):
        file=open(self.xml_file_path,"w",encoding=coding_other_files)
        file.write(self.xml_root.prettify(formatter="minimal"))
        file.close()
    def Add_diagram(self,new_diagram):
        self.list_of_diagrams.append(new_diagram)
        return
    def Get_diagram(self,number_of_diagram):
        if number_of_diagram<0 or (number_of_diagram-1)>len(self.list_of_diagrams):
            return None
        else:
            return self.list_of_diagrams[number_of_diagram]
    def Get_list_of_diagrams(self):
        return self.list_of_diagrams
    def Find_object_in_Model(self,object_id):
        for i in range(0,len(self.list_of_diagrams)):
            if self.list_of_diagrams[i].Find_object(object_id)!=None:
                return self.list_of_diagrams[i].Find_object(object_id)
        return None
    def Add_recomendation(self,new_recomendation,group_of_recommendation,type_comment,list_of_id):
        for group in self.list_of_recomendations:
            if group[0]==group_of_recommendation:
                for comment in group[1]:
                    if comment[0]==new_recomendation:
                        return
                group[1].append([new_recomendation,type_comment,list_of_id])
                return
        self.list_of_recomendations.append([group_of_recommendation,[[new_recomendation,type_comment,list_of_id]]])
    def Get_recomendation(self,number_of_recomendation):
        if number_of_recomendation<0 or number_of_recomendation>=len(self.list_of_recomendations):
            return None
        else:
            return self.list_of_recomendations[number_of_recomendation]
    def Get_list_of_recomendations(self):
        return self.list_of_recomendations
    def Parse_Model(self,path_of_xml_file):
        self.controller.AddCommand(["Visual","Начался процесс чтения и анализа модели"])
        self.xml_file_path=path_of_xml_file
        xml_file=open(path_of_xml_file,"r",encoding=coding_xml)
        xml_tree=BeautifulSoup(xml_file,"xml")
        xml_file.close()
        self.SetRoots(xml_tree)
        model_package=self.model_root
        model_data=model_package.find_all("umldi:Diagram")
        counter=0
        self.name=model_package.find("packagedElement")["name"]
        for diagram in model_data:
            counter+=1
            our_diagram=obj_Diagram(self)
            self.controller.AddCommand(["Visual",["Состояние прогресса",counter,100]])
            our_diagram.Parse_diaram(diagram)
            self.Add_diagram(our_diagram)
            del our_diagram
        self.Completion_of_the_Model_formation()
        self.controller.AddCommand(["Visual",["Информация о процессе 1","Завершено чтение и формирование представления модели <"+self.Get_name()+">","Финальный"]])
        self.Search_for_recommendations()
        self.controller.AddCommand(["Visual","Закончился процесс чтения и анализа модели"])
        self.SendModel()
        self.SendRecommenadions()
    def SendModel(self):
        mess=[]
        mess.append(self.name)
        data_mess=[]
        for count in range(0,len(self.list_of_diagrams)):
            diagram_mess=[]
            diagram_mess.append(self.list_of_diagrams[count].Get_name())
            data_diagram_mess=[]
            data_diagram_mess.append("Тип диаграммы: "+self.list_of_diagrams[count].Get_type())
            our_list_of_objects=self.list_of_diagrams[count].Get_list_of_objects()
            for i in range(0,len(our_list_of_objects)):
                object_mess=[]
                data_object_mess=[]
                if our_list_of_objects[i].Get_type()=="uml:Class" or our_list_of_objects[i].Get_type()=="uml:Component" or our_list_of_objects[i].Get_type()=="uml:Interface" or our_list_of_objects[i].Get_type()=="uml:AssociationClass" or our_list_of_objects[i].Get_type()=="uml:Boundary":
                    object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID объекта: "+our_list_of_objects[i].Get_id())
                    data_object_mess.append("Независимость существования: "+str(our_list_of_objects[i].Get_independent_existence()))
                    if our_list_of_objects[i].Get_type()=="uml:AssociationClass":
                        data_object_mess.append("Класс отправитель: "+our_list_of_objects[i].Get_sender_class_id()+"("+self.Find_object_in_Model(our_list_of_objects[i].Get_sender_class_id()).Get_name()+")")
                        data_object_mess.append("Класс получатель: "+our_list_of_objects[i].Get_recipient_class_id()+"("+self.Find_object_in_Model(our_list_of_objects[i].Get_recipient_class_id()).Get_name()+")")
                    our_parents=our_list_of_objects[i].Get_parents_id()
                    if our_parents==[] or our_parents==[None]:
                        data_object_mess.append("Родители: нет")
                    else:
                        parent_mess=[]
                        parent_mess.append("Родители")
                        data_parent_mess=[]
                        for j in range(0,len(our_parents)):
                            data_parent_mess.append("Родитель: "+self.Find_object_in_Model(our_parents[j]).Get_name()+"("+our_parents[j]+")")
                        parent_mess.append(data_parent_mess)
                        data_object_mess.append(parent_mess)
                    our_params=our_list_of_objects[i].Get_list_of_parametres()
                    if our_params==[]:
                        data_object_mess.append("Параметры: нет")
                    else:
                        params_mess=[]
                        params_mess.append("Параметры")
                        data_params_mess=[]
                        for j in range(0,len(our_params)):
                            curr_param=[]
                            curr_param.append(our_params[j][2])
                            data_curr_param=[]
                            data_curr_param.append("Уровень видимости: "+our_params[j][0])
                            data_curr_param.append("Тип данных: "+our_params[j][1])
                            data_curr_param.append("Начальное значение: "+our_params[j][4])
                            data_curr_param.append("Кратность: "+our_params[j][3])
                            curr_param.append(data_curr_param)
                            data_params_mess.append(curr_param)
                        params_mess.append(data_params_mess)
                        data_object_mess.append(params_mess)
                    our_funcs=our_list_of_objects[i].Get_list_of_functions()
                    if our_funcs==[]:
                        data_object_mess.append("Функции: нет")
                    else:
                        #print(our_funcs)
                        func_mess=[]
                        func_mess.append("Функции")
                        data_func_mess=[]
                        for j in range(0,len(our_funcs)):
                            curr_func_mess=[]
                            curr_func_mess.append(our_funcs[j][2])
                            data_curr_func_mess=[]
                            data_curr_func_mess.append("Уровень видимости: "+our_funcs[j][0])
                            data_curr_func_mess.append("Возвращаемый тип данных: "+our_funcs[j][1])
                            if len(our_funcs[j])==3:
                                data_curr_func_mess.append("Параметры: нет")
                            else:
                                params_mess=[]
                                params_mess.append("Параметры")
                                data_params_mess=[]
                                for l in range(3,len(our_funcs[j]),2):
                                    data_params_mess.append("Имя параметра:"+our_funcs[j][l+1])
                                    data_params_mess.append("Тип параметра: "+our_funcs[j][l])
                                params_mess.append(data_params_mess)
                                data_curr_func_mess.append(params_mess)
                            curr_func_mess.append(data_curr_func_mess)
                            data_func_mess.append(curr_func_mess)
                        func_mess.append(data_func_mess)
                        data_object_mess.append(func_mess)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:Association" or our_list_of_objects[i].Get_type()=="uml:Dependency" or our_list_of_objects[i].Get_type()=="uml:Realization" or our_list_of_objects[i].Get_type()=="uml:Composition" or our_list_of_objects[i].Get_type()=="uml:Aggregation":
                    if our_list_of_objects[i].Get_name()=="None":
                        our_name=""
                        our_name+=self.Find_object_in_Model(our_list_of_objects[i].Get_sender_class_id()).Get_name()+"->"+self.Find_object_in_Model(our_list_of_objects[i].Get_recipient_class_id()).Get_name()
                        object_mess.append(our_name)
                    else:
                        object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID: "+our_list_of_objects[i].Get_id())
                    data_object_mess.append("ID отправителя: "+our_list_of_objects[i].Get_sender_class_id()+"("+str(self.Find_object_in_Model(our_list_of_objects[i].Get_sender_class_id()).Get_name())+")")
                    data_object_mess.append("Роль отправителя: "+our_list_of_objects[i].Get_role_sender())
                    current_string="Кратность отправителя: "
                    current_string+=our_list_of_objects[i].Get_multiplicity_of_sender_class()
                    data_object_mess.append(current_string)
                    data_object_mess.append("ID получателя: "+our_list_of_objects[i].Get_recipient_class_id()+"("+str(self.Find_object_in_Model(our_list_of_objects[i].Get_recipient_class_id()).Get_name())+")")
                    data_object_mess.append("Роль получателя: "+our_list_of_objects[i].Get_role_recipient())
                    current_string="Кратность получателя: "
                    current_string+=our_list_of_objects[i].Get_multiplicity_of_recipient_class()
                    data_object_mess.append(current_string)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:Actor":
                    object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта : "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID: "+our_list_of_objects[i].Get_id())
                    if len(our_list_of_objects[i].Get_parents_id())==0:
                        data_object_mess.append("Родители: нет")
                    else:
                        our_list_of_parents=our_list_of_objects[i].Get_parents_id()
                        parent_mess=[]
                        parent_mess.append("Родители")
                        data_parent_mess=[]
                        for j in range(0,len(our_list_of_parents)):
                            data_parent_mess.append("Родитель: "+self.Find_object_in_Model(our_list_of_parents[j]).Get_name()+"("+our_list_of_parents[j]+")")
                        parent_mess.append(data_parent_mess)
                        data_object_mess.append(parent_mess)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:UseCase":
                    object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID: "+our_list_of_objects[i].Get_id())
                    if len(our_list_of_objects[i].Get_list_of_actors())==0:
                        data_object_mess.append("Актёры: нет")
                    else:
                        actors_mess=[]
                        actors_mess.append("Актёры")
                        our_list_of_actors=our_list_of_objects[i].Get_list_of_actors()
                        data_actors_mess=[]
                        for j in range(0,len(our_list_of_actors)):
                            data_actors_mess.append("Актёр: "+self.Find_object_in_Model(our_list_of_actors[j]).Get_name()+"("+our_list_of_actors[j]+")")
                        actors_mess.append(data_actors_mess)
                        data_object_mess.append(actors_mess)
                    if len(our_list_of_objects[i].Get_parents_id())==0:
                        data_object_mess.append("Родители: нет")
                    else:
                        parent_mess=[]
                        parent_mess.append("Родители")
                        data_parent_mess=[]
                        our_list_of_parents=our_list_of_objects[i].Get_parents_id()
                        for j in range(0,len(our_list_of_parents)):
                            data_parent_mess.append("Родитель: "+self.Find_object_in_Model(our_list_of_parents[j]).Get_name()+"("+our_list_of_parents[j]+")")
                        parent_mess.append(data_parent_mess)
                        data_object_mess.append(parent_mess)
                    if len(our_list_of_objects[i].Get_list_of_includions())==0:
                        data_object_mess.append("Включения: нет")
                    else:
                        includes_mess=[]
                        includes_mess.append("Включения")
                        our_list_of_includions=our_list_of_objects[i].Get_list_of_includions()
                        data_includes_mess=[]
                        for j in range(0,len(our_list_of_includions)):
                            data_includes_mess.append("Включение: "+self.Find_object_in_Model(our_list_of_includions[j]).Get_name()+"("+our_list_of_includions[j]+")")
                        includes_mess.append(data_includes_mess)
                        data_object_mess.append(includes_mess)
                    if len(our_list_of_objects[i].Get_list_of_extentions())==0:
                        data_object_mess.append("Расширения: нет")
                    else:
                        extends_mess=[]
                        extends_mess.append("Расширения")
                        data_extends_mess=[]
                        our_list_of_extentions=our_list_of_objects[i].Get_list_of_extentions()
                        for j in range(0,len(our_list_of_extentions)):
                            curr_extend=[]
                            curr_extend.append("Расширение: "+our_list_of_extentions[j][0]+"("+self.Find_object_in_Model(our_list_of_extentions[j][0]).Get_name()+")")
                            data_curr_extend=[]
                            if len(our_list_of_extentions[j])==2:
                                list_of_conditions=["Условия в расширении:"]
                                data_list_of_conditions=[]
                                for condition in our_list_of_extentions[j][1]:
                                    data_list_of_conditions.append(condition)
                                list_of_conditions.append(data_list_of_conditions)
                                data_curr_extend.append(list_of_conditions)
                            else:
                                data_curr_extend.append("Условие расширения: нет")
                            curr_extend.append(data_curr_extend)
                            data_extends_mess.append(curr_extend)
                        extends_mess.append(data_extends_mess)
                        data_object_mess.append(extends_mess)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:Boundary":
                    object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:Lifeline":
                    object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID: "+our_list_of_objects[i].Get_id())
                    our_string="Привязанный объект: "+our_list_of_objects[i].Get_connected_object_id()+"("
                    if self.Find_object_in_Model(our_list_of_objects[i].Get_connected_object_id())!=None:
                        our_string+=self.Find_object_in_Model(our_list_of_objects[i].Get_connected_object_id()).Get_name()+")"+"["+self.Find_object_in_Model(our_list_of_objects[i].Get_connected_object_id()).Get_type()+"]"
                    else:
                        our_string+="нет)"
                    data_object_mess.append(our_string)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:Message":
                    if our_list_of_objects[i].Get_name()=="None":
                        object_mess.append("Нет имени (Message)")
                    else:
                        object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID: "+our_list_of_objects[i].Get_id())
                    if self.Find_object_in_Model(our_list_of_objects[i].Get_id_point_from())!=None:
                        data_object_mess.append("ID временной линии или объекта, вызывающей данную процедуру: "+our_list_of_objects[i].Get_id_point_from()+"("+self.Find_object_in_Model(our_list_of_objects[i].Get_id_point_from()).Get_name()+")")
                    else:
                        data_object_mess.append("ID временной линии или объекта, вызывающей данную процедуру: "+our_list_of_objects[i].Get_id_point_from())
                    if self.Find_object_in_Model(our_list_of_objects[i].Get_id_point_to())!=None:
                        data_object_mess.append("ID временной линии, в которой вызывается данная процедура: "+our_list_of_objects[i].Get_id_point_to()+"("+self.Find_object_in_Model(our_list_of_objects[i].Get_id_point_to()).Get_name()+")")
                    else:
                        data_object_mess.append("ID временной линии, в которой вызывается данная процедура: "+our_list_of_objects[i].Get_id_point_to())
                    data_object_mess.append("Тип вызова: "+our_list_of_objects[i].Get_type_connection())
                    data_object_mess.append("Вид вызова: "+our_list_of_objects[i].Get_kind_connection())
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:CombinedFragment":
                    object_mess.append(our_list_of_objects[i].Get_name())
                    data_object_mess.append("Тип объекта: "+our_list_of_objects[i].Get_type())
                    data_object_mess.append("ID: "+our_list_of_objects[i].Get_id())
                    livelines_data=[]
                    livelines_data.append("Затрагиваемые временные линии")
                    data_livelines_data=[]
                    our_list_covered_lifelines=our_list_of_objects[i].Get_list_of_covered_lifeline()
                    for j in range(0,len(our_list_covered_lifelines)):
                        data=self.Find_object_in_Model(our_list_covered_lifelines[j])
                        if data!=None:
                            data=data.name
                        else:
                            data="нет"
                        data_livelines_data.append("ID временной линии: "+our_list_covered_lifelines[j]+"("+data+")")
                    livelines_data.append(data_livelines_data)
                    data_object_mess.append(livelines_data)
                    our_list_of_alternatives=our_list_of_objects[i].Get_list_of_alternatives()
                    alternatives_mess=[]
                    alternatives_mess.append("Альтернативы")
                    data_alternatives_mess=[]
                    for j in range(0,len(our_list_of_alternatives)):
                        curr_alternative=[]
                        curr_alternative.append(our_list_of_alternatives[j][0])
                        data_curr_alternative=[]
                        if len(our_list_of_alternatives[j])!=1:
                            number_mess=0
                            for k in range(1,len(our_list_of_alternatives[j]),2):
                                number_mess+=1
                                new_mess=[]
                                data_new_mess=[]
                                new_mess.append("Вызов "+str(number_mess))
                                data=self.Find_object_in_Model(our_list_of_alternatives[j][k])
                                if data==None:
                                    data="нет"
                                else:
                                    data=data.Get_name()
                                data_new_mess.append("ID временной линии, которая вызывает данную процедуру: "+our_list_of_alternatives[j][k]+"("+data+")")
                                data=self.Find_object_in_Model(our_list_of_alternatives[j][k+1])
                                if data==None:
                                    data="нет"
                                else:
                                    data=data.Get_name()
                                data_new_mess.append("ID временной линии, в которой вызывается данная процедура: "+our_list_of_alternatives[j][k+1]+"("+data+")")
                                new_mess.append(data_new_mess)
                                data_curr_alternative.append(new_mess)
                        curr_alternative.append(data_curr_alternative)
                        data_alternatives_mess.append(curr_alternative)
                    alternatives_mess.append(data_alternatives_mess)
                    data_object_mess.append(alternatives_mess)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
            diagram_mess.append(data_diagram_mess)
            data_mess.append(diagram_mess)
        mess.append(data_mess)
        #print(mess)
        self.controller.AddCommand(["Visual",["Модель",mess]])
    def SendRecommenadions(self):
        for group in self.list_of_recomendations:
            group[1].sort()
        self.controller.AddCommand(["Visual",["Рекомендации и замечания",self.list_of_recomendations]])
    def Completion_of_the_Model_formation(self):
        for i in range(0,len(self.list_of_diagrams)):
            self.controller.AddCommand(["Visual",["Информация о процессе 1","Идёт постформирование диаграммы <"+self.list_of_diagrams[i].Get_name()+">","Обычный"]])
            self.controller.AddCommand(["Visual",["Состояние прогресса",len(self.list_of_diagrams)+i+1,2*len(self.list_of_diagrams)]])
            self.list_of_diagrams[i].Completion_of_the_diagram_formation()
        return 
    def Search_for_recommendations(self):
        #раздел с ванильной проверкой
        flag_class=False
        flag_use_case=False
        flag_sequnce=False
        for i in range(0,len(self.list_of_diagrams)):
            if self.list_of_diagrams[i].Get_type()=="Logical":
                flag_class=True
            elif self.list_of_diagrams[i].Get_type()=="Use Case":
                flag_use_case=True
            elif self.list_of_diagrams[i].Get_type()=="Sequence":
                flag_sequnce=True
            if flag_class==True and flag_use_case==True and flag_sequnce==True:
                break
        if flag_class==False:
            self.Add_recomendation("В модели нет диаграмм классов, из-за чего невозможно поддерживать полноту модели и её детальность","Полнота модели","None",[])
        if flag_use_case==False:
            self.Add_recomendation("В модели нет диаграмм прецедентов, из-за чего нет возможности получить данные о взаимодействиях в системе и актеров, которые влияют на систему","Полнота модели","None",[])
        if flag_sequnce==False:
            self.Add_recomendation("В модели нет диаграмм ситемных взаимодействий, из-за чего нет возможности детализировать существующие диаграммы классов","Полнота модели","None",[])
        #сама ванильная проверка
        counter=0
        for diagram in self.list_of_diagrams:
            counter+=1
            self.controller.AddCommand(["Visual",["Информация о процессе 2","Идёт базовая проверка <"+diagram.Get_name()+">","Обычный"]])
            self.controller.AddCommand(["Visual",["Состояние прогресса",counter,len(self.list_of_diagrams)]])
            diagram.UsualCheck()
        #раздел с неванильными проверками
        #print("In model:",self.list_of_patterns_and_mechanisms_from_file)
        for j in range(0,len(self.list_of_patterns_and_mechanisms_from_file)):
            if len(self.list_of_patterns_and_mechanisms_from_file[j])==6 and self.list_of_patterns_and_mechanisms_from_file[j][2]==str("True"):
                self.list_of_patterns_and_mechanisms_from_file[j][5]()
        self.controller.AddCommand(["Visual",["Информация о процессе 2","Закончена проверка модели и работа выбранных механизмов","Финальный"]])
        self.SaveComments()
        return
    def SaveComments(self):
        file_with_comm=open(file_path_with_prom_comments,"w",encoding=coding_other_files)
        #print(self.list_of_recomendations)
        for group in self.list_of_recomendations:
            for recommendation in group[1]:
                list_of_objects=list(set(re.findall("'([^']+)'",recommendation[0])))
                new_string=group[0]+"/"+recommendation[0]+"/?!#"
                for object in list_of_objects:
                    new_string+="'"+object+"',"
                if new_string[-1]!="#":
                    new_string=new_string[0:-1]
                new_string+="#!?\n"
                file_with_comm.write(new_string)
        return
    def AddCommand(self,new_command):
        self.list_of_commands.append(new_command)
    def CheckCommands(self):
        #print("Поток модели:",threading.current_thread())
        while True:
            if len(self.list_of_commands)>0:
                #print("In Model:",self.list_of_commands)
                if self.list_of_commands[0]=="Закончить работу":
                    break
                elif self.list_of_commands[0]=="Получить паттерны и механизмы":
                    mess=[]
                    mess.append("Паттерны и механизмы")
                    mess.append([])
                    for i in range(0,len(self.list_of_patterns_and_mechanisms_from_file)):
                        mess[1].append(self.list_of_patterns_and_mechanisms_from_file[i])
                    #print(self.list_of_patterns_and_mechanisms_from_file)
                    self.controller.AddCommand(["Visual",mess])
                elif self.list_of_commands[0][0]=="Парсинг модели":
                    #print("Чтение модели из файла",self.list_of_commands[0][1])
                    self.ClearSelf()
                    self.Parse_Model(self.list_of_commands[0][1])
                elif self.list_of_commands[0][0]=="Выбранные паттерны и механизмы":
                    #print(self.list_of_patterns_and_mechanisms_from_file)
                    for i in range(1,len(self.list_of_commands[0])):
                        for k in range(0,len(self.list_of_patterns_and_mechanisms_from_file)):
                            if self.list_of_commands[0][i][0]==self.list_of_patterns_and_mechanisms_from_file[k][1]:
                                self.list_of_patterns_and_mechanisms_from_file[k][2]=str(self.list_of_commands[0][i][1])
                                break
                    #print(self.list_of_patterns_and_mechanisms_from_file)
                    old_file=open(file_path_with_params,"r",encoding=coding_other_files)
                    new_file=open(file_path_with_params+str(1),"w",encoding=coding_other_files)
                    while True:
                        line=old_file.readline()
                        if not line:
                            break
                        if line[len(line)-1]=='\n':
                            line=line[0:-1]
                        flag_exist=False
                        i=0
                        for i in range(0,len(self.list_of_patterns_and_mechanisms_from_file)):
                            if self.list_of_patterns_and_mechanisms_from_file[i][1] in line:
                                flag_exist=True
                                break
                        if flag_exist==True:
                            while line[len(line)-1]!=':':
                                line=line[0:-1]
                            line+=str(self.list_of_patterns_and_mechanisms_from_file[i][2])
                        new_file.write(line+"\n")
                    old_file.close()
                    new_file.close()
                    os.remove(file_path_with_params)
                    os.rename(file_path_with_params+str(1),file_path_with_params)
                    list_of_model_functions=inspect.getmembers(self,predicate=inspect.ismethod).copy()#список всех функций и ссылок на них
                    list_1=[]
                    for i in range(0,len(list_of_model_functions)):
                        list_1.append(list_of_model_functions[i][0])
                        list_1[i]=list_1[i].replace("_","")
                        list_1[i]=list_1[i].upper()
                    list_2=[]
                    for i in range(0,len(self.list_of_patterns_and_mechanisms_from_file)):
                        list_2.append(self.list_of_patterns_and_mechanisms_from_file[i][1])
                        list_2[i]=list_2[i].replace("_","")
                        list_2[i]=list_2[i].replace(" ","")
                        list_2[i]=list_2[i].upper()
                    for i in range(0,len(list_2)):
                        flag_exist=False
                        for j in range(0,len(list_1)):
                            if list_2[i]==list_1[j]:
                                flag_exist=True
                                break
                        if flag_exist:
                            if len(self.list_of_patterns_and_mechanisms_from_file[i])<6:
                                self.list_of_patterns_and_mechanisms_from_file[i].append(list_of_model_functions[j][1])
                            else:
                                self.list_of_patterns_and_mechanisms_from_file[i][5]=list_of_model_functions[j][1]
                elif self.list_of_commands[0][0]=="Предоставить данные об объектах":
                    new_list_of_objects=[]
                    for id in self.list_of_commands[0][1]:
                        if self.Find_object_in_Model(id)!=None:
                            new_object=[]
                            new_object.append(self.Find_object_in_Model(id).name)
                            new_object.append(id)
                            new_list_of_objects.append(new_object)
                    self.controller.AddCommand(["Visual",["Установить объекты рекомендации",new_list_of_objects]])
                elif self.list_of_commands[0][0]=="Решение проблемы":
                    self.GetSolution(self.list_of_commands[0][1])
                self.list_of_commands.pop(0)
            else:
                time.sleep(0.1)
        return
    def ClearSelf(self):
        while len(self.list_of_diagrams)>0:
            del self.list_of_diagrams[0]
        self.list_of_recomendations.clear()
    def __del__(self):
        if self.thread1.is_alive()==True:
            self.thread1.join()
    #Раздел с паттернами и механизмами
    def Offering_classes_on_frequently_repeated_nouns_in_use_cases(self):
        counter=0
        name=re.search('<.*,.* (\w*)>',str(traceback.extract_stack()[-1])).group(1).replace("_"," ")
        for diagram in self.list_of_diagrams:
            counter+=1
            if diagram.Get_type()=="Use Case":
                self.controller.AddCommand(["Visual",["Информация о процессе 2","Работа механизма <"+name+"> в диаграмме <"+diagram.Get_name()+">","Обычный"]])
                diagram.Offering_classes_on_frequently_repeated_nouns_in_use_cases()
            self.controller.AddCommand(["Visual",["Состояние прогресса",counter,len(self.list_of_diagrams)]])
    def Paired_words_in_sequence_diagrams(self):
        counter=0
        name=re.search('<.*,.* (\w*)>',str(traceback.extract_stack()[-1])).group(1).replace("_"," ")
        for diagram in self.list_of_diagrams:
            counter+=1
            self.controller.AddCommand(["Visual",["Информация о процессе 2","Работа механизма <"+name+"> в диаграмме <"+diagram.Get_name()+">","Обычный"]])
            self.controller.AddCommand(["Visual",["Состояние прогресса",counter,len(self.list_of_diagrams)]])
            diagram.Paired_words_in_sequence_diagrams()
    def GRASP(self):
        counter=0
        name=re.search('<.*,.* (\w*)>',str(traceback.extract_stack()[-1])).group(1).replace("_"," ")
        for diagram in self.list_of_diagrams:
            counter+=1
            self.controller.AddCommand(["Visual",["Информация о процессе 2","Работа механизма <"+name+"> в диаграмме <"+diagram.Get_name()+">","Обычный"]])
            self.controller.AddCommand(["Visual",["Состояние прогресса",counter,len(self.list_of_diagrams)]])
            diagram.GRASP()
    def Accounting_for_past_comments(self):
        #предложенная рекоммендация была проигнорирована, в дальнейшем возможны конфликты и ошибки
        #предлодженная рекоммендация была проигнорирована, обратите внимание, что возникли новые рекомендации, связанные с данным объектом
        name=re.search('<.*,.* (\w*)>',str(traceback.extract_stack()[-1])).group(1).replace("_"," ")
        self.controller.AddCommand(["Visual",["Информация о процессе 2","Работа механизма <"+name+">","Обычный"]])
        self.controller.AddCommand(["Visual",["Состояние прогресса",0,1]])
        this_name_of_group_recomendation="Анализ прошлых замечаний"
        file_with_comm=open(file_path_with_prom_comments,"r",encoding=coding_other_files)
        old_list_of_comments=[]
        #print("--------------------------------------------------------------------------------------------------------------")
        #print(self.list_of_recomendations)
        while True:
            string=file_with_comm.readline()
            #print(string)
            if not string:
                break
            string=re.search('(.*)/(.*)/\?!#(.*)#!\?',string)
            curr_type=string.group(1)
            curr_comm=string.group(2)
            curr_list_of_obj=string.group(3)
            curr_list_of_obj=re.findall("'([^']+)'",curr_list_of_obj)
            for curr_object in curr_list_of_obj:
                founded_group=None
                for objects_group in old_list_of_comments:
                    if objects_group[0]==curr_object:
                        founded_group=objects_group
                        break
                if founded_group==None:
                    old_list_of_comments.append([curr_object,[[curr_comm,curr_type]]])
                else:
                    founded_group[1].append([curr_comm,curr_type])
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for group in self.list_of_recomendations:
            if group[0]!=this_name_of_group_recomendation:
                for recomendation in group[1]:
                    flag_exist=False
                    #поиск повторяющейся ркомендации или замечания
                    for objects_group in old_list_of_comments:
                        for comments in  objects_group[1]:
                            if recomendation[0]==comments[0]:
                                flag_exist=True
                                break
                        if flag_exist==True:
                            break
                    if flag_exist==True:
                        new_list_of_objects=re.findall("'([^']+)'",recomendation[0])
                        #print(recomendation[0])
                        #print(new_list_of_objects)
                        #создаем список объектов из данного замечания и связанных с ними замечаниями из прошлой и новой резолюции
                        list_of_group_objects=[]#[имя объекта, список старых замечаний с этим именем объект, список старых замечаний с этим именем объекта]
                        #и заполняем его
                        for object in new_list_of_objects:
                            #print("Object:"+object)
                            list_of_group_objects.append([object,[]])
                            flag_exist=False
                            #заполнение прошлыми замечаниями
                            for objects_group in old_list_of_comments:
                                if objects_group[0]==object:
                                    #print(objects_group)
                                    for elem in objects_group[1]:
                                        #print(elem)
                                        if elem[1]!=this_name_of_group_recomendation:
                                            #print("success")
                                            list_of_group_objects[-1][-1].append(elem[0])
                                    flag_exist=True
                                    break
                            #если ни одного замечания не было найдео, то просто добавляем пустой список
                            if flag_exist==False:
                                list_of_group_objects[-1].append([])
                            list_of_group_objects[-1].append([])
                            #print("Текущие предложения:",self.list_of_recomendations)
                            #заполнение новыми замечаниями
                            for curr_group in self.list_of_recomendations:
                                #print(curr_group[0])
                                if curr_group[0]!=this_name_of_group_recomendation:
                                    for curr_recomendation in curr_group[1]:
                                        curr_objects_list=re.findall("'([^']+)'",curr_recomendation[0])
                                        for curr_objects in curr_objects_list:
                                           #t(curr_objects,"?",object)
                                            if curr_objects==object:
                                                list_of_group_objects[-1][-1].append(curr_recomendation[0])
                                                break
                        count_old=0
                        count_new=0
                        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n",list_of_group_objects,"\n")
                        for curr_group in list_of_group_objects:
                            count_old+=len(curr_group[1])
                            count_new+=len(curr_group[2])
                        #print(count_old,"/",count_new)
                        if count_old==count_new:
                            flag_same=True
                            for curr_group in list_of_group_objects:
                                curr_group[1].sort()
                                curr_group[2].sort()
                                if curr_group[1]!=curr_group[2]:
                                    flag_same=False
                                    break
                            if flag_same==True:
                                self.Add_recomendation("Предложенная рекоммендация:<"+recomendation[0]+">была проигнорирована, в дальнейшем возможны конфликты и ошибки",this_name_of_group_recomendation,"None",[])
                        if count_new>count_old:
                            #print(list_of_group_objects)
                            self.Add_recomendation("Предложенная рекоммендация:<"+recomendation[0]+">была проигнорирована, обратите внимание, что возникли новые рекомендации, связанные с данным объектом или диаграммой",this_name_of_group_recomendation,"None",[])
        self.controller.AddCommand(["Visual",["Состояние прогресса",1,1]])
        return
    def GetSolution(self,data):
        if data[0]=="Вынос функции в родителя":
            list_of_names=re.findall("('[^']+')",data[1])
            function_name=list_of_names[0][1:-1]
            curr_diagram=self.Find_object_in_Model(data[2][0])
            parent_class=self.Find_object_in_Model(data[2][len(data[2])-1])
            list_of_childs=[]
            for i in range(1,len(data[2])-1):
                list_of_childs.append(self.Find_object_in_Model(data[2][i]))
            parent_node=self.model_root.find("packagedElement",attrs={"xmi:id":parent_class.id})
            parent_help_node=self.extension_root.find("element",attrs={"xmi:idref":parent_class.id})
            if parent_node!=None and parent_help_node!=None:
                for child in list_of_childs:
                    if not self.model_root.find("packagedElement",attrs={"xmi:id":child.id}) or not self.extension_root.find("element",attrs={"xmi:idref":child.id}) or not self.model_root.find("packagedElement",attrs={"xmi:id":child.id}).find("ownedOperation",attrs={"name":function_name}) or not self.extension_root.find("element",attrs={"xmi:idref":child.id}).find("operation",attrs={"name":function_name}):
                        self.controller.AddCommand(["Visual",["Результат выполнения операции","Ошибка"]])
                        return
                first_child=self.model_root.find("packagedElement",attrs={"xmi:id":list_of_childs[0].id})
                first_child_help=self.extension_root.find("element",attrs={"xmi:idref":list_of_childs[0].id})
                if first_child.find("ownedOperation",attrs={"name":function_name}) and first_child.find("ownedOperation",attrs={"name":function_name}).has_attr("xmi:id") and first_child_help.find("operation",attrs={"xmi:idref":first_child.find("ownedOperation",attrs={"name":function_name})["xmi:id"]}):
                    operation=first_child.find("ownedOperation",attrs={"name":function_name})
                    operation_help=first_child_help.find("operation",attrs={"xmi:idref":first_child.find("ownedOperation",attrs={"name":function_name})["xmi:id"]})
                    parent_node.append(BeautifulSoup(str(operation),"xml"))
                    if not parent_help_node.find("operations"):
                        new_tag=BeautifulSoup(str(parent_help_node),"xml").new_tag("operations")
                        parent_help_node.append(new_tag)
                    parent_help_node.operations.append(BeautifulSoup(str(operation_help),"xml"))
                    for child in list_of_childs:
                        curr_child=self.model_root.find("packagedElement",attrs={"xmi:id":child.id})
                        curr_child_help=self.extension_root.find("element",attrs={"xmi:idref":child.id})
                        curr_child.find("ownedOperation",attrs={"name":function_name}).decompose()
                        curr_child_help.find("operation",attrs={"name":function_name}).decompose()                        
                        flag_exist=False
                        for tag in curr_child_help.operations:
                            if tag!="\n":
                                flag_exist=True
                                break
                        if flag_exist==False:
                            curr_child_help.operations.decompose()
                    self.ResetXMLFile()
                else:
                    self.controller.AddCommand(["Visual",["Результат выполнения операции","Ошибка"]])
                    return
            else:
                self.controller.AddCommand(["Visual",["Результат выполнения операции","Ошибка"]])
                return
            self.controller.AddCommand(["Visual",["Результат выполнения операции","Удача"]])
        else:
            self.controller.AddCommand(["Visual",["Результат выполнения операции","Неудача"]])
        return

class obj_Diagram(Object):
    def __init__(self,init_model):
        self.list_of_objects=[]
        self.model=init_model
        self.list_of_nouns=[]#[[сущевтвительное,число повторений существительного],...,[сущевтвительное,число повторений существительного]]
        self.list_of_verbs=[]#[[глагол,имя объекта-родителя этого глагола],...,[глагол,имя объекта-родителя этого глагола]]
        super().__init__()
        return
    def Add_object(self,new_object):
        self.list_of_objects.append(new_object)
        return
    def Delete_object(self,number_of_object,object_id):
        if number_of_object!=None and number_of_object>-1 and (number_of_object-1)<=len(self.list_of_objects):
            self.list_of_objects.pop(number_of_object)
        elif object_id!=None:
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_id()==object_id:
                    self.list_of_objects.pop(i)
                    break
        return
    def Get_object(self,number_of_object):
        if number_of_object<0 or number_of_object>=len(self.list_of_objects):
            return None
        else:
            return self.list_of_objects[number_of_object]
    def Get_list_of_objects(self):
        return self.list_of_objects
    def Find_object(self,object_id):
        if object_id==self.id:
            return self
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_id()==object_id:
                return self.list_of_objects[i]
        return None
    def Get_nouns_and_verbs_from_words(self,object):
        words=[]
        begin=0
        end=0
        current_fraze=object.Get_name()
        current_fraze=current_fraze.replace("_"," ")
        for j in range(0,len(current_fraze)):
            if current_fraze[j]==" ":
                end=j
                if begin!=0:
                    begin+=1
                words.append(current_fraze[begin:end])
                begin=end
            elif j==(len(current_fraze)-1):
                end=j
                if len(words)==0:
                    begin-=1
                words.append(current_fraze[begin+1:end+1])
        words=predictor.predict(words)
        for j in range(0,len(words)):
            if words[j].pos=="VERB":
                flag_exist=False
                for k in range(0,len(self.list_of_verbs)):
                    if self.list_of_verbs[k]==words[j].normal_form:
                        flag_exist=True
                        break
                if flag_exist==False:
                    new_verb=[]
                    new_verb.append(words[j].normal_form.casefold())
                    new_verb.append(object.Get_name())
                    self.list_of_verbs.append(new_verb)
            elif words[j].pos=="NOUN":
                flag_extention=False
                for k in range(0,len(self.list_of_nouns)):
                    if self.list_of_nouns[k][0]==words[j].normal_form.casefold():
                        self.list_of_nouns[k][1]+=1
                        flag_extention=True
                        break
                if flag_extention==False:
                    new_noun=[]
                    new_noun.append(words[j].normal_form.casefold())
                    new_noun.append(1)
                    self.list_of_nouns.append(new_noun)
        return
    def Parse_diaram(self,root):
        local_root=root
        if local_root.has_attr("modelElement"):
            self.id=local_root["modelElement"]
        self.type=local_root
        if self.type.has_attr("xmi:id") and self.model.extension_root.find("diagram",attrs={"xmi:id":self.type["xmi:id"]}):
            self.type=self.model.extension_root.find("diagram",attrs={"xmi:id":self.type["xmi:id"]})
            if self.type.find("properties") and self.type.properties.has_attr("name") and self.type.properties.has_attr("type"):
                self.name=self.type.properties["name"]
                self.type=self.type.properties["type"]
        self.model.controller.AddCommand(["Visual",["Информация о процессе 1","Идёт чтение диаграммы <"+self.name+">","Обычный"]])
        self.Parse_node(local_root)
        return
    def Parse_node(self,root):
        local_root=root
        for local_elem in local_root.children:
            child=None
            list_of_tags=["packagedElement","lifeline","message","fragment"]
            if local_elem!="\n":
                for tag in list_of_tags:
                    child=self.model.model_root.find(tag,attrs={"xmi:id":local_elem["modelElement"]})
                    if child!=None:
                        break
            if child!=None and (child.name=="packagedElement" or child.name=="nestedClassifier" or child.name=="lifeline" or child.name=="message" or child.name=="ownedAttribute" or child.name=="ownedComment" or child.name=="ownedBehavior" or child.name=="fragment"):
                """if child["xmi:type"]=="uml:Package" or child["xmi:type"]=="uml:Collaboration" or (child["xmi:type"]=="uml:Interaction" and child.name=="ownedBehavior"):
                    self.Parse_node(child)"""
                if child["xmi:type"]=="uml:Class" or child["xmi:type"]=="uml:Component" or child["xmi:type"]=="uml:Interface" or child["xmi:type"]=="uml:AssociationClass":
                    new_obj_class=obj_Class(self)
                    new_obj_class.Parse_class(child)
                    del new_obj_class
                if child["xmi:type"]=="uml:Association" or child["xmi:type"]=="uml:Dependency" or child["xmi:type"]=="uml:Realization":
                    new_obj_connection=obj_Connection(self)
                    new_obj_connection.Parse_connection(child)
                    del new_obj_connection
                if child["xmi:type"]=="uml:UseCase":
                    new_use_case=obj_Use_Case(self)
                    new_use_case.Parse_use_case(child)
                    del new_use_case
                if child["xmi:type"]=="uml:Actor":
                    new_actor=Object()
                    if child.has_attr("name"):
                        new_actor.Set_name(child["name"])
                        local_name=child["name"]
                    else:
                        new_actor.Set_name("None")
                    if child.has_attr("xmi:id"):
                        new_actor.Set_id(child["xmi:id"])
                    else:
                        new_actor.Set_id("None")
                    if child.has_attr("xmi:type"):
                        new_actor.Set_type(child["xmi:type"])
                        local_type=child["xmi:type"]
                    else:
                        new_actor.Set_type("None")
                    if len(child.contents)!=0:
                       for i in range(0,len(child.contents)):
                        if child.contents[i].name=="generalization" and child.contents[i].has_attr("general"):
                            new_actor.Add_parents(child.contents[i]["general"])
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",new_actor.type+"'"+new_actor.name+"' начал читаться из XML файла"]])
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",new_actor.type+"'"+new_actor.name+"' прочитан"]])
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",new_actor.type+"'"+new_actor.name+"' добавляется в модель"]])
                    self.Add_object(new_actor)
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",new_actor.type+"'"+new_actor.name+"' добавлен в модель"]])
                    del new_actor
                if child["xmi:type"]=="uml:Lifeline":
                    new_obj_lifeLine=obj_LifeLine(self)
                    new_obj_lifeLine.Parse_LifeLine(child)
                    del new_obj_lifeLine
                if child["xmi:type"]=="uml:Message":
                    our_obj_time_connection=obj_Message(self)
                    our_obj_time_connection.Parse_Message(child)
                    del our_obj_time_connection
                if child["xmi:type"]=="uml:CombinedFragment":
                    our_alternative=obj_Alternative(self)
                    our_alternative.Parse_alternative(child)
                    del our_alternative
                if child["xmi:type"]=="uml:Comment":
                    our_comment=Object()
                    if child.has_attr("xmi:type"):
                        our_comment.Set_type(child["xmi:type"])
                    if child.has_attr("body"):
                        our_comment.Set_name("body")
                    if child.has_attr("xmi:id"):
                        our_comment.Set_id(child["xmi:id"])
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",our_comment.type+"'"+our_comment.name+"' начал читаться из XML файла"]])
                    if len(child.contents)!=0 and child.contents[1].has_attr("xmi:idref"):
                        our_comment.Add_parents(child.contents[1]["xmi:idref"])
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",our_comment.type+"'"+our_comment.name+"' прочитан"]])
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",our_comment.type+"'"+our_comment.name+"' добавляется в модель"]])
                    self.Add_object(our_comment)
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга",our_comment.type+"'"+our_comment.name+"' добавлен в модель"]])
                    del our_comment
        return
    def Completion_of_the_diagram_formation(self): 
        if self.type=="Logical":#диаграмма классов
            for object in self.list_of_objects:
                if isinstance(object,obj_Connection):   
                    if object.Get_flag_composite() or object.Get_flag_shared():
                        source=self.Find_object(object.Get_sender_class_id())
                        target=self.Find_object(object.Get_recipient_class_id())
                        if source!="None" and target!="None":
                            additional_param=["Protected","None","None","None","None"]
                            additional_param[1]=source.name
                            new_name=source.name+"_1"
                            target_params=target.Get_list_of_parametres()
                            while list(filter(lambda x: str(new_name) in x, target_params)):
                                new_name+="_1"
                            additional_param[2]=new_name
                            target.Add_param(additional_param)
                        if object.Get_flag_composite()==True:
                            source.Set_independent_existence(False)
        if self.type=="Sequence":
            for object in self.list_of_objects:
                if object.type=="uml:Message":
                    lifeline=object.Get_id_point_from()
                    if lifeline!=None:
                        lifeline=self.Find_object(lifeline)
                        if lifeline==None:
                            lifeline=self.model.model_root.find("lifeline",attrs={"xmi:id":object.Get_id_point_from()})
                            if lifeline!=None:
                                new_obj_lifeLine=obj_LifeLine(self)
                                new_obj_lifeLine.Parse_LifeLine(lifeline)
                                del new_obj_lifeLine
                    lifeline=object.Get_id_point_to()
                    if lifeline!=None:
                        lifeline=self.Find_object(lifeline)
                        if lifeline==None:
                            lifeline=self.model.model_root.find("lifeline",attrs={"xmi:id":object.Get_id_point_to()})
                            if lifeline!=None:
                                new_obj_lifeLine=obj_LifeLine(self)
                                new_obj_lifeLine.Parse_LifeLine(lifeline)
                                del new_obj_lifeLine
        return
    def UsualCheck(self):
        global predictor
        if predictor==None:
            predictor=RNNMorphPredictor(language="ru")
        if len(self.list_of_objects)==0:
            self.model.Add_recomendation("Диаграмма '"+self.name+"' пустая, рекомендуется внести в неё элементы","Детальность модели","None",[])
        local_numbers=0
        for i in range(0,len(self.model.Get_list_of_diagrams())):
            if self.model.Get_list_of_diagrams()[i].Get_name()==self.name:
                local_numbers+=i*1000
        if self.type=="Use Case":
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_type()=="uml:UseCase":
                    flag_extention=False
                    for j in range(0,len(self.list_of_objects)):
                        if self.list_of_objects[j].Get_type()=="uml:UseCase":
                            list_of_extentions=self.list_of_objects[j].Get_list_of_extentions()
                            for k in range(0,len(list_of_extentions)):
                                if list_of_extentions[k][0]==self.list_of_objects[i].Get_id():
                                    flag_extention=True
                    if flag_extention==False:
                        list_of_diagrams=self.model.Get_list_of_diagrams()
                        flag_exist=False
                        number_of_an_existing_diagram=-1
                        for j in range(0,len(list_of_diagrams)):
                            if list_of_diagrams[j].Get_name()==self.list_of_objects[i].Get_name():
                                flag_exist=True
                                number_of_an_existing_diagram=j
                                break
                        if flag_exist==False:
                            self.model.Add_recomendation("Рекомендуется создать диаграмму системных взаимодействий, связанную с прецедентов '"+self.list_of_objects[i].Get_name()+"'","Полнота модели","None",[])
                        else:
                            list_of_actors=self.list_of_objects[i].Get_list_of_actors()
                            sequence_diagram_objects=self.model.Get_diagram(number_of_an_existing_diagram).Get_list_of_objects()
                            for j in range(0,len(list_of_actors)):
                                flag_extention=False
                                for k in range(0,len(sequence_diagram_objects)):
                                    if sequence_diagram_objects[k].Get_type()=="uml:Actor" and sequence_diagram_objects[k].Get_name()==self.model.Find_object_in_Model(list_of_actors[j]).Get_name():
                                        flag_extention=True
                                        break
                                if flag_extention==False:
                                    self.model.Add_recomendation("Рекомендуется добавить актёра с именем '"+self.model.Find_object_in_Model(list_of_actors[j]).Get_name()+"' в диаграмму системных взаимодейтсвий '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'","Детальность модели","None",[])
                            list_of_extentions=self.list_of_objects[i].Get_list_of_extentions()
                            for j in range(0,len(list_of_extentions)):
                                flag_extention=False
                                for k in range(0,len(sequence_diagram_objects)):
                                    if sequence_diagram_objects[k].Get_type()=="uml:CombinedFragment" and self.model.Find_object_in_Model(list_of_extentions[j][0]).Get_name()==sequence_diagram_objects[k].Get_name():
                                        flag_extention=True
                                        break
                                if flag_extention==False:
                                    self.model.Add_recomendation("Рекомендуется добавить комбинированный фрагмент (alt) с именем '"+self.model.Find_object_in_Model(list_of_extentions[j][0]).Get_name()+"' в диаграмму системных взаимодействий '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'","Полнота модели","None",[])
                                else:
                                    flag_extention=False
                                    list_of_alternatives=sequence_diagram_objects[k].Get_list_of_alternatives()
                                    if len(list_of_extentions[j])!=1:
                                        for condition in list_of_extentions[j][1]:
                                            flag_exist=False
                                            for condition_in_alternative in list_of_alternatives:
                                                if condition==condition_in_alternative[0]:
                                                    flag_exist=True
                                                    break
                                            if flag_exist==False:
                                                self.model.Add_recomendation("Рекомендуется добавить условие '"+condition+"' в комбинированный фрагмент '"+self.model.Find_object_in_Model(list_of_extentions[j][0]).Get_name()+"' в диаграмме системных взаимодействий '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'","Детальность модели","None",[])
        if self.type=="Sequence":
            list_of_use_cases_diagrams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Use Case":
                    list_of_use_cases_diagrams.append(self.model.Get_diagram(i))
            flag_exist=False
            for i in range(0,len(list_of_use_cases_diagrams)):
                list_of_use_case_diagram_objects=list_of_use_cases_diagrams[i].Get_list_of_objects()
                for j in range(0,len(list_of_use_case_diagram_objects)):
                    if list_of_use_case_diagram_objects[j].Get_name()==self.name:
                        flag_exist=True
                        break
                if flag_exist==True:
                    break
            if flag_exist==False:
                self.model.Add_recomendation("Рекомендуется создать прецедент с именем '"+self.name+"', который будет связан с диаграммой системных взаимодействий с именем '"+self.name+"'","Полнота модели","None",[])
            else:
                counter=0
                list_of_objects=self.Get_list_of_objects()
                for i in range(0,len(list_of_objects)):
                    if list_of_objects[i].Get_type()=="uml:Lifeline":
                        counter+=1
                        if list_of_objects[i].Get_connected_object_id()!="None":
                            connected_object=self.model.Find_object_in_Model(list_of_objects[i].Get_connected_object_id())
                            if connected_object.Get_type()!="uml:Actor":
                                list_of_functions=connected_object.Get_list_of_functions()
                                list_of_messages=[]
                                for j in range(0,len(list_of_objects)):
                                    if list_of_objects[j].Get_type()=="uml:Message" and list_of_objects[j].Get_id_point_to()==list_of_objects[i].Get_id():
                                        list_of_messages.append(list_of_objects[j])
                                for j in range(0,len(list_of_messages)):
                                    flag_exist=False
                                    for k in range(0,len(list_of_functions)):
                                        if list_of_messages[j].Get_name()==list_of_functions[k][2]:
                                            flag_exist=True
                                            break
                                    if flag_exist==False:
                                        self.model.Add_recomendation("Объект '"+connected_object.Get_name()+"' не имеет функцию с именем '"+list_of_messages[j].Get_name()+"'. Рекомендуется изменить имя системного вызова в диаграмме системных взаимодейтсвий с именем '"+self.name+"' на уже существующую в данном объекте или создать новую функцию с таким именем","Детальность модели","None",[])
                        else:
                            self.model.Add_recomendation("Рекомендуется соединить временную линию '"+list_of_objects[i].Get_name()+"' в диаграмме системных взаимодействий с именем '"+self.name+"' с существующим классом","Детальность модели","None",[])
                    if list_of_objects[i].Get_type()=="uml:CombinedFragment":
                        list_of_covered_lifelines=list_of_objects[i].Get_list_of_covered_lifeline().copy()
                        j=0
                        #print(list_of_covered_lifelines)
                        while j<len(list_of_covered_lifelines):
                            if self.model.Find_object_in_Model(list_of_covered_lifelines[j]).Get_connected_object_id()=="None" or (self.model.Find_object_in_Model(self.model.Find_object_in_Model(list_of_covered_lifelines[j]).Get_connected_object_id())!=None and self.model.Find_object_in_Model(self.model.Find_object_in_Model(list_of_covered_lifelines[j]).Get_connected_object_id()).Get_type()=="uml:Actor"):
                                list_of_covered_lifelines.pop(j)
                            else:
                                j+=1
                        if len(list_of_covered_lifelines)==0 and list_of_objects[i].Get_type_alternative()=="alt":
                            list_of_use_cases_diagrams=[]
                            for j in range(0,len(self.model.Get_list_of_diagrams())):
                                if self.model.Get_diagram(j).Get_type()=="Use Case":
                                    list_of_use_cases_diagrams.append(self.model.Get_diagram(j))
                            current_use_case_diagram=None
                            current_use_case=None
                            for j in range(0,len(list_of_use_cases_diagrams)):
                                list_of_use_case_diagram_objects=list_of_use_cases_diagrams[j].Get_list_of_objects()
                                current_use_case_diagram=list_of_use_cases_diagrams[j]
                                flag_exist=False
                                for k in range(0,len(list_of_use_case_diagram_objects)):
                                    if list_of_use_case_diagram_objects[k].Get_name()==self.name:
                                        flag_exist=True
                                        current_use_case=list_of_use_case_diagram_objects[k]
                                        break
                                if flag_exist==True:
                                    break
                            list_of_extentions=current_use_case.Get_list_of_extentions()
                            flag_exist=False
                            for extention in list_of_extentions:
                                if self.model.Find_object_in_Model(extention[0]).Get_name()==list_of_objects[i].Get_name():
                                    list_of_extentions=extention
                                    flag_exist=True
                                    break
                            #print(list_of_extentions)
                            if flag_exist==False:
                                self.model.Add_recomendation("Рекомендуется добавить расширение с именем '"+list_of_objects[i].Get_name()+"' в прецедент с именем '"+current_use_case.Get_name()+"' в диаграмме прецедентов '"+current_use_case_diagram.Get_name()+"'","Детальность модели","None",[])
                            else:
                                #print("LIST:")
                                #print(list_of_objects[i].Get_list_of_alternatives())
                                for condition in list_of_objects[i].Get_list_of_alternatives():
                                    #print("CON",condition)
                                    flag_exist=False
                                    #print("List_of_ext:")
                                    #print(list_of_extentions[1])
                                    if len(list_of_extentions)==2:
                                        for node_condition in list_of_extentions[1]:
                                            if condition[0]==node_condition:
                                                flag_exist=True
                                                break
                                    if flag_exist==False:
                                        self.model.Add_recomendation("Рекомендуется добавить условие '"+condition[0]+"' из '"+list_of_objects[i].name+"' из '"+self.name+"' в расширение '"+self.model.Find_object_in_Model(list_of_extentions[0]).name+"' в '"+current_use_case_diagram.name+"'","Детальность модели","None",[])
                if counter<2:
                    self.model.Add_recomendation("В диаграмме системных взаимодействий '"+self.name+"' есть только одна временная линия. Данная диаграмма является некорректной и рекомендуется добавление в неё еще нескольких временных линий.","Детальность модели","None",[])
        if self.type=="Logical":
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_type()=="uml:Class":
                    if len(self.list_of_objects[i].Get_list_of_functions())==0:
                        self.model.Add_recomendation("Рекомендуется в класс '"+self.list_of_objects[i].Get_name()+"' добавить функции, т.к. класс не обладает ни одной функцией","Детальность модели","None",[])
                    list_of_children=[]
                    for j in range(0,len(self.list_of_objects)):
                        if self.list_of_objects[j].Get_type()=="uml:Class":
                            list_of_parents=self.list_of_objects[j].Get_parents_id()
                            for k in range(0,len(list_of_parents)):
                                if list_of_parents[k]==self.list_of_objects[i].Get_id():
                                    list_of_children.append(self.list_of_objects[j])
                                    break
                    list_of_functions=[]
                    for j in range(0,len(list_of_children)):
                        current_list_of_function=list_of_children[j].Get_list_of_functions()
                        for k in range(0,len(current_list_of_function)):
                            flag_exist=False
                            for l in range(0,len(list_of_functions)):
                                if current_list_of_function[k][2]==list_of_functions[l][0]:
                                    flag_exist=True
                                    list_of_functions[l][1]+=1
                                    break
                            if flag_exist==False:
                                new_func=[]
                                new_func.append(current_list_of_function[k][2])
                                new_func.append(1)
                                list_of_functions.append(new_func)
                    for j in range(0,len(list_of_functions)):
                        if list_of_functions[j][1]==len(list_of_children) and list_of_functions[j][1]!=1:
                            current_string="Рекомендуется вынести функцию '"+list_of_functions[j][0]+"' из классов"
                            for k in range(0,len(list_of_children)):
                                current_string+=" '"+list_of_children[k].Get_name()+"'"
                            current_string+=" в их родителя '"+self.list_of_objects[i].name+"' и сделать её виртуальной"
                            list_of_ids=[self.id]
                            for child in list_of_children:
                                list_of_ids.append(child.id)
                            list_of_ids.append(self.list_of_objects[i].id)
                            self.model.Add_recomendation(current_string,"Детальность модели","Вынос функции в родителя",list_of_ids)
        return
    def __del__(self):
        while len(self.list_of_objects)>0:
            del self.list_of_objects[0]
    #Раздел с паттернами и механизмами
    def Offering_classes_on_frequently_repeated_nouns_in_use_cases(self):
        if self.type=="Use Case":
            for object in self.list_of_objects:
                if object.type=="uml:UseCase":
                    self.Get_nouns_and_verbs_from_words(object)
            list_of_class_diagams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Logical":
                    list_of_class_diagams.append(self.model.Get_diagram(i))
            for i in range(0,len(self.list_of_nouns)):
                if self.list_of_nouns[i][1]>=2:
                    flag_exist=False
                    for j in range(0,len(list_of_class_diagams)):
                        list_of_objects=list_of_class_diagams[j].Get_list_of_objects()
                        for k in range(0,len(list_of_objects)):
                            if list_of_objects[k].Get_name()==self.list_of_nouns[i][0]:
                                flag_exist=True
                                break
                    if flag_exist==False:
                        self.model.Add_recomendation("Рекомендуется создать класс с именем '"+self.list_of_nouns[i][0]+"'","Механизм предложения классов по часто повторяющимся существительным в прецедентах","None",[])
        return
    def Paired_words_in_sequence_diagrams(self):
        if self.type=="Sequence" or self.type=="Use Case":
            for object in self.list_of_objects:
                if object.type=="uml:Message" or object.type=="uml:UseCase":
                    self.Get_nouns_and_verbs_from_words(object)
            list_of_class_diagams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Logical":
                    list_of_class_diagams.append(self.model.Get_diagram(i))
            for i in range(0,len(self.list_of_verbs)):
                current_verb=self.list_of_verbs[i]
                current_sequence_diagram=None
                if self.Get_type()=="Sequence":
                    current_sequence_diagram=self
                else:
                    for j in range(0,len(self.model.Get_list_of_diagrams())):
                        if self.model.Get_diagram(j).Get_name()==current_verb[1]:
                            current_sequence_diagram=self.model.Get_diagram(j)
                            break
                if current_sequence_diagram!=None:
                    current_list_of_recommended_sequence=[]
                    if current_verb[0]=="включить" or current_verb[0]=="выключить":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["включить",False])
                            current_list_of_recommended_sequence.append(["выключить",False])
                        elif current_verb[0]=="включить":
                            current_list_of_recommended_sequence.append(["включить",True])
                            current_list_of_recommended_sequence.append(["выключить",False])
                        else:
                            current_list_of_recommended_sequence.append(["включить",False])
                            current_list_of_recommended_sequence.append(["выключить",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'включить' и 'выключить', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'включить', так как существует системный вызов 'выключить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'выключить', так как существует системный вызов 'включить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'включить' поставить выше системного вызова 'выключить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="октрыть" or current_verb[0]=="закрыть":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["октрыть",False])
                            current_list_of_recommended_sequence.append(["закрыть",False])
                        elif current_verb[0]=="октрыть":
                            current_list_of_recommended_sequence.append(["октрыть",True])
                            current_list_of_recommended_sequence.append(["закрыть",False])
                        else:
                            current_list_of_recommended_sequence.append(["октрыть",False])
                            current_list_of_recommended_sequence.append(["закрыть",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'открыть' и 'закрыть', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'открыть', так как существует системный вызов 'закрыть'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'закрыть', так как существует системный вызов 'открыть'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'открыть' поставить выше системного вызова 'закрыть'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="войти" or current_verb[0]=="выйти":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["войти",False])
                            current_list_of_recommended_sequence.append(["выйти",False])
                        elif current_verb[0]=="войти":
                            current_list_of_recommended_sequence.append(["войти",True])
                            current_list_of_recommended_sequence.append(["выйти",False])
                        else:
                            current_list_of_recommended_sequence.append(["войти",False])
                            current_list_of_recommended_sequence.append(["выйти",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'войти' и 'выйти', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'войти', так как существует системный вызов 'выйти'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'выйти', так как существует системный вызов 'войти' и это может повысить безопасность ситемных взаимодейтсвий в данном сценарии","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'войти' поставить выше системного вызова 'выйти'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="отправить" or current_verb[0]=="получить":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["отправить",False])
                            current_list_of_recommended_sequence.append(["получить",False])
                        elif current_verb[0]=="отправить":
                            current_list_of_recommended_sequence.append(["отправить",True])
                            current_list_of_recommended_sequence.append(["получить",False])
                        else:
                            current_list_of_recommended_sequence.append(["отправить",False])
                            current_list_of_recommended_sequence.append(["получить",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'оптравить' и 'получить', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить парный системный вызов ('оптравить' или 'найти') связанный с системным вызовом 'получить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'получить', так как существует системный вызов 'оптравить', но нет ответа на эту отправку","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'оптравить' поставить выше системного вызова 'получить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="найти" or current_verb[0]=="получить":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["найти",False])
                            current_list_of_recommended_sequence.append(["получить",False])
                        elif current_verb[0]=="найти":
                            current_list_of_recommended_sequence.append(["найти",True])
                            current_list_of_recommended_sequence.append(["получить",False])
                        else:
                            current_list_of_recommended_sequence.append(["найти",False])
                            current_list_of_recommended_sequence.append(["получить",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'найти' и 'получить', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить парный системный вызов ('оптравить' или 'найти') связанный с системным вызовом 'получить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'получить', так как существует системный вызов 'найти', ведь при поиске необходимо получить искомый объект","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'найти' поставить выше системного вызова 'получить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="редактировать":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["найти",False])
                            current_list_of_recommended_sequence.append(["редактировать",False])
                        elif current_verb[0]=="редактировать":
                            current_list_of_recommended_sequence.append(["найти",False])
                            current_list_of_recommended_sequence.append(["редактировать",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'найти' и 'редактировать', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'найти', так как существует системный вызов 'редактировать'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'найти' поставить выше системного вызова 'редактировать'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="начать" or current_verb[0]=="закончить":                    
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["начать",False])
                            current_list_of_recommended_sequence.append(["закончить",False])
                        elif current_verb[0]=="начать":
                            current_list_of_recommended_sequence.append(["начать",True])
                            current_list_of_recommended_sequence.append(["закончить",False])
                        else:
                            current_list_of_recommended_sequence.append(["начать",False])
                            current_list_of_recommended_sequence.append(["закончить",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'начать' и 'закончить', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'начать', так как существует системный вызов 'закончить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'закончить', так как существует системный вызов 'начать'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'начать' поставить выше системного вызова 'закончить'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                    elif current_verb[0]=="скачать" or current_verb[0]=="загрузить":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["select",False])
                            current_list_of_recommended_sequence.append(["скачать",False])
                            current_list_of_recommended_sequence.append(["загрузить",False])
                        elif current_verb[0]=="скачать":
                            current_list_of_recommended_sequence.append(["select",False])
                            current_list_of_recommended_sequence.append(["скачать",True])
                            current_list_of_recommended_sequence.append(["загрузить",False])
                        else:
                            current_list_of_recommended_sequence.append(["select",False])
                            current_list_of_recommended_sequence.append(["скачать",False])
                            current_list_of_recommended_sequence.append(["загрузить",True])
                        current_list_of_sequence_of_current_diagram_sequence=[]
                        for j in range(0,len(current_sequence_diagram.Get_list_of_objects())):
                            if current_sequence_diagram.Get_object(j).Get_type()=="uml:Message":
                                current_list_of_sequence_of_current_diagram_sequence.append(current_sequence_diagram.Get_object(j))
                        begin=-1
                        end=-1
                        for j in range(0,len(current_list_of_sequence_of_current_diagram_sequence)):
                            current_fraze=current_list_of_sequence_of_current_diagram_sequence[j].Get_name().casefold()
                            current_fraze=list(current_fraze)
                            for k in range(0,len(current_fraze)):
                                if current_fraze[k]=="_":
                                    current_fraze[k]=' '
                            current_fraze="".join(current_fraze)
                            if (current_list_of_recommended_sequence[0][0] in current_fraze)==True:
                                begin=j
                                current_list_of_recommended_sequence[0][1]=True
                            elif (current_list_of_recommended_sequence[1][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[1][1]=True
                            elif (current_list_of_recommended_sequence[2][0] in current_fraze)==True:
                                end=j
                                current_list_of_recommended_sequence[2][1]=True
                            if begin!=-1 and end!=-1:
                                break
                        second_sequence=None
                        for j in range(1,len(current_list_of_recommended_sequence)):
                            if current_list_of_recommended_sequence[j][1]==True:
                                if second_sequence==None:
                                    second_sequence=current_list_of_recommended_sequence[j][0]
                                    break 
                        if begin==end:#оба равны -1
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'выбрать' и 'скачать' или 'загрузить', так как их наличие подразумевает само название данной диаграммы","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'выбрать', так как существует системный вызов '"+second_sequence+"'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'скачать' или 'загрузить', так как существует системный вызов 'выбрать'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'выбрать' поставить выше системного вызова '"+second_sequence+"'","Механизм предложения парных глаголов в диаграммах прецеднтов","None",[])
    def GRASP(self):
        if self.type=="Logical":
            for object in self.list_of_objects:
                if object.type=="uml:Class":
                    list_of_params=object.Get_list_of_parametres().copy()
                    j=0
                    while j<len(list_of_params):
                        flag_exist=False
                        for k in range(0,len(self.list_of_objects)):
                            if self.list_of_objects[k].Get_type()=="uml:Class" and self.list_of_objects[k].Get_name()==list_of_params[j][1]:
                                flag_exist=True
                                break
                        if flag_exist==False:
                            if list_of_params[j][2]!=object.Get_name():
                                self.model.Add_recomendation("Рекомендуется создать отдельный класс для типа данных '"+list_of_params[j][2]+"', чтобы увеличить зацепление и обеспечить низкую связность между элементами классами в модели","GRASP","None",[])
                            list_of_params.pop(j)
                        else:
                            j+=1
                    if len(list_of_params)!=0:
                        list_of_functions=object.Get_list_of_functions().copy()
                        for j in range(0,len(list_of_params)):
                            flag_exist=False
                            current_name="Создать "+list_of_params[j][1]
                            for k in range(0,len(list_of_functions)):
                                if list_of_functions[k][2]==current_name:
                                    flag_exist=True
                                    break
                            if flag_exist==False:
                                self.model.Add_recomendation("Рекомендуется в класс '"+object.Get_name()+"' добавить функцию для создания '"+list_of_params[j][1]+"', так как он работает с ними","GRASP","None",[])
                            current_object=None
                            for k in range(0,len(self.list_of_objects)):
                                if self.list_of_objects[k].Get_name()==list_of_params[j][1]:
                                    current_object=self.list_of_objects[k]
                                    break
                            current_objec_list_of_params=current_object.Get_list_of_parametres()
                            flag_exist=False
                            for k in range(0,len(current_objec_list_of_params)):
                                if current_objec_list_of_params[k][1]==object.Get_name():
                                    flag_exist=True
                                    break
                            if flag_exist==True:
                                self.model.Add_recomendation("Рекомендуется создать отдельный класс с классами '"+object.Get_name()+"' и '"+current_object.Get_name()+"', ослабляющий сильную связь между ними (в первом классе есть второй, а во втором - первый) ","GRASP","None",[])
        return

class obj_Class(Object):
    def __init__(self,init_diagram):
        self.diagram=init_diagram
        self.list_of_parametres=[]#[[видимость,тип,имя,кратность,начальное значение],...,[видимость,тип,имя,кратность,начальное значение]]
        self.list_of_functions=[]#[[видимость,тип возвращаемого значения,имя,тип парамерта, имя параметра,тип параемтра, имя параметра],...,[видимость,тип возвращаемого значения,имя,тип парамерта, имя параметра,тип параемтра, имя параметра]]
        self.independent_existence=True#флаг независимого существования
        self.sender_class_id="None"
        self.recipient_class_id="None"
        super().__init__()
        return
    def Add_param(self,new_param):
        self.list_of_parametres.append(new_param)
        return
    def Add_func(self,new_func):
        self.list_of_functions.append(new_func)
        return
    def Set_independent_existence(self,new_independent_existence):
        self.independent_existence=new_independent_existence
        return
    def Set_sender_class_id(self,new_sender_class_id):
        self.sender_class_id=new_sender_class_id
        return
    def Set_recipient_class_id(self,new_recipient_class_id):
        self.recipient_class_id=new_recipient_class_id
        return
    def Change_param(self,number_param,number_of_string,new_string):
        if number_param>len(self.list_of_parametres):
            return None
        else:
            if number_of_string>len(self.list_of_parametres[number_param]):
                return None
            else:
                self.list_of_parametres[number_param][number_of_string]=new_string
        return
    def Change_func(self,number_func,number_of_string,new_string):
        if number_func>len(self.list_of_functions):
            return None
        else:
            if number_of_string>len(self.list_of_functions[number_func]):
                return None
            else:
                self.list_of_functions[number_func][number_of_string]=new_string
        return
    def Get_info_about_param(self,number_of_param):
        if number_of_param>=len(self.list_of_parametres):
            return None
        else:
            return self.list_of_parametres[number_of_param]
    def Get_info_about_func(self,number_of_func):
        if number_of_func>len(self.list_of_functions):
            return None
        else:
            return self.list_of_functions[number_of_func]
    def Get_list_of_parametres(self):
        return self.list_of_parametres
    def Get_list_of_functions(self):
        return self.list_of_functions
    def Get_independent_existence(self):
        return self.independent_existence
    def Get_sender_class_id(self):
        return self.sender_class_id
    def Get_recipient_class_id(self):
        return self.recipient_class_id
    def Parse_class(self,root):
        local_root=root
        help_root=self.diagram.model.extension_root.find("element",attrs={"xmi:idref":local_root["xmi:id"]})
        if help_root!=None:
            if help_root.has_attr("xmi:idref"):
                self.Set_id(help_root["xmi:idref"])
            if help_root.has_attr("xmi:type"):
                self.Set_type(help_root["xmi:type"])
            if help_root.has_attr("name"):
                self.Set_name(help_root["name"])
            self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+" '"+self.name+"' начал читаться из XML файла"]])
            attributes=help_root.find("attributes")
            if attributes!=None:
                attributes=attributes.find_all("attribute")
                if attributes!=None:
                    for attribute in attributes:
                        new_atribute=["None","None","None","None","None"]
                        if attribute.has_attr("scope"):
                            new_atribute[0]=attribute["scope"]
                        if attribute.has_attr("name"):
                            new_atribute[2]=attribute["name"]
                        if attribute.find("properties")!=None and attribute.properties.has_attr("type"):
                            new_atribute[1]=attribute.properties["type"]
                        if attribute.find("initial")!=None and attribute.initial.has_attr("body"):
                            new_atribute[4]=attribute.initial["body"]
                        self.list_of_parametres.append(new_atribute)
            operations=help_root.find("operations")
            if operations!=None:
                operations=operations.find_all("operation")
                if operations!=None:
                    for operation in operations:
                        new_operation=["None","None","None"]
                        if operation.has_attr("scope"):
                            new_operation[0]=operation["scope"]
                        if operation.has_attr("name"):
                            new_operation[2]=operation["name"]
                        if operation.find("type")!=None and operation.type.has_attr("type"):
                            new_operation[1]=operation.type["type"]
                        parameters=operation.find("parameters")
                        if parameters!=None:
                            parameters=parameters.find_all("parameter")
                            if parameters!=None:
                                for parameter in parameters:
                                    if parameter.has_attr("xmi:idref") and local_root.find("ownedParameter",attrs={"xmi:id":parameter["xmi:idref"]}):
                                        properties=parameter.find("properties")
                                        if properties!=None and properties.has_attr("type"):
                                            new_operation.append(properties["type"])
                                        else:
                                            new_operation.append("None")
                                        if local_root.find("ownedParameter",attrs={"xmi:id":parameter["xmi:idref"]}).has_attr("name"):
                                            new_operation.append(local_root.find("ownedParameter",attrs={"xmi:id":parameter["xmi:idref"]})["name"])
                                        else:
                                            new_operation.append("None")
                        self.list_of_functions.append(new_operation)
            extendedProperties=help_root.find("extendedProperties")
            if extendedProperties!=None and extendedProperties.has_attr("conID"):
                connector=self.diagram.model.extension_root.find("connector",attrs={"xmi:idref":extendedProperties["conID"]})
                if connector!=None:
                    source=connector.find("source")
                    if source!=None and source.has_attr("xmi:idref"):
                        self.sender_class_id=source["xmi:idref"]
                    target=connector.find("target")
                    if target!=None and target.has_attr("xmi:idref"):
                        self.recipient_class_id=target["xmi:idref"]
            links=help_root.find("links")
            if links!=None:
                Generalizations=links.find_all("Generalization",attrs={"start":self.id})
                if Generalizations!=None:
                    for Generalization in Generalizations:
                        if Generalization.has_attr("end"):
                            self.parents_id.append(Generalization["end"])               
        for child in local_root:
            if child.name=="nestedClassifier" and child.has_attr("xmi:type") and child["xmi:type"]=="uml:Class":
                new_class=obj_Class(self.diagram)
                new_class.Parse_class(child)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+" '"+self.name+"' прочитан"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+" '"+self.name+"' добавляется в модель"]])
        #print("Type:"+self.type+"|Id:"+self.id)
        self.diagram.Add_object(self)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+" '"+self.name+"' добавлен в модель"]])
        return
    def Change_params_to_correct(self):
        for i in range(0,len(self.list_of_parametres)):
            for j in range(0,len(self.list_of_parametres[i])):
                self.list_of_parametres[i][j]=self.Change_to_correct_type(self.list_of_parametres[i][j])
        for i in range(0,len(self.list_of_functions)):
            for j in range(0,len(self.list_of_functions[i])):
                self.list_of_functions[i][j]=self.Change_to_correct_type(self.list_of_functions[i][j])
        return
    def Change_to_correct_type(self,for_change):
        if for_change[0:7]=="EAJava_":
            return for_change[7:]
        if for_change=="Integer" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#Integer":
            return "int"
        if for_change == "Boolean" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#Boolean":
            return "boolean"
        if for_change=="UnlimitedNatural" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#UnlimitedNatural":
            return "string"
        if for_change=="EAnone_void" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#String":
            return "void"
        return for_change
    def Delete_param(self,number_of_param):
        if number_of_param<0 or number_of_param>len(self.list_of_parametres):
            return None
        del self.list_of_parametres[number_of_param]

class obj_Connection(Object):
    def __init__(self,init_diagram):
        self.diagram=init_diagram
        self.sender_class_id="None"
        self.recipient_class_id="None"
        self.multiplicity_of_sender_class="None"
        self.multiplicity_of_recipient_class="None"
        self.role_sender="None"
        self.role_recipient="None"
        self.flag_composite=False#флаг композиции
        self.flag_shared=False#флаг агрегации
        super().__init__()
        return
    def Set_sender_class_id(self,new_sender_class_id):
        self.sender_class_id=new_sender_class_id
        return
    def Set_recipient_class_id(self,new_recipient_class_id):
        self.recipient_class_id=new_recipient_class_id
        return
    def Set_role_sender(self,new_role_sender):
        self.role_sender=new_role_sender
        return
    def Set_role_recipient(self,new_role_recipient):
        self.role_recipient=new_role_recipient
        return
    def Set_flag_composite(self,new_flag_composite):
        self.flag_composite=new_flag_composite
        return
    def Set_flag_shared(self,new_flag_shared):
        self.flag_shared=new_flag_shared
        return
    def Get_sender_class_id(self):
        return self.sender_class_id
    def Get_recipient_class_id(self):
        return self.recipient_class_id
    def Get_multiplicity_of_sender_class(self):
        return self.multiplicity_of_sender_class
    def Get_multiplicity_of_recipient_class(self):
        return self.multiplicity_of_recipient_class
    def Get_role_sender(self):
        return self.role_sender
    def Get_role_recipient(self):
        return self.role_recipient
    def Get_flag_composite(self):
        return self.flag_composite
    def Get_flag_shared(self):
        return self.flag_shared
    def Parse_connection(self,root):
        #???разобраться со всеми видами соединений
        local_root=root
        if local_root.has_attr("xmi:id"):
            self.Set_id(local_root["xmi:id"])
        if local_root.has_attr("xmi:type"):
            self.Set_type(local_root["xmi:type"])
        if local_root.has_attr("name"):
            self.Set_name(local_root["name"])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.name+"' начал читаться из XML файла"]])
        help_root=self.diagram.model.extension_root.find("connector",attrs={"xmi:idref":self.id})
        if help_root!=None:
            sender_root=help_root.find("source")
            if sender_root!=None:
                if sender_root.has_attr("xmi:idref"):
                    self.sender_class_id=sender_root["xmi:idref"]
                else:
                    self.sender_class_id="None"
                type=sender_root.find("type")
                if type!=None:
                    if type.has_attr("multiplicity"):
                        self.multiplicity_of_sender_class=type["multiplicity"]
                role=sender_root.find("role")
                if role!=None:
                    if role.has_attr("name"):
                        self.role_sender=role["name"]
            recipient_root=help_root.find("target")
            if recipient_root!=None:
                if recipient_root.has_attr("xmi:idref"):
                    self.recipient_class_id=recipient_root["xmi:idref"]
                else:
                    self.recipient_class_id="None"
                type=recipient_root.find("type")
                if type!=None:
                    if type.has_attr("multiplicity"):
                        self.multiplicity_of_recipient_class=type["multiplicity"]
                    if type.has_attr("aggregation"):
                        if type["aggregation"]=="composite":
                            self.flag_composite=True
                        elif type["aggregation"]=="shared":
                            self.flag_shared=True
                role=recipient_root.find("role")
                if role!=None:
                    if role.has_attr("name"):
                        self.role_recipient=role["name"]
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.name+"' прочитан"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.name+"' добавляется в модель"]])
        self.diagram.Add_object(self)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.name+"' добавлен в модель"]])
        return
    
class obj_Use_Case(Object):
    def __init__(self,init_diagram):
        self.diagram=init_diagram
        self.list_of_actors=[]
        self.list_of_includions=[]#what is included in this Use Case (required)
        self.list_of_extentions=[]#what extends this Use Case (optional, but possible)
        super().__init__()
        return
    def Add_actor(self,new_actor):
        self.list_of_actors.append(new_actor)
        return
    def Change_actor(self,number_of_actor,changed_actor):
        if number_of_actor<0 or (number_of_actor-1)>len(self.list_of_actors):
            return None
        else:
            self.list_of_actors[number_of_actor]=changed_actor
        return
    def Get_info_about_actor(self,number_of_actor):
        if number_of_actor<0 or (number_of_actor-1)>len(self.list_of_actors):
            return None
        else:
            return self.list_of_actors[number_of_actor]
    def Get_list_of_actors(self):
        return self.list_of_actors
    def Add_includion(self,new_includion):
        self.list_of_includions.append(new_includion)
        return
    def Change_includion(self,number_of_includion,changed_includion):
        if number_of_includion<0 or (number_of_includion-1)>len(self.list_of_includions):
            return None
        else:
            self.list_of_includions[number_of_includion]=changed_includion
        return
    def Get_info_about_includion(self,number_of_includion):
        if number_of_includion<0 or (number_of_includion-1)>len(self.list_of_includions):
            return None
        else:
            return self.list_of_includions[number_of_includion]
    def Get_list_of_includions(self):
        return self.list_of_includions
    def Add_extention(self,new_extention):
        self.list_of_extentions.append(new_extention)
        return
    def Change_extention(self,number_of_extention,changed_extention):
        if number_of_extention<0 or (number_of_extention-1)>len(self.list_of_extentions):
            return None
        else:
            self.list_of_extentions[number_of_extention]=changed_extention
        return
    def Get_info_about_extention(self,number_of_extention):
        if number_of_extention<0 or (number_of_extention-1)>len(self.list_of_extentions):
            return None
        else:
            return self.list_of_extentions[number_of_extention]
    def Get_list_of_extentions(self):
        return self.list_of_extentions
    def Delete_extention(self,number_of_extention):
        if number_of_extention<0 or (number_of_extention-1)>len(self.list_of_extentions):
            return None
        else:
            del self.list_of_extentions[number_of_extention]
        return
    def Parse_use_case(self,root):
        local_root=root
        help_root=None
        if local_root.has_attr("xmi:id"):
            self.id=local_root["xmi:id"]
            help_root=self.diagram.model.extension_root.find("element",attrs={"xmi:idref":local_root["xmi:id"]})
            if help_root!=None:
                if help_root.has_attr("name"):
                    self.name=help_root["name"]
                if help_root.has_attr("xmi:type"):
                    self.type=help_root["xmi:type"]
                links=help_root.find("links")
                if links!=None:
                    Generalizations=links.find_all("Generalization")
                    if Generalizations!=None:
                        for Generalization in Generalizations:
                            if Generalization.has_attr("start") and help_root.has_attr("xmi:idref") and Generalization["start"]==help_root["xmi:idref"] and Generalization.has_attr("end"):
                                self.Add_parents(Generalization["end"])
                    UseCases=help_root.find_all("UseCase")
                    if UseCases!=None:
                        for UseCase in UseCases:
                            if UseCase.has_attr("xmi:id") and UseCase.has_attr("end") and UseCase["end"]==self.id:
                                connector=self.diagram.model.extension_root.find("connector",attrs={"xmi:idref":UseCase["xmi:id"]})
                                if connector!=None:
                                    properties=connector.find("properties")
                                    if properties!=None and properties.has_attr("stereotype") and properties["stereotype"]=="extend":
                                        if connector.find("source") and connector.source.has_attr("xmi:idref"):
                                            new_extention=[]
                                            new_extention.append(connector.source["xmi:idref"])
                                            node=self.diagram.model.model_root.find("annotatedElement",attrs={"xmi:idref":connector["xmi:idref"]})
                                            if node!=None:
                                                node=node.parent
                                                if node.has_attr("body"):
                                                    result=re.findall("([^ \|]{1}[^\|]*[^ \|]{1})",node["body"])
                                                    for i in range(0,len(result)):
                                                        result[i]=result[i].replace("&amp;","&")
                                                        result[i]=result[i].replace("&gt;",">")
                                                        result[i]=result[i].replace("&lt;","<")
                                                    new_extention.append(result)
                                            self.Add_extention(new_extention)
                            elif UseCase.has_attr("xmi:id") and UseCase.has_attr("start") and UseCase["start"]==self.id:
                                connector=self.diagram.model.extension_root.find("connector",attrs={"xmi:idref":UseCase["xmi:id"]})
                                if connector!=None:
                                    properties=connector.find("properties")
                                    if properties!=None and properties.has_attr("stereotype") and properties["stereotype"]=="include":
                                        if connector.find("target") and connector.target.has_attr("xmi:idref"):
                                            self.Add_includion(connector.target["xmi:idref"])
                    Associations=help_root.find_all("Association")
                    if Associations!=None:
                        for Association in Associations:
                            connected_object_id=None
                            if Association.has_attr("start") and Association["start"]!=self.id:
                                connected_object_id=Association["start"]
                            elif Association.has_attr("end") and Association["end"]!=self.id:
                                connected_object_id=Association["end"]
                            if connected_object_id!=None and self.diagram.model.extension_root.find("element",attrs={"xmi:idref":connected_object_id,"xmi:type":"uml:Actor"}):
                                self.Add_actor(connected_object_id)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' начал читаться из XML файла"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' прочитан"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавляется в модель"]])
        self.diagram.Add_object(self)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавлен в модель"]])
        return

class obj_LifeLine(Object):
    def __init__(self,init_diagram):
        self.diagram=init_diagram
        self.connected_object_id="None"
        super().__init__()
        return
    def Set_connected_object_id(self,new_connected_object_id):
        self.connected_object_id=new_connected_object_id
        return
    def Get_connected_object_id(self):
        return self.connected_object_id
    def Parse_LifeLine(self,root):
        local_root=root
        if local_root.has_attr("xmi:id"):
            self.id=local_root["xmi:id"]
        if local_root.has_attr("xmi:type"):
            self.type=local_root["xmi:type"]
        if local_root.has_attr("name"):
            self.name=local_root["name"]
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' начал читаться из XML файла"]])
        if local_root.has_attr("represents"):
            represents=local_root["represents"]
            represents=self.diagram.model.model_root.find("ownedAttribute",attrs={"xmi:id":represents})
            if represents!=None and represents.find("type")!=None and represents.type.has_attr("xmi:idref"):
                    self.connected_object_id=represents.type["xmi:idref"]
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' прочитан"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавляется в модель"]])
        self.diagram.Add_object(self)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавлен в модель"]])
        
class obj_Message(Object):
    def __init__(self,init_diagram):
        self.diagram=init_diagram
        self.id_point_from="None"
        self.id_point_to="None"
        self.type_connection="None"
        self.kind_connection="None"
        super().__init__()
        return
    def Set_id_point_from(self,new_id_point_from):
        self.id_point_from=new_id_point_from
        return
    def Get_id_point_from(self):
        return self.id_point_from
    def Set_id_point_to(self,new_id_point_to):
        self.id_point_to=new_id_point_to
        return
    def Get_id_point_to(self):
        return self.id_point_to
    def Set_type_connection(self,new_type_connection):
        self.type_connection=new_type_connection
        return
    def Get_type_connection(self):
        return self.type_connection
    def Set_kind_connection(self,new_kind_connection):
        self.kind_connection=new_kind_connection
        return
    def Get_kind_connection(self):
        return self.kind_connection
    def Parse_Message(self,root):
        local_root=root
        if local_root.has_attr("name"):
            self.name=local_root["name"]
        if local_root.has_attr("xmi:type"):
            self.type=local_root["xmi:type"]
        if local_root.has_attr("xmi:id"):
            self.id=local_root["xmi:id"]
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' начал читаться из XML файла"]])
        if local_root.has_attr("sendEvent"):
            fragment=self.diagram.model.model_root.find("fragment",attrs={"xmi:id":local_root["sendEvent"]})
            if fragment!=None and fragment.has_attr("covered"):
                smth=self.diagram.model.model_root.find(attrs={"xmi:id":fragment["covered"]})
                if smth!=None:
                    self.id_point_from=smth["xmi:id"]
                else:
                    self.id_point_from=local_root["sendEvent"]
            else:
                self.id_point_from=local_root["sendEvent"]
        if local_root.has_attr("receiveEvent"):
            fragment=self.diagram.model.model_root.find("fragment",attrs={"xmi:id":local_root["receiveEvent"]})
            if fragment!=None:
                smth=self.diagram.model.model_root.find(attrs={"xmi:id":fragment["covered"]})
                if smth!=None:
                    self.id_point_to=smth["xmi:id"]
                else:
                    self.id_point_to=local_root["receiveEvent"]
            else:
                self.id_point_to=local_root["receiveEvent"]
        if local_root.has_attr("messageKind"):
            self.kind_connection=local_root["messageKind"]
        if local_root.has_attr("messageSort"):
            self.type_connection=local_root["messageSort"]
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' прочитан"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавляется в модель"]])
        self.diagram.Add_object(self)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавлен в модель"]])
        return

class obj_Alternative(Object):
    def __init__(self,init_diagram):
        self.diagram=init_diagram
        self.type_alternative="None"
        self.list_of_covered_lifeline=[]
        self.list_of_alternatives=[]
        super().__init__()
        return
    def Set_type_alternative(self,new_type_alternative):
        self.type_alternative=new_type_alternative
        return
    def Get_type_alternative(self):
        return self.type_alternative
    def Add_covered_lifeline(self,new_covered_lifeline):
        self.list_of_covered_lifeline.append(new_covered_lifeline)
        return
    def Get_list_of_covered_lifeline(self):
        return self.list_of_covered_lifeline
    def Get_covered_lifeline(self,number_covered_lifeline):
        if number_covered_lifeline<0 or (number_covered_lifeline-1)>len(self.list_of_covered_lifeline):
            return None
        else:
            return self.list_of_covered_lifeline[number_covered_lifeline]
    def Add_alternative(self,new_alternative):
        self.list_of_alternatives.append(new_alternative)
        return
    def Get_list_of_alternatives(self):
        return self.list_of_alternatives
    def Get_alternative(self,number_of_alternative):
        if number_of_alternative<0 or (number_of_alternative-1)>len(self.list_of_alternatives):
            return None
        else:
            return self.list_of_alternatives[number_of_alternative]
    def Parse_alternative(self,root):
        local_root=root
        if local_root.has_attr("xmi:id"):
            self.id=local_root["xmi:id"]
        if local_root.has_attr("xmi:type"):
            self.type=local_root["xmi:type"]
        if local_root.has_attr("name"):
            self.name=local_root["name"]
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' начал читаться из XML файла"]])
        if local_root.has_attr("interactionOperator"):
            self.type_alternative=local_root["interactionOperator"]
        for child in local_root.children:
            #if child.name=="covered":
            #    self.Add_covered_lifeline(child["xmi:idref"])
            if child.name=="operand":
                new_alernative_variavnt=[]
                for elements in child.children:
                    if elements.name=="guard":
                        if elements.contents[1].has_attr("body"):
                            new_alernative_variavnt.append(elements.contents[1]["body"])
                    elif elements.name=="fragment":
                        new_alernative_variavnt.append(elements["covered"])
                if len(new_alernative_variavnt)!=0:
                    self.Add_alternative(new_alernative_variavnt)
        for alterntive in self.list_of_alternatives:
            for i in range(1,len(alterntive)):
                flag_exist=False
                for lifeline_id in self.list_of_covered_lifeline:
                    if lifeline_id==alterntive[i]:
                        flag_exist=True
                        break
                if flag_exist==False:
                    self.list_of_covered_lifeline.append(alterntive[i])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' прочитан"]])
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавляется в модель"]])
        self.diagram.Add_object(self)
        self.diagram.model.controller.AddCommand(["Visual",["Трассировка парсинга",self.type+"'"+self.name+"' добавлен в модель"]])
        print(self.list_of_alternatives)
        return

controller=controller()