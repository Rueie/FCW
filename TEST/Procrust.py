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
predictor = RNNMorphPredictor(language="en")

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
        self.number_of_login_windows=0
        self.number_of_opened_frames=3
        self.current_window=None
        self.current_widget=None
        
        self.controller=init_controller
        self.list_of_commands=[]
        self.thread1=Thread(target=self.Start,args=())
        self.thread1.start()
        
        self.number_rows_in_string_in_tree=1
        return
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

        self.result_page_commetns_tracert=Text(self.result_page_frame_result,font="Times 11",wrap="word",height=math.floor(self.main_window.winfo_screenheight()/3/14))
        self.result_page_commetns_tracert.pack(side=LEFT,expand=True,fill="both")
        self.font_for_groups=font.Font(family="Times",size=14,weight="bold",slant="italic",underline=True)
        self.result_page_commetns_tracert.tag_configure("Раздел",font=self.font_for_groups)

        self.result_page_commetns_tracert_ver_srollbar=Scrollbar(self.result_page_frame_result,orient="vertical",command=self.result_page_commetns_tracert.yview)
        self.result_page_commetns_tracert_ver_srollbar.pack(side=RIGHT,anchor=E,fill="y")
        self.result_page_commetns_tracert["yscrollcommand"] = self.result_page_commetns_tracert_ver_srollbar.set
        
        self.result_page_frame_tracert=Frame(self.result_page,height=math.floor(self.main_window.winfo_screenheight()/4),width=self.main_window.winfo_screenwidth())
        self.result_page_frame_tracert.pack(anchor=CENTER)
        self.result_page_frame_tracert.pack_propagate(False)

        self.result_page_label2=Label(self.result_page_frame_tracert,text="Трассировка работы:")
        self.result_page_label2.pack(anchor=NW)

        self.result_page_job_tracert=Text(self.result_page_frame_tracert)
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
            self.list_of_commands.pop(0)
        self.main_window.after(10,self.CheckCommands)
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
        self.result_page_commetns_tracert["state"]="normal"
        for group in list_of_recomendations:
            self.result_page_commetns_tracert.insert(END,group[0]+":\n","Раздел")
            for recomendation in group[1]:
                self.result_page_commetns_tracert.insert(END,"-->"+recomendation+"\n")
        self.result_page_commetns_tracert["state"]="disabled"
        return
    def LogIn(self):
        if self.number_of_login_windows==0:
            self.number_of_login_windows+=1
            self.exit_button['state']='disable'
            
            login_window=Tk()
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

            self.current_window=login_window
            self.current_widget=login_window_entry_password
    def LogOut(self):
        self.current_window.destroy()
        self.number_of_login_windows=0
        self.current_window=0
        self.exit_button['state']='normal'
    def ExitProrust(self):
        self.controller.AddCommand(["Закончить работу"])
        if self.number_of_login_windows==1:
            self.LogOut()
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
        self.result_page_commetns_tracert.delete('1.0',END)
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
                while True:
                    line=xml_file.readline()
                    check_format=""
                    for i in range(0,len(line)):
                        if line[i]==' ':
                            break
                        else:
                            check_format+=line[i]
                    if check_format=="	<xmi:Extension":
                        break
                    else:
                        self.files_page_text_from_file.insert(END,line)
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
        self.result_page_commetns_tracert.delete('1.0',END)
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
    id=""
    type=""
    name=""
    parents_id=[]#A list of strings
    def __init__(self):
        self.id=""
        self.type=""
        self.name=""
        self.parents_id=[]
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
        self.controller=init_controller
        self.list_of_commands=[]
        self.list_of_diagrams=[]#List of obj_Diagram type objects
        self.list_of_recomendations=[]#[[группа замечаний,[рекомендации и замечания]],...,[группа замечаний,[рекомендации и замечания]]]
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
    def Add_recomendation(self,new_recomendation,group_of_recommendation):
        flag_exist=False
        curr_group=None
        for group in self.list_of_recomendations:
            if group[0]==group_of_recommendation:
                flag_exist=True
                curr_group=group
                break
        if flag_exist==True:
            flag_exist=False
            for recomendation in curr_group[1]:
                if recomendation==new_recomendation:
                    flag_exist=True
                    break
            if flag_exist==False:
                curr_group[1].append(new_recomendation)
        else:
            new_group=[group_of_recommendation,[]]
            new_group[1].append(new_recomendation)
            self.list_of_recomendations.append(new_group)
    def Get_recomendation(self,number_of_recomendation):
        if number_of_recomendation<0 or number_of_recomendation>=len(self.list_of_recomendations):
            return None
        else:
            return self.list_of_recomendations[number_of_recomendation]
    def Get_list_of_recomendations(self):
        return self.list_of_recomendations
    def Parse_Model(self,path_of_xml_file):
        self.controller.AddCommand(["Visual","Начался процесс чтения и анализа модели"])
        with open(path_of_xml_file,encoding= 'unicode_escape') as fp:
            root=BeautifulSoup(fp,features="lxml")
        local_root=root
        for child in local_root.descendants:
            if child.name=="packagedelement":
                local_root=child
                break
        self.Set_name(local_root["name"])
        counter=1
        for child in local_root.children:
            if child!='\n':
                counter+=1
                our_diagram=obj_Diagram(self)
                our_diagram.Set_name(child["name"])
                self.controller.AddCommand(["Visual",["Информация о процессе 1","Идёт чтение диаграммы <"+our_diagram.Get_name()+">","Обычный"]])
                self.controller.AddCommand(["Visual",["Состояние прогресса",counter,100]])
                our_diagram.Parse_diaram(child)
                self.Add_diagram(our_diagram)
                del our_diagram
        self.Completion_of_the_Model_formation()
        self.controller.AddCommand(["Visual",["Информация о процессе 1","Завершено чтение и формирование представления модели <"+self.Get_name()+">","Финальный"]])
        self.Search_for_recommendations()
        #print("Закончили парсинг модели")
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
                if our_list_of_objects[i].Get_type()=="uml:Class" or our_list_of_objects[i].Get_type()=="uml:Component" or our_list_of_objects[i].Get_type()=="uml:Interface" or our_list_of_objects[i].Get_type()=="uml:AssociationClass":
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
                        func_mess=[]
                        func_mess.append("Функции")
                        data_func_mess=[]
                        for j in range(0,len(our_funcs)):
                            data_func_mess.clear()
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
                                    data_params_mess.clear()
                                    data_params_mess.append(our_funcs[j][l+1])
                                    data_params_mess.append("Тип параметра: "+our_funcs[j][l])
                                params_mess.append(data_params_mess)
                                data_curr_func_mess.append(params_mess)
                            curr_func_mess.append(data_curr_func_mess)
                            data_func_mess.append(curr_func_mess)
                        func_mess.append(data_func_mess)
                        data_object_mess.append(func_mess)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
                if our_list_of_objects[i].Get_type()=="uml:Association" or our_list_of_objects[i].Get_type()=="uml:Composition" or our_list_of_objects[i].Get_type()=="uml:Aggregation" or our_list_of_objects[i].Get_type()=="uml:Dependency" or our_list_of_objects[i].Get_type()=="uml:Realization":
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
                    current_string+=our_list_of_objects[i].Take_type_string_from_type_number(our_list_of_objects[i].Get_type_of_the_number_of_sender_class())
                    data_object_mess.append(current_string)
                    data_object_mess.append("ID получателя: "+our_list_of_objects[i].Get_recipient_class_id()+"("+str(self.Find_object_in_Model(our_list_of_objects[i].Get_recipient_class_id()).Get_name())+")")
                    data_object_mess.append("Роль получателя: "+our_list_of_objects[i].Get_role_recipient())
                    current_string="Кратность получателя: "
                    current_string+=our_list_of_objects[i].Take_type_string_from_type_number(our_list_of_objects[i].Get_type_of_the_number_of_recipient_class())
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
                if our_list_of_objects[i].Get_type()=="System boundary":
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
                    data_object_mess.append("ID временной линии, вызывающей данную процедуру: "+our_list_of_objects[i].Get_id_point_from()+"("+self.Find_object_in_Model(our_list_of_objects[i].Get_id_point_from()).Get_name()+")")
                    data_object_mess.append("ID временной линии, в которой вызывается данная процедура: "+our_list_of_objects[i].Get_id_point_to()+"("+self.Find_object_in_Model(our_list_of_objects[i].Get_id_point_to()).Get_name()+")")
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
                        data_livelines_data.append("ID временной линии: "+our_list_covered_lifelines[j]+"("+self.Find_object_in_Model(our_list_covered_lifelines[j]).Get_name()+")")
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
                            data_curr_alternative.append("ID временной линии, которая вызывает данную процедуру: "+our_list_of_alternatives[j][1]+"("+self.Find_object_in_Model(our_list_of_alternatives[j][1]).Get_name()+")")
                            data_curr_alternative.append("ID временной линии, в которой вызывается данная процедура: "+our_list_of_alternatives[j][2]+"("+self.Find_object_in_Model(our_list_of_alternatives[j][2]).Get_name()+")")
                        curr_alternative.append(data_curr_alternative)
                        data_alternatives_mess.append(curr_alternative)
                    alternatives_mess.append(data_alternatives_mess)
                    data_object_mess.append(alternatives_mess)
                    object_mess.append(data_object_mess)
                    data_diagram_mess.append(object_mess)
            diagram_mess.append(data_diagram_mess)
            data_mess.append(diagram_mess)
        mess.append(data_mess)
        self.controller.AddCommand(["Visual",["Модель",mess]])
    def SendRecommenadions(self):
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
            if self.list_of_diagrams[i].Get_type()=="Class diagram":
                flag_class=True
            elif self.list_of_diagrams[i].Get_type()=="Use Case diagram":
                flag_use_case=True
            elif self.list_of_diagrams[i].Get_type()=="Sequence diagram":
                flag_sequnce=True
            if flag_class==True and flag_use_case==True and flag_sequnce==True:
                break
        if flag_class==False:
            self.Add_recomendation("В модели нет диаграмм классов, из-за чего невозможно поддерживать полноту модели и её детальность","Полнота модели")
        if flag_use_case==False:
            self.Add_recomendation("В модели нет диаграмм прецедентов, из-за чего нет возможности получить данные о взаимодействиях в системе и актеров, которые влияют на систему","Полнота модели")
        if flag_sequnce==False:
            self.Add_recomendation("В модели нет диаграмм ситемных взаимодействий, из-за чего нет возможности детализировать существующие диаграммы классов","Полнота модели")
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
        file_with_comm=open(file_path_with_prom_comments,"w")
        for group in self.list_of_recomendations:
            for recommendation in group[1]:
                list_of_objects=re.findall('\'[\d\w ]*\'',recommendation)
                new_string=group[0]+"/"+recommendation+"/?!#"
                for object in list_of_objects:
                    new_string+=object+","
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
                    new_file=open(file_path_with_params+str(1),"w")
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
            if diagram.Get_type()=="Use Case diagram":
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
            curr_list_of_obj=re.findall("'([ _a-zA-Z0-9'^]*)'",curr_list_of_obj)
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
        #for group in old_list_of_comments:
            #print(group)
        #print("_______________________________________________________________")
        for group in self.list_of_recomendations:
            if group[0]!=this_name_of_group_recomendation:
                for recomendation in group[1]:
                    flag_exist=False
                    for objects_group in old_list_of_comments:
                        for comments in  objects_group[1]:
                            if recomendation==comments[0]:
                                flag_exist=True
                                break
                        if flag_exist==True:
                            break
                    if flag_exist==True:
                        new_list_of_objects=re.findall("'([ _a-zA-Z0-9'^]*)'",recomendation)
                        #print(new_list_of_objects)
                        list_of_group_objects=[]#[имя лбъекта, список старых замечаний с этим именем объект, список старых замечаний с этим именем объекта]
                        for object in new_list_of_objects:
                            list_of_group_objects.append([object,[]])
                            flag_exist=False
                            for objects_group in old_list_of_comments:
                                if objects_group[0]==object:
                                    for elem in objects_group[1]:
                                        if elem[1]!=this_name_of_group_recomendation:
                                            list_of_group_objects[-1][-1].append(elem[0])
                                    flag_exist=True
                                    break
                            if flag_exist==False:
                                list_of_group_objects[-1].append([])
                            list_of_group_objects[-1].append([])
                            #print("Текущие предложения:",self.list_of_recomendations)
                            for curr_group in self.list_of_recomendations:
                                #print(curr_group[0])
                                if curr_group[0]!=this_name_of_group_recomendation:
                                    for curr_recomendation in curr_group[1]:
                                        curr_objects_list=re.findall("'([ _a-zA-Z0-9'^]*)'",curr_recomendation)
                                        for curr_objects in curr_objects_list:
                                           #t(curr_objects,"?",object)
                                            if curr_objects==object:
                                                list_of_group_objects[-1][-1].append(curr_recomendation)
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
                                self.Add_recomendation("Предложенная рекоммендация:<"+recomendation+">была проигнорирована, в дальнейшем возможны конфликты и ошибки",this_name_of_group_recomendation)
                        if count_new>count_old:
                            self.Add_recomendation("Предложенная рекоммендация:<"+recomendation+">была проигнорирована, обратите внимание, что возникли новые рекомендации, связанные с данным объектом или диаграммой",this_name_of_group_recomendation)
        self.controller.AddCommand(["Visual",["Состояние прогресса",1,1]])
        return

class obj_Diagram(Object):
    list_of_objects=[]
    model=None
    list_of_nouns=[]#[[сущевтвительное,число повторений существительного],...,[сущевтвительное,число повторений существительного]]
    list_of_verbs=[]#[[глагол,имя объекта-родителя этого глагола],...,[глагол,имя объекта-родителя этого глагола]]
    def __init__(self,init_model):
        self.list_of_objects=[]
        self.model=init_model
        self.list_of_nouns=[]
        self.list_of_verbs=[]
        self.model.Find_object_in_Model
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
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_id()==object_id:
                return self.list_of_objects[i]
        return None
    def Define_the_diagram_type(self):
        list_of_types=[]
        flag_unic=True
        for i in range(0,len(self.list_of_objects)):
            for j in range(0,len(list_of_types)):
                if list_of_types[j]==self.list_of_objects[i].Get_type():
                    flag_unic=False
            if flag_unic==True:
                list_of_types.append(self.list_of_objects[i].Get_type())
            flag_unic=True
        flag_actor=False
        flag_use_case=False
        flag_life_line=False
        for i in range(0,len(list_of_types)):
            if list_of_types[i]=="uml:UseCase":
                flag_use_case=True
            if list_of_types[i]=="uml:Actor":
                flag_actor==True
            if list_of_types[i]=="uml:Lifeline":
                flag_life_line=True
        if len(self.list_of_objects)==0:
            list_of_use_case=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                current_list_of_objects=self.model.Get_diagram(i).Get_list_of_objects()
                for j in range(0,len(current_list_of_objects)):
                    if current_list_of_objects[j].Get_type()=="uml:UseCase":
                        list_of_use_case.append(current_list_of_objects[j])
            for i in range(0,len(list_of_use_case)):
                if list_of_use_case[i].Get_name()==self.name:
                    flag_life_line=True
        if flag_life_line==True:
            self.Set_type("Sequence diagram")
        elif flag_use_case==True:
            self.Set_type("Use Case diagram")
        elif flag_actor==False:
            self.Set_type("Class diagram")
        else:
            self.Set_type("Use Case diagram")
        return
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
            if j<(len(words)-1) and ((words[j].normal_form.casefold()=="turn" and words[j+1].normal_form.casefold()=="on") or (words[j].normal_form.casefold()=="switch" and words[j+1].normal_form.casefold()=="off") or (words[j].normal_form.casefold()=="log" and words[j+1].normal_form.casefold()=="in") or (words[j].normal_form.casefold()=="log" and words[j+1].normal_form.casefold()=="out")):
                current_fraze=words[j].normal_form.casefold()+" "+words[j+1].normal_form.casefold()
                flag_exist=False
                for k in range(0,len(self.list_of_verbs)):
                    if current_fraze==self.list_of_verbs[k]:
                        flag_exist=True
                        break
                if flag_exist==False:
                    new_verb=[]
                    new_verb.append(current_fraze)
                    new_verb.append(object.Get_name())
                    self.list_of_verbs.append(new_verb)
            elif words[j].normal_form.casefold()=="open" or words[j].normal_form.casefold()=="close" or words[j].normal_form.casefold()=="send" or words[j].normal_form.casefold()=="recieve" or words[j].normal_form.casefold()=="find" or words[j].normal_form.casefold()=="edit" or words[j].normal_form.casefold()=="start" or words[j].normal_form.casefold()=="finish" or words[j].normal_form.casefold()=="download" or words[j].normal_form.casefold()=="upload" or words[j].normal_form.casefold()=="select":
                flag_exist=False
                for k in range(0,len(self.list_of_verbs)):
                    if words[j].normal_form.casefold()==self.list_of_verbs[k]:
                        flag_exist=True
                        break
                if flag_exist==False:
                    new_verb=[]
                    new_verb.append(words[j].normal_form.casefold())
                    new_verb.append(object.Get_name())
                    self.list_of_verbs.append(new_verb)
            elif words[j].pos=="VERB":
                flag_exist=False
                for k in range(0,len(self.list_of_verbs)):
                    if self.list_of_verbs[k]==words[j].normal_form:
                        flag_exist=True
                        break
                if flag_exist==False:
                    new_verb=[]
                    new_verb.append(words[j].normal_form.casefold())
                    new_verb.append(object.Get_name())
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
        for child in local_root.descendants:
            if child!="\n":
                if child.name=="xmi:Extension":
                    break
                elif child.name=="packagedelement" or child.name=="nestedclassifier" or child.name=="lifeline" or child.name=="message" or child.name=="fragment" or child.name=="ownedattribute" or child.name=="ownedcomment":
                    if child["xmi:type"]=="uml:Class" or child["xmi:type"]=="uml:Component" or child["xmi:type"]=="uml:Interface" or child["xmi:type"]=="uml:AssociationClass":
                        new_obj_class=obj_Class()
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+" '"+child["name"]+"' начал читаться из XML файла"]])
                        new_obj_class.Set_id(child["xmi:id"])
                        new_obj_class.Set_name(child["name"])
                        new_obj_class.Set_type(child["xmi:type"])
                        new_obj_class.Parse_class(child)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+" '"+child["name"]+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+" '"+child["name"]+"' добавляется в модель"]])
                        self.Add_object(new_obj_class)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+" '"+child["name"]+"' добавлен в модель"]])
                        del new_obj_class
                    if child["xmi:type"]=="uml:Association":
                        tracert_string="Association '"+child["xmi:id"]
                        if child.has_attr("name"):
                            tracert_string+="("+child["name"]+")"
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",tracert_string+"' начал читаться из XML файла"]])
                        new_obj_connection=obj_Connection()
                        new_obj_connection.Set_id(child["xmi:id"])
                        if child.has_attr("name"):
                            new_obj_connection.Set_name(child["name"])
                        else:
                            new_obj_connection.Set_name("None")
                        new_obj_connection.Set_type(child["xmi:type"])
                        new_obj_connection.Parse_connection(child)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",tracert_string+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",tracert_string+"' добавляется в модель"]])
                        self.Add_object(new_obj_connection)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",tracert_string+"' добавлен в модель"]])
                        del new_obj_connection
                    if child["xmi:type"]=="uml:UseCase":
                        new_use_case=obj_Use_Case()
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' начал читаться из XML файла"]])
                        new_use_case.Set_id(child["xmi:id"])
                        new_use_case.Set_name(child["name"])
                        new_use_case.Set_type(child["xmi:type"])
                        new_use_case.Parse_use_case(child)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавляется в модель"]])
                        self.Add_object(new_use_case)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавлен в модель"]])
                        del new_use_case
                    if child["xmi:type"]=="uml:Actor":
                        new_actor=Object()
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' начал читаться из XML файла"]])
                        new_actor.Set_name(child["name"])
                        new_actor.Set_id(child["xmi:id"])
                        new_actor.Set_type(child["xmi:type"])
                        if len(child.contents)!=0:
                           for i in range(0,len(child.contents)):
                            if child.contents[i].name=="generalization":
                                new_actor.Add_parents(child.contents[i]["general"])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавляется в модель"]])
                        self.Add_object(new_actor)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавлен в модель"]])
                        del new_actor
                    if child["xmi:type"]=="uml:Lifeline":
                        new_obj_lifeLine=obj_LifeLine()
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' начал читаться из XML файла"]])
                        new_obj_lifeLine.Set_id(child["xmi:id"])
                        new_obj_lifeLine.Set_type(child["xmi:type"])
                        new_obj_lifeLine.Set_name(child["name"])
                        new_obj_lifeLine.Set_connected_object_id(child["represents"])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавляется в модель"]])
                        self.Add_object(new_obj_lifeLine)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавлен в модель"]])
                        del new_obj_lifeLine
                    if child["xmi:type"]=="uml:OccurrenceSpecification":
                        our_point=Object()
                        our_point.Set_id(child["xmi:id"])
                        our_point.Set_type(child["xmi:type"])
                        our_point.Set_name(child["covered"])
                        self.Add_object(our_point)
                        del our_point
                    if child["xmi:type"]=="uml:Message":
                        our_obj_time_connection=obj_Time_connection()
                        current_name=""
                        if child.has_attr("name")==True:
                            current_name=child["name"]
                        else:
                            current_name=child["xmi:id"]
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+current_name+"' начал читаться из XML файла"]])
                        our_obj_time_connection.Set_type(child["xmi:type"])
                        our_obj_time_connection.Set_id(child["xmi:id"])
                        if child.has_attr("name"):
                            our_obj_time_connection.Set_name(child["name"])
                        else:
                            our_obj_time_connection.Set_name("None")
                        if child.has_attr("sendevent"):
                            our_obj_time_connection.Set_id_point_from(child["sendevent"])
                        else:
                            our_obj_time_connection.Set_id_point_from("None")
                        if child.has_attr("receiveevent"):
                            our_obj_time_connection.Set_id_point_to(child["receiveevent"])
                        else:
                            our_obj_time_connection.Set_id_point_to("None")
                        our_obj_time_connection.Set_kind_connection(child["messagekind"])
                        our_obj_time_connection.Set_type_connection(child["messagesort"])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+current_name+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+current_name+"' добавляется в модель"]])
                        self.Add_object(our_obj_time_connection)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+current_name+"' добавлен в модель"]])
                        del our_obj_time_connection
                    if child["xmi:type"]=="uml:Property" and child.has_attr("name")==False and child.has_attr("visibility")==False:
                        our_life_line=None
                        for i in range(0,len(self.list_of_objects)):
                            if self.list_of_objects[i].Get_type()=="uml:Lifeline" and self.list_of_objects[i].Get_connected_object_id()==child["xmi:id"]:
                                our_life_line=self.list_of_objects[i]
                                break
                        if our_life_line==None:
                            our_list_of_diagrams=self.model.Get_list_of_diagrams()
                            for k in range(0,len(our_list_of_diagrams)):
                                list_of_objects=our_list_of_diagrams[k].Get_list_of_objects()
                                for i in range(0,len(list_of_objects)):
                                    if list_of_objects[i].Get_type()=="uml:Lifeline" and list_of_objects[i].Get_connected_object_id()==child["xmi:id"]:
                                        our_life_line=list_of_objects[i]
                                        break
                        if len(child.contents)!=0:
                            our_life_line.Set_connected_object_id(child.contents[1]["xmi:idref"])
                    if child["xmi:type"]=="uml:CombinedFragment":
                        our_alternative=obj_Alternative()
                       #result_page_job_tracert.configure(state="normal")
                        our_alternative.Set_id(child["xmi:id"])
                        our_alternative.Set_type(child["xmi:type"])
                        our_alternative.Set_name(child["name"])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' начал читаться из XML файла"]])
                        our_alternative.Set_type_alternative(child["interactionoperator"])
                        our_alternative.Parse_alternative(child)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавляется в модель"]])
                        self.Add_object(our_alternative)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+child["name"]+"' добавлен в модель"]])
                        del our_alternative
                    if child["xmi:type"]=="uml:InstanceSpecification":
                        for i in range(0,len(self.list_of_objects)):
                            if self.list_of_objects[i].Get_type()=="uml:Lifeline":
                                if child["xmi:id"]==self.list_of_objects[i].Get_connected_object_id():
                                    self.list_of_objects[i].Set_connected_object_id(child["classifier"])
                                    break
                        our_list_of_diagrams=self.model.Get_list_of_diagrams()
                        for k in range(0,len(our_list_of_diagrams)):
                            list_of_objects=our_list_of_diagrams[k].Get_list_of_objects()
                            for i in range(0,len(list_of_objects)):
                                if list_of_objects[i].Get_type()=="uml:Lifeline":
                                    if child["xmi:id"]==list_of_objects[i].Get_connected_object_id():
                                        list_of_objects[i].Set_connected_object_id(child["classifier"])
                                        break
                    if child["xmi:type"]=="uml:Comment":
                        our_comment=Object()
                        curr_text=''
                        if child.has_attr("body"):
                            curr_text+=child["body"]
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+curr_text+"' начал читаться из XML файла"]])
                        our_comment.Set_id(child["xmi:id"])
                        our_comment.Set_type(child["xmi:type"])
                        our_comment.Set_name(curr_text)
                        if len(child.contents)!=0:
                            our_comment.Add_parents(child.contents[1]["xmi:idref"])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+curr_text+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+curr_text+"' добавляется в модель"]])
                        self.Add_object(our_comment)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"'"+curr_text+"' добавлен в модель"]])
                        del our_comment
                    if child["xmi:type"]=="uml:Dependency" or child["xmi:type"]=="uml:Realization":
                        our_dependency=obj_Connection()
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"' начал читаться из XML файла"]])
                        our_dependency.Set_type(child["xmi:type"])
                        our_dependency.Set_id(child["xmi:id"])
                        if child.has_attr("name"):
                            our_dependency.Set_name(child["name"])
                        else:
                            our_dependency.Set_name("None")
                        our_dependency.Set_sender_class_id(child["client"])
                        our_dependency.Set_recipient_class_id(child["supplier"])
                        our_dependency.Set_role_sender("None")
                        our_dependency.Set_role_recipient("None")
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"' прочитан"]])
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"' добавляется в модель"]])
                        self.Add_object(our_dependency)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга",child["xmi:type"]+"' добавлен в модель"]])
                        del our_dependency
        self.Define_the_diagram_type()
        return
    def Completion_of_the_diagram_formation(self):  
        if self.Get_type()=="Use Case diagram":
            list_of_objects=self.list_of_objects
            for i in range(0,len(list_of_objects)):
                current_node=list_of_objects[i]
                if current_node.Get_type()=="uml:UseCase":
                    if len(current_node.Get_list_of_extentions())!=0:
                        our_list_of_extentions=current_node.Get_list_of_extentions()
                        for j in range(0,len(our_list_of_extentions)):
                            if len(our_list_of_extentions[j])==2 and our_list_of_extentions[j][0][0:4]=="EAID" and our_list_of_extentions[j][1][0:4]=="EAID": 
                                our_extention=[]
                                our_extention.append(current_node.Get_id())
                                for k in range(0,len(self.list_of_objects)):
                                    if self.list_of_objects[k].Get_type()=="uml:Comment":
                                        parents_list=self.list_of_objects[k].Get_parents_id()
                                        for l in range(0,len(parents_list)):
                                            if parents_list[l]==our_list_of_extentions[j][0]:
                                                result=re.findall("([^ \|]{1}[^\|]*[^ \|]{1})",self.list_of_objects[k].Get_name())
                                                our_extention.append(result)
                                                break
                                self.Find_object(our_list_of_extentions[j][1]).Add_extention(our_extention)
                                current_node.Delete_extention(j)
                                self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                if current_node.Get_type()=="uml:Class":
                    current_node.Set_type("System boundary")
                    self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
        if self.Get_type()=="Sequence diagram":
            list_of_objects=self.list_of_objects
            for i in range(0,len(list_of_objects)):
                current_node=list_of_objects[i]
                if list_of_objects[i].Get_type()=="uml:Message":
                    if list_of_objects[i].Get_id_point_from()!="None":
                        our_point=self.Find_object(list_of_objects[i].Get_id_point_from())
                        list_of_objects[i].Set_id_point_from(our_point.Get_name())
                    if list_of_objects[i].Get_id_point_to()!="None":
                        our_point=self.Find_object(list_of_objects[i].Get_id_point_to())
                        list_of_objects[i].Set_id_point_to(our_point.Get_name())
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+self.list_of_objects[i].Get_name()+"'"]])
            i=0
            while i<len(list_of_objects):
                if list_of_objects[i].Get_type()=="uml:OccurrenceSpecification":
                    self.Delete_object(i,None)
                else:
                    i+=1
        if self.Get_type()=="Class diagram":
            list_of_objects=self.list_of_objects
            for i in range(0,len(list_of_objects)):
                current_node=list_of_objects[i]
                if current_node.Get_type()=="uml:Class":
                    for j in range(0,len(current_node.Get_list_of_parametres())):
                        current_param=current_node.Get_info_about_param(j)
                        current_association=None
                        current_string=current_param[0]
                        if current_string[0:4]=="EAID":
                            current_association=self.model.Find_object_in_Model(current_param[0])
                            if current_association.Get_recipient_class_id()==current_param[1]:
                                current_association.Set_recipient_class_id(current_param[2])
                                current_association.Set_flag_composite(True)
                                self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                        else:
                            current_string=current_param[1]
                            if current_string[0:4]=="EAID":
                                current_node.Change_param(j,1,self.model.Find_object_in_Model(current_param[1]).Get_name())  
                                self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                    for j in range(0,len(current_node.Get_list_of_functions())):
                        current_func=current_node.Get_info_about_func(j)
                        for k in range(0,len(current_func)):
                            current_string=current_func[k]
                            if current_string[0:4]=="EAID":
                                current_node.Change_func(j,k,self.model.Find_object_in_Model(current_string).Get_name())
                                self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
        list_of_objects=self.list_of_objects
        for i in range(0,len(list_of_objects)):
            current_node=list_of_objects[i]
            if current_node.Get_type()=="uml:Association":
                if current_node.Get_flag_composite()==True:
                    current_node.Set_type("uml:Composition")
                    sender=self.model.Find_object_in_Model(current_node.Get_sender_class_id())
                    recipient=self.model.Find_object_in_Model(current_node.Get_recipient_class_id())
                    our_param=[]
                    for j in range(0,len(sender.Get_list_of_parametres())):
                        if j<len(sender.Get_list_of_parametres()) and sender.Get_info_about_param(j)[2]==recipient.Get_id():
                            our_param.append(sender.Get_info_about_param(j)[3])
                            sender.Delete_param(j)
                            j-=1
                            our_name=sender.Get_name()
                            for k in range(0,len(recipient.Get_list_of_parametres())):
                                local_name=recipient.Get_info_about_param(k)[1]
                                if our_name==local_name[0:len(our_name)]:
                                    our_name=local_name
                            our_name+="_1"
                            our_param.append(sender.Get_name())
                            our_param.append(our_name)
                            our_param.append(current_node.Take_type_string_from_type_number(current_node.Get_type_of_the_number_of_sender_class()))
                            our_param.append("None")
                            recipient.Add_param(our_param)
                            self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                    if current_node.Get_flag_shared()==False:
                        sender.Set_independent_existence(False)
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                    else:
                        current_node.Set_type("uml:Aggregation")
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                    for j in range(0,len(sender.Get_list_of_parametres())):
                        if sender.Get_parent(j)==recipient.Get_id():
                            sender.Delete_parent(j)
                            self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
                            break
                elif self.model.Find_object_in_Model(current_node.Get_sender_class_id()).Get_type()=="uml:Actor":
                    flag=False
                    our_actors=self.model.Find_object_in_Model(current_node.Get_recipient_class_id()).Get_list_of_actors()
                    for j in range(0,len(our_actors)):
                        if our_actors[j]==current_node.Get_sender_class_id():
                            flag=True
                            break
                    if flag==False:
                        self.model.Find_object_in_Model(current_node.Get_recipient_class_id()).Add_actor(current_node.Get_sender_class_id())
                        self.model.controller.AddCommand(["Visual",["Трассировка парсинга","Были внесены изменения в диаграмму '"+self.name+"', связанные с элементом '"+current_node.Get_name()+"'"]])
        return
    def UsualCheck(self):
        global predictor
        if len(self.list_of_objects)==0:
            self.model.Add_recomendation("Диаграмма '"+self.name+"' пустая, рекомендуется внести в неё элементы","Детальность модели")
        local_numbers=0
        for i in range(0,len(self.model.Get_list_of_diagrams())):
            if self.model.Get_list_of_diagrams()[i].Get_name()==self.name:
                local_numbers+=i*1000
        if self.type=="Use Case diagram":
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
                            self.model.Add_recomendation("Рекомендуется создать диаграмму системных взаимодействий, связанную с прецедентов '"+self.list_of_objects[i].Get_name()+"'","Полнота модели")
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
                                    self.model.Add_recomendation("Рекомендуется добавить актёра с именем '"+self.model.Find_object_in_Model(list_of_actors[j]).Get_name()+"' в диаграмму системных взаимодейтсвий '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'","Детальность модели")
                            list_of_extentions=self.list_of_objects[i].Get_list_of_extentions()
                            for j in range(0,len(list_of_extentions)):
                                flag_extention=False
                                for k in range(0,len(sequence_diagram_objects)):
                                    if sequence_diagram_objects[k].Get_type()=="uml:CombinedFragment" and self.model.Find_object_in_Model(list_of_extentions[j][0]).Get_name()==sequence_diagram_objects[k].Get_name():
                                        flag_extention=True
                                        break
                                if flag_extention==False:
                                    self.model.Add_recomendation("Рекомендуется добавить комбинированный фрагмент (alt) с именем '"+self.model.Find_object_in_Model(list_of_extentions[j][0]).Get_name()+"' в диаграмму системных взаимодействий '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'","Полнота модели")
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
                                                self.model.Add_recomendation("Рекомендуется добавить условие '"+condition+"' в комбинированный фрагмент '"+self.model.Find_object_in_Model(list_of_extentions[j][0]).Get_name()+"' в диаграмме системных взаимодействий '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'","Детальность модели")
        if self.type=="Sequence diagram":
            list_of_use_cases_diagrams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Use Case diagram":
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
                self.model.Add_recomendation("Рекомендуется создать прецедент с именем '"+self.name+"', который будет связан с диаграммой системных взаимодействий с именем '"+self.name+"'","Полнота модели")
            else:
                counter=0
                list_of_objects=self.Get_list_of_objects()
                for i in range(0,len(list_of_objects)):
                    if list_of_objects[i].Get_type()=="uml:Lifeline":
                        counter+=1
                        if list_of_objects[i].Get_connected_object_id()[0:7]!="EAID_AT":
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
                                        self.model.Add_recomendation("Объект '"+connected_object.Get_name()+"' не имеет функцию с именем '"+list_of_messages[j].Get_name()+"'. Рекомендуется изменить имя системного вызова в диаграмме системных взаимодейтсвий с именем '"+self.name+"' на уже существующую в данном объекте или создать новую функцию с таким именем","Детальность модели")
                        else:
                            self.model.Add_recomendation("Рекомендуется соединить временную линию '"+list_of_objects[i].Get_name()+"' в диаграмме системных взаимодействий с именем '"+self.name+"' с существующим классом","Детальность модели")
                    if list_of_objects[i].Get_type()=="uml:CombinedFragment":
                        list_of_covered_lifelines=list_of_objects[i].Get_list_of_covered_lifeline().copy()
                        j=0
                        while j<len(list_of_covered_lifelines):
                            if self.model.Find_object_in_Model(list_of_covered_lifelines[j]).Get_connected_object_id()[0:7]=="EAID_AT" or self.model.Find_object_in_Model(self.model.Find_object_in_Model(list_of_covered_lifelines[j]).Get_connected_object_id()).Get_type()=="uml:Actor":
                                list_of_covered_lifelines.pop(j)
                            else:
                                j+=1
                        if len(list_of_covered_lifelines)==0 and list_of_objects[i].Get_type_alternative()=="alt":
                            list_of_use_cases_diagrams=[]
                            for j in range(0,len(self.model.Get_list_of_diagrams())):
                                if self.model.Get_diagram(j).Get_type()=="Use Case diagram":
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
                            print(list_of_extentions)
                            if flag_exist==False:
                                self.model.Add_recomendation("Рекомендуется добавить расширение с именем '"+list_of_objects[i].Get_name()+"' в прецедент с именем '"+current_use_case.Get_name()+"' в диаграмме прецедентов '"+current_use_case_diagram.Get_name()+"'","Детальность модели")
                            else:
                                print("LIST:")
                                print(list_of_objects[i].Get_list_of_alternatives())
                                for condition in list_of_objects[i].Get_list_of_alternatives():
                                    print("CON",condition)
                                    flag_exist=False
                                    for node_condition in list_of_extentions[1]:
                                        if condition[0]==node_condition:
                                            flag_exist=True
                                            break
                                    if flag_exist==False:
                                        self.model.Add_recomendation("Рекомендуется добавить условие '"+condition[0]+"' из '"+list_of_objects[i].name+"' из '"+self.name+"' в расширение '"+self.model.Find_object_in_Model(list_of_extentions[0]).name+"' в '"+current_use_case_diagram.name+"'","Детальность модели")
                if counter<2:
                    self.model.Add_recomendation("В диаграмме системных взаимодействий '"+self.name+"' есть только одна временная линия. Данная диаграмма является некорректной и рекомендуется добавление в неё еще нескольких временных линий.","Детальность модели")
        if self.type=="Class diagram":
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_type()=="uml:Class":
                    if len(self.list_of_objects[i].Get_list_of_functions())==0:
                        self.model.Add_recomendation("Рекомендуется в класс '"+self.list_of_objects[i].Get_name()+"' добавить функции, т.к. класс не обладает ни одной функцией","Детальность модели")
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
                            current_string+=" в их родителя и сделать её виртуальной"
                            self.model.Add_recomendation(current_string,"Детальность модели")
        list_of_connected_objects=[]
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_type()!="uml:Association" and self.list_of_objects[i].Get_type()!="uml:Message" and self.list_of_objects[i].Get_type()!="uml:Aggregation" and self.list_of_objects[i].Get_type()!="uml:Composition":
                flag_exist=False
                for j in range(0,len(list_of_connected_objects)):
                    if self.list_of_objects[i].Get_name()==list_of_connected_objects[j][0] and self.list_of_objects[i].Get_type()==list_of_connected_objects[j][2]:
                        flag_exist=True
                        list_of_connected_objects[j][1]+=1
                        break
                if flag_exist==False:
                    new_conn_obj=[]
                    new_conn_obj.append(self.list_of_objects[i].Get_name())
                    number_of_connected_objects=len(self.list_of_objects[i].Get_parents_id())
                    for j in range(0,len(self.list_of_objects)):
                        for k in range(0,len(self.list_of_objects[j].Get_parents_id())):
                            if self.list_of_objects[j].Get_parent(k)==self.list_of_objects[i].Get_id():
                                number_of_connected_objects+=1
                    if self.list_of_objects[i].Get_type()=="uml:CombinedFragment":
                        number_of_connected_objects+=len(self.list_of_objects[i].Get_list_of_covered_lifeline())
                    new_conn_obj.append(number_of_connected_objects)
                    new_conn_obj.append(self.list_of_objects[i].Get_type())
                    list_of_connected_objects.append(new_conn_obj)
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_type()=="uml:Association" or self.list_of_objects[i].Get_type()=="uml:Aggregation" or self.list_of_objects[i].Get_type()=="uml:Composition":
                sender_id=self.list_of_objects[i].Get_sender_class_id()
                recipient_id=self.list_of_objects[i].Get_recipient_class_id()
                sender=self.Find_object(sender_id)
                recipient=self.Find_object(recipient_id)
                for j in range(0,len(list_of_connected_objects)):
                    if list_of_connected_objects[j][0]==sender.Get_name() or list_of_connected_objects[j][0]==recipient.Get_name():
                        list_of_connected_objects[j][1]+=1
            elif self.list_of_objects[i].Get_type()=="uml:Message":
                sender_id=self.list_of_objects[i].Get_id_point_from()
                recipient_id=self.list_of_objects[i].Get_id_point_to()
                sender=self.Find_object(sender_id)
                recipient=self.Find_object(recipient_id)
                for j in range(0,len(list_of_connected_objects)):
                    if list_of_connected_objects[j][0]==sender.Get_name() or list_of_connected_objects[j][0]==recipient.Get_name():
                        list_of_connected_objects[j][1]+=1        
        for i in range(0,len(list_of_connected_objects)):
            if list_of_connected_objects[i][1]==0:
                self.model.Add_recomendation("Объект '"+list_of_connected_objects[i][0]+"' из диаграммы '"+self.name+"' ни с чем не связан, необходимо данный объект связать с другими элементами диаграммы","Детальность модели")
        return
    def __del__(self):
        while len(self.list_of_objects)>0:
            del self.list_of_objects[0]
    #Раздел с паттернами и механизмами
    def Offering_classes_on_frequently_repeated_nouns_in_use_cases(self):
        if self.type=="Use Case diagram":
            for object in self.list_of_objects:
                if object.type=="uml:UseCase":
                    self.Get_nouns_and_verbs_from_words(object)
            list_of_class_diagams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Class diagram":
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
                        self.model.Add_recomendation("Рекомендуется создать класс с именем '"+self.list_of_nouns[i][0]+"'","Механизм предложения классов по часто повторяющимся существительным в прецедентах")
        return
    def Paired_words_in_sequence_diagrams(self):
        if self.type=="Sequence diagram" or self.type=="Use Case diagram":
            for object in self.list_of_objects:
                if object.type=="uml:Message" or object.type=="uml:UseCase":
                    self.Get_nouns_and_verbs_from_words(object)
            list_of_class_diagams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Class diagram":
                    list_of_class_diagams.append(self.model.Get_diagram(i))
            #print("Список глаголов:",self.list_of_verbs)
            for i in range(0,len(self.list_of_verbs)):
                current_verb=self.list_of_verbs[i]
                current_sequence_diagram=None
                if self.Get_type()=="Sequence diagram":
                    current_sequence_diagram=self
                else:
                    for j in range(0,len(self.model.Get_list_of_diagrams())):
                        if self.model.Get_diagram(j).Get_name()==current_verb[1]:
                            current_sequence_diagram=self.model.Get_diagram(j)
                            break
                if current_sequence_diagram!=None:
                    current_list_of_recommended_sequence=[]
                    if current_verb[0]=="turn on" or current_verb[0]=="switch off":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["turn on",False])
                            current_list_of_recommended_sequence.append(["switch off",False])
                        elif current_verb[0]=="turn on":
                            current_list_of_recommended_sequence.append(["turn on",True])
                            current_list_of_recommended_sequence.append(["switch off",False])
                        else:
                            current_list_of_recommended_sequence.append(["turn on",False])
                            current_list_of_recommended_sequence.append(["switch off",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'turn on' и 'switch off', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'turn on', так как существует системный вызов 'switch off'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'switch off', так как существует системный вызов 'turn on'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'turn on' поставить выше системного вызова 'switch off'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="open" or current_verb[0]=="close":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["open",False])
                            current_list_of_recommended_sequence.append(["close",False])
                        elif current_verb[0]=="open":
                            current_list_of_recommended_sequence.append(["open",True])
                            current_list_of_recommended_sequence.append(["close",False])
                        else:
                            current_list_of_recommended_sequence.append(["open",False])
                            current_list_of_recommended_sequence.append(["close",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'open' и 'close', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'open', так как существует системный вызов 'close'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'close', так как существует системный вызов 'open'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'open' поставить выше системного вызова 'close'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="log in" or current_verb[0]=="log out":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["log in",False])
                            current_list_of_recommended_sequence.append(["log out",False])
                        elif current_verb[0]=="log in":
                            current_list_of_recommended_sequence.append(["log in",True])
                            current_list_of_recommended_sequence.append(["log out",False])
                        else:
                            current_list_of_recommended_sequence.append(["log in",False])
                            current_list_of_recommended_sequence.append(["log out",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'log in' и 'log out', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'log in', так как существует системный вызов 'log out'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'log out', так как существует системный вызов 'log in' и это может повысить безопасность ситемных взаимодейтсвий в данном сценарии","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'log in' поставить выше системного вызова 'log out'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="send" or current_verb[0]=="recieve":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["send",False])
                            current_list_of_recommended_sequence.append(["recieve",False])
                        elif current_verb[0]=="send":
                            current_list_of_recommended_sequence.append(["send",True])
                            current_list_of_recommended_sequence.append(["recieve",False])
                        else:
                            current_list_of_recommended_sequence.append(["send",False])
                            current_list_of_recommended_sequence.append(["recieve",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'send' и 'recieve', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить парный системный вызов ('send' или 'find') связанный с системным вызовом 'recieve'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'recieve', так как существует системный вызов 'send', но нет ответа на эту отправку","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'send' поставить выше системного вызова 'recieve'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="find" or current_verb[0]=="recieve":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["find",False])
                            current_list_of_recommended_sequence.append(["recieve",False])
                        elif current_verb[0]=="find":
                            current_list_of_recommended_sequence.append(["find",True])
                            current_list_of_recommended_sequence.append(["recieve",False])
                        else:
                            current_list_of_recommended_sequence.append(["find",False])
                            current_list_of_recommended_sequence.append(["recieve",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'find' и 'recieve', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить парный системный вызов ('send' или 'find') связанный с системным вызовом 'recieve'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'recieve', так как существует системный вызов 'find', ведь при поиске необходимо получить искомый объект","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'find' поставить выше системного вызова 'recieve'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="edit":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["find",False])
                            current_list_of_recommended_sequence.append(["edit",False])
                        elif current_verb[0]=="edit":
                            current_list_of_recommended_sequence.append(["find",False])
                            current_list_of_recommended_sequence.append(["edit",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'find' и 'edit', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'find', так как существует системный вызов 'edit'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'find' поставить выше системного вызова 'edit'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="start" or current_verb[0]=="finish":                    
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["start",False])
                            current_list_of_recommended_sequence.append(["finish",False])
                        elif current_verb[0]=="start":
                            current_list_of_recommended_sequence.append(["start",True])
                            current_list_of_recommended_sequence.append(["finish",False])
                        else:
                            current_list_of_recommended_sequence.append(["start",False])
                            current_list_of_recommended_sequence.append(["finish",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'start' и 'finish', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'start', так как существует системный вызов 'finish'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'finish', так как существует системный вызов 'start'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'start' поставить выше системного вызова 'finish'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                    elif current_verb[0]=="download" or current_verb[0]=="upload":
                        if current_sequence_diagram!=self:
                            current_list_of_recommended_sequence.append(["select",False])
                            current_list_of_recommended_sequence.append(["download",False])
                            current_list_of_recommended_sequence.append(["upload",False])
                        elif current_verb[0]=="download":
                            current_list_of_recommended_sequence.append(["select",False])
                            current_list_of_recommended_sequence.append(["download",True])
                            current_list_of_recommended_sequence.append(["upload",False])
                        else:
                            current_list_of_recommended_sequence.append(["select",False])
                            current_list_of_recommended_sequence.append(["download",False])
                            current_list_of_recommended_sequence.append(["upload",True])
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
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системные вызовы 'select' и 'download или upload', так как их наличие подразумевает само название данной диаграммы","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin==-1 and end!=-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'select', так как существует системный вызов '"+second_sequence+"'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin!=-1 and end==-1:
                            self.model.Add_recomendation("Рекомендуется в диаграмму системных взаимодействий '"+current_sequence_diagram.Get_name()+"' добавить системный вызов 'download или upload', так как существует системный вызов 'select'","Механизм преложения парных глаголов в диаграммах прецеднтов")
                        elif begin>end:
                            self.model.Add_recomendation("Рекомендуется в диаграмме системных взаимодействий '"+current_sequence_diagram.Get_name()+"' системный вызов 'select' поставить выше системного вызова '"+second_sequence+"'","Механизм преложения парных глаголов в диаграммах прецеднтов")
    def GRASP(self):
        if self.type=="Class diagram":
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
                                self.model.Add_recomendation("Рекомендуется создать отдельный класс для типа данных '"+list_of_params[j][2]+"', чтобы увеличить зацепление и обеспечить низкую связность между элементами классами в модели","GRASP")
                            list_of_params.pop(j)
                        else:
                            j+=1
                    if len(list_of_params)!=0:
                        list_of_functions=object.Get_list_of_functions().copy()
                        for j in range(0,len(list_of_params)):
                            flag_exist=False
                            current_name="Create_"+list_of_params[j][1]
                            for k in range(0,len(list_of_functions)):
                                if list_of_functions[k][2]==current_name:
                                    flag_exist=True
                                    break
                            if flag_exist==False:
                                self.model.Add_recomendation("Рекомендуется в класс '"+object.Get_name()+"' добавить функцию для создания '"+list_of_params[j][1]+"', так как он работает с ними","GRASP")
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
                                self.model.Add_recomendation("Рекомендуется создать отдельный класс с классами '"+object.Get_name()+"' и '"+current_object.Get_name()+"', ослабляющий сильную связь между ними (в первом классе есть второй, а во втором - первый) ","GRASP")
        return

class obj_Class(Object):
    list_of_parametres=[]#[видимость,тип,имя,кратность,начальное значение]
    list_of_functions=[]
    independent_existence=True
    sender_class_id=""
    recipient_class_id=""
    def __init__(self):
        self.parents_id=[]
        self.list_of_parametres=[]
        self.list_of_functions=[]
        self.independent_existence=True
        self.sender_class_id=""
        self.recipient_class_id=""
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
        if local_root.name=="nestedclassifier":
            self.Add_parents(local_root.parent["xmi:id"])
        for child in local_root.children:
            if child.name=="ownedattribute":
                new_attribute=[]
                if child.has_attr("association"):
                    new_attribute.append(child["association"])
                    new_attribute.append(child["xmi:id"])
                    new_attribute.append(child.contents[1]["xmi:idref"])
                    new_attribute.append(child["visibility"])
                else:
                    new_attribute.append(child["visibility"])
                    our_elem=child.find("type")
                    if our_elem!=None:
                        if our_elem.has_attr("href"):
                            new_attribute.append(our_elem["href"])
                        else:
                            new_attribute.append(our_elem["xmi:idref"])
                    else:
                        new_attribute.append("None")
                    if child.has_attr("name"):
                        new_attribute.append(child["name"])
                    else:
                        new_attribute.append("None")
                    new_attribute.append("None")
                    for check in child.children:
                        if check.name=="defaultvalue":
                            new_attribute.append(check["value"])
                while len(new_attribute)!=5:
                    new_attribute.append("None")
                self.Add_param(new_attribute)
            if child.name=="ownedoperation":
                new_operation=[]
                new_operation.append(child["visibility"])
                new_operation.append("")
                new_operation.append(child["name"])
                for i in child.children:
                    if i.name=="ownedparameter" and i["direction"]!="return":
                        our_elem=i.find("type")
                        if our_elem!=None:
                            new_operation.append(i.contents[1]["href"])
                        elif i.has_attr("type")!=False:
                            new_operation.append(i["type"])
                        else:
                            new_operation.append("None")
                        new_operation.append(i["name"])
                    if i.name=="ownedparameter" and i["direction"]=="return":
                        new_operation[1]=i["type"]
                self.Add_func(new_operation)
            if child.name=="generalization":
                flag=False
                for i in range(0,len(self.parents_id)):
                    if self.parents_id[i]==child["general"]:
                        flag=True
                        break
                if flag==False:
                    self.Add_parents(child["general"])
            if self.Get_type()=="uml:AssociationClass":
                if child.name=="memberend":
                    if child["xmi:idref"][5:8]=="dst":
                        self.recipient_class_id=child["xmi:idref"]
                    else:
                        self.sender_class_id=child["xmi:idref"]
                elif child.name=="ownedend":
                    if child["xmi:id"]==self.sender_class_id:
                        self.sender_class_id=child.contents[1]["xmi:idref"]
                    else:
                        self.recipient_class_id=child.contents[1]["xmi:idref"]
        self.Change_params_to_correct()
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
    sender_class_id=""
    recipient_class_id=""
    #connection types of sender-recipient classes
	#0=*
	#1=0
	#2=0..*
	#3=0..1
	#4=1
	#5=1..*
    type_of_the_number_of_sender_class=0
    type_of_the_number_of_recipient_class=0
    role_sender=""
    role_recipient=""
    flag_composite=False
    flag_shared=False
    def __init__(self):
        self.sender_class_id=""
        self.recipient_class_id=""
        self.type_of_the_number_of_sender_class=-1
        self.type_of_the_number_of_recipient_class=-1
        self.role_sender=""
        self.role_recipient=""
        self.flag_composite=False
        self.flag_shared=False
        return
    def Set_sender_class_id(self,new_sender_class_id):
        self.sender_class_id=new_sender_class_id
        return
    def Set_recipient_class_id(self,new_recipient_class_id):
        self.recipient_class_id=new_recipient_class_id
        return
    def Set_type_of_the_number_of_sender_class(self,new_type_of_the_number_of_sender_class):
        self.type_of_the_number_of_sender_class=new_type_of_the_number_of_sender_class
        return
    def Set_type_of_the_number_of_recipient_class(self,new_type_of_the_number_of_recipient_class):
        self.type_of_the_number_of_recipient_class=new_type_of_the_number_of_recipient_class
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
    def Get_type_of_the_number_of_sender_class(self):
        return self.type_of_the_number_of_sender_class
    def Get_type_of_the_number_of_recipient_class(self):
        return self.type_of_the_number_of_recipient_class
    def Get_role_sender(self):
        return self.role_sender
    def Get_role_recipient(self):
        return self.role_recipient
    def Get_flag_composite(self):
        return self.flag_composite
    def Get_flag_shared(self):
        return self.flag_shared
    def Take_your_type(self,upper,lower):
        if upper==lower:
            if upper=="-1":
                return 0
            if upper=="0":
                return 1
            else:
                return 4
        if lower=="0":
            if upper=="-1":
                return 2
            else:
                return 3
        else:
            return 5
    def Take_type_string_from_type_number(self,number):
        if number==0:
            return "*"
        elif number==1:
            return "0"
        elif number==2:
            return "0..*"
        elif number==3:
            return "0..1"
        elif number==4:
            return "1"
        elif number==5:
            return "1..*"
        else:
            return "None"
    def Parse_connection(self,root):
        local_root=root
        for child in local_root.children:
            if child.name=="memberend":
                if self.recipient_class_id=="":
                    self.recipient_class_id=child["xmi:idref"]
                else:
                    self.sender_class_id=child["xmi:idref"]
            if child.name=="ownedend":
                if child["xmi:id"]==self.recipient_class_id:
                    self.recipient_class_id=child.contents[1]["xmi:idref"]
                    if len(child.contents)>4:
                        num1=child.contents[3]["value"]
                        num2=child.contents[5]["value"]
                        self.type_of_the_number_of_recipient_class=self.Take_your_type(num2,num1)
                    else:
                        self.type_of_the_number_of_recipient_class=1
                    if child.has_attr("name"):
                        self.role_recipient=child["name"]
                    else:
                        self.role_recipient="None"
                else:
                    self.sender_class_id=child.contents[1]["xmi:idref"]
                    if len(child.contents)>4:
                        num1=child.contents[3]["value"]
                        num2=child.contents[5]["value"]
                        self.type_of_the_number_of_sender_class=self.Take_your_type(num2,num1)
                    else:
                        self.type_of_the_number_of_recipient_class=1
                    if child.has_attr("name"):
                        self.role_sender=child["name"]
                    else:
                        self.role_sender="None"
                    if child["aggregation"]=="composite":
                        self.Set_flag_composite(True)
                    if child["aggregation"]=="shared":
                        self.Set_flag_shared(True)
        if self.role_sender=="":
            self.role_sender="None"
        if self.role_recipient=="":
            self.role_recipient="None"
        return
    
class obj_Use_Case(Object):
    list_of_actors=[]
    list_of_includions=[]#what is included in this Use Case (required)
    list_of_extentions=[]#what extends this Use Case (optional, but possible)
    def __init__(self):
        self.list_of_actors=[]
        self.parents_id=[]
        self.list_of_includions=[]
        self.list_of_extentions=[]
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
        for child in local_root.children:
            if child.name=="include":
                self.list_of_includions.append(child["addition"])
            if child.name=="extend":
                new_extent=[]
                new_extent.append(child["xmi:id"])
                new_extent.append(child["extendedcase"])
                self.list_of_extentions.append(new_extent)
            if child.name=="generalization":
                self.parents_id.append(child["general"])
        return

class obj_LifeLine(Object):
    connected_object_id=""
    def __init__(self):
        self.connected_object_id=""
        return
    def Set_connected_object_id(self,new_connected_object_id):
        self.connected_object_id=new_connected_object_id
        return
    def Get_connected_object_id(self):
        return self.connected_object_id

class obj_Time_connection(Object):
    id_point_from=""
    id_point_to=""
    type_connection=""
    kind_connection=""
    def __init__(self):
        self.id_point_from=""
        self.id_point_to=""
        self.type_connection=""
        self.kind_connection=""
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

class obj_Alternative(Object):
    type_alternative=""
    list_of_covered_lifeline=[]
    list_of_alternatives=[]
    def __init__(self):
        self.type_alternative=""
        self.list_of_covered_lifeline=[]
        self.list_of_alternatives=[]
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
        for child in local_root.children:
            if child.name=="covered":
                self.Add_covered_lifeline(child["xmi:idref"])
            elif child.name=="operand":
                new_alernative_variavnt=[]
                for elements in child.children:
                    if elements.name=="guard":
                        if elements.contents[1].has_attr("body"):
                            new_alernative_variavnt.append(elements.contents[1]["body"])
                    elif elements.name=="fragment":
                        new_alernative_variavnt.append(elements["covered"])
                if len(new_alernative_variavnt)!=0:
                    self.Add_alternative(new_alernative_variavnt)
        return

controller=controller()