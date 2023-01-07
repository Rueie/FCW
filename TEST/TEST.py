import math
import tkinter as tk
from tkinter import CENTER, END, LEFT, RIGHT, ttk
from tkinter import filedialog
from win32api import GetSystemMetrics
from bs4 import BeautifulSoup

file_name_with_params="Params.txt"
number_of_login_windows=0;
current_window=0
current_widget=0
number_of_opened_frames=1#число открытых вкладок основного окна
our_model=None

class Object:
    id=""
    type=""
    name=""
    def __init__(self):
        self.id=""
        self.type=""
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

#НАДО ДОПИСАТЬ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class Model(Object):
    list_of_objects=[]
    def __init__(self,init_name):
        self.name=init_name
        self.list_of_objects=[]
        return
    def Add_obj_to_model(self,new_object):
        self.list_of_objects.append(new_object)
        return
    def Get_info_about_object(self,id_object,number_of_object):
        if number_of_object>len(self.list_of_objects):
            return None
        for i in range(0,len(self.list_of_objects)):
            if i.Get_id()==id_object:
                return i
        return None
    def Get_list_of_objects(self):
        return self.list_of_objects
    def Find_name_to_ip(self,our_id):
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_id()==our_id:
                return self.list_of_objects[i].Get_name()
        return None
    def Find_obj_to_ip(self,our_ip):
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_id()==our_ip:
                return self.list_of_objects[i]
        return None
    def Parse_model(self,root):
        local_root=root
        for child in local_root.descendants:
            if child.name=="packagedelement":
                local_root=child
                break
        result_page_label3.configure(text="Reading the model...")
        result_page_progressbar.configure(maximum=10000)
        for child in local_root.descendants:
            if child!="\n":
                if child.name=="packagedelement" or child.name=="nestedclassifier":
                    if child["xmi:type"]=="uml:Class":
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,"Class '"+child["name"]+"' being read\n")
                        new_obj_class=obj_Class()
                        new_obj_class.Set_id(child["xmi:id"])
                        new_obj_class.Set_name(child["name"])
                        new_obj_class.Set_type(child["xmi:type"])
                        new_obj_class.Parse_class(child)
                        result_page_job_tracert.insert(tk.END,"Class '"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,"Class '"+child["name"]+"' is added to the model\n")
                        self.Add_obj_to_model(new_obj_class)
                        result_page_job_tracert.insert(tk.END,"Class '"+child["name"]+"' added to the model\n")
                        result_page_job_tracert.configure(state="disabled")
                        del new_obj_class
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:Association":
                        result_page_job_tracert.configure(state="normal")
                        tracert_string="Association '"+child["xmi:id"]
                        if child.has_attr("name"):
                            tracert_string+="("+child["name"]+")"
                        result_page_job_tracert.insert(tk.END,tracert_string+"' being read\n")
                        new_obj_connection=obj_Connection()
                        new_obj_connection.Set_id(child["xmi:id"])
                        if child.has_attr("name"):
                            new_obj_connection.Set_name(child["name"])
                        else:
                            new_obj_connection.Set_name("None")
                        new_obj_connection.Set_type(child["xmi:type"])
                        new_obj_connection.Parse_connection(child)
                        result_page_job_tracert.insert(tk.END,tracert_string+"' is read\n")
                        result_page_job_tracert.insert(tk.END,tracert_string+"' is added to the model\n")
                        self.Add_obj_to_model(new_obj_connection)
                        result_page_job_tracert.insert(tk.END,tracert_string+"' added to the model\n")
                        del new_obj_connection
                        result_page.after(1,result_page.update())
                    result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                    result_page_job_tracert.yview_moveto('1.0')
        result_page_progressbar.configure(maximum=len(self.list_of_objects))
        result_page_progressbar.configure(value=0)
        result_page_label3.configure(text="Post-processing of classes...")
        #конечный этап анализа распаршенных элементов модели
        for i in range(0,len(self.list_of_objects)):
            current_node=self.list_of_objects[i]
            if current_node.Get_type()=="uml:Class":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Class '"+current_node.Get_name()+"' is post-analyzed\n")
                for j in range(0,len(current_node.Get_parents_id())):
                    current_node.Change_parent(j,self.Find_name_to_ip(current_node.Get_parent(j)))
                for j in range(0,len(current_node.Get_list_of_parametres())):
                    current_param=current_node.Get_info_about_param(j)
                    current_association=None
                    current_string=current_param[0]
                    check_string=""
                    if len(current_string)>=4:
                        for k in range(0,4):
                            check_string+=current_string[k]
                    if check_string=="EAID":
                        current_association=self.Find_obj_to_ip(current_param[0])
                        if current_association.Get_recipient_class_id()==current_param[1]:
                            current_association.Set_recipient_class_id(current_param[2])
                            current_association.Set_flag_composite(True)
                    else:
                        current_string=current_param[1]
                        check_string=""
                        if len(current_string)>=4:
                            for k in range(0,4):
                                check_string+=current_string[k]
                        if check_string=="EAID":
                            current_node.Change_param(j,1,self.Find_name_to_ip(current_param[1]))               
                for j in range(0,len(current_node.Get_list_of_functions())):
                    current_func=current_node.Get_info_about_func(j)
                    for k in range(0,len(current_func)):
                        current_string=current_func[k]
                        check_string=""
                        if len(current_string)>=4:
                            for l in range(0,4):
                                check_string+=current_string[l]
                        if check_string=="EAID":
                            current_node.Change_func(j,k,self.Find_name_to_ip(current_string))
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.insert(tk.END,"Changes related to the class '"+current_node.Get_name()+"' have been made to the model\n")
                result_page_job_tracert.configure(state="disabled")
                result_page.after(1,result_page.update())
                result_page_job_tracert.yview_moveto('1.0')
        result_page_label3.configure(text="Post-processing of associations...")
        for i in range(0,len(self.list_of_objects)):
            current_node=self.list_of_objects[i]
            if current_node.Get_type()=="uml:Association":
                if current_node.Get_flag_composite()==True:
                    result_page_job_tracert.configure(state="normal")
                    result_page_job_tracert.insert(tk.END,"Association '"+current_node.Get_id()+"' is post-analyzed\n")
                    sender=self.Find_obj_to_ip(current_node.Get_sender_class_id())
                    recipient=self.Find_obj_to_ip(current_node.Get_recipient_class_id())
                    our_param=[]
                    for j in range(0,len(sender.Get_list_of_parametres())):
                        if len(sender.Get_info_about_param(j))==4 and sender.Get_info_about_param(j)[2]==recipient.Get_id():
                            our_param.append(sender.Get_info_about_param(j)[3])
                            sender.Delete_param(j)
                            our_name=sender.Get_name()
                            for k in range(0,len(recipient.Get_list_of_parametres())):
                                local_name=recipient.Get_info_about_param(k)[1]
                                if our_name==local_name[0:len(our_name)]:
                                    our_name=local_name
                            our_name+="_1"
                            our_param.append(sender.Get_name())
                            our_param.append(our_name)
                            recipient.Add_param(our_param)
                    result_page_job_tracert.insert(tk.END,"Changes related to the association '"+current_node.Get_id()+"' have been made to the model\n")
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.configure(state="disabled")
                result_page.after(1,result_page.update())
                result_page_job_tracert.yview_moveto('1.0')
        result_page_label3.configure(text="Model processing is completed")
        return
    
class obj_Class(Object):
    parents_id=[]
    list_of_parametres=[]
    list_of_functions=[]
    def __init__(self):
        self.parents_id=[]
        self.list_of_parametres=[]
        self.list_of_functions=[]
        return
    def Add_parents(self,new_parent):
        self.parents_id.append(new_parent)
        return
    def Add_param(self,new_param):
        self.list_of_parametres.append(new_param)
        return
    def Add_func(self,new_func):
        self.list_of_functions.append(new_func)
        return
    def Change_parent(self,number,new_id):
        if number>len(self.parents_id):
            return None
        else:
            self.parents_id[number]=new_id
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
    def Get_parent(self,number_of_parent):
        if number_of_parent>len(self.parents_id):
            return None
        else:
            return self.parents_id[number_of_parent]
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
    def Get_parents_id(self):
        return self.parents_id
    def Get_list_of_parametres(self):
        return self.list_of_parametres
    def Get_list_of_functions(self):
        return self.list_of_functions
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
                    if our_elem.has_attr("href"):
                        new_attribute.append(our_elem["href"])
                    else:
                        new_attribute.append(our_elem["xmi:idref"])
                    if child.has_attr("name"):
                        new_attribute.append(child["name"])
                    for check in child.children:
                        if check.name=="defaultvalue":
                            new_attribute.append(check["value"])
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
                        else:
                            new_operation.append(i["type"])
                        new_operation.append(i["name"])
                    if i.name=="ownedparameter" and i["direction"]=="return":
                        new_operation[1]=i["type"]
                self.Add_func(new_operation)
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
        if for_change=="Integer" or for_change=="EAJava_int" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#Integer":
            return "Int"
        if for_change == "Boolean" or for_change == "EAJava_boolean" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#Boolean":
            return "Bool"
        if for_change=="EAJava_string" or for_change=="UnlimitedNatural" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#UnlimitedNatural":
            return "String"
        if for_change=="None" or for_change=="EAnone_void" or for_change=="EAJava_void" or for_change=="http://schema.omg.org/spec/UML/2.1/uml.xml#String":
            return "Void"
        if for_change=="EAJava_char":
            return "Char"
        if for_change=="EAJava_double":
            return "Double"
        if for_change=="EAJava_float":
            return "Float"
        if for_change=="EAJava_long":
            return "Long"
        if for_change=="EAJava_short":
            return "Short"
        if for_change=="EAJava_byte":
            return "Byte"
        return for_change
    def Delete_param(self,number_of_param):
        if number_of_param<0 or number_of_param>len(self.list_of_parametres):
            return None
        del self.list_of_parametres[number_of_param]
    
class obj_Connection(Object):
    sender_class_id=""
    recipient_class_id=""
    #типы подключений классов отправителей-получателей
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
    def __init__(self):
        self.sender_class_id=""
        self.recipient_class_id=""
        self.type_of_the_number_of_sender_class=-1
        self.type_of_the_number_of_recipient_class=-1
        self.role_sender=""
        self.role_recipient=""
        self.flag_composite=False
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
        if self.role_sender=="":
            self.role_sender="None"
        if self.role_recipient=="":
            self.role_recipient="None"
        return
#конец раздела классов xml

#раздел с разными командами интерфейса
#функция обработки закрытия приложения
def exit_procrust():
    global number_of_login_windows, current_window
    if number_of_login_windows==1:
        login_out
    main_window.destroy()
    exit

#раздел функций, связанных с регистрацией
#функция выхода из окна входа в учетную запись
def login_out():
    global number_of_login_windows, current_window
    current_window.destroy()
    number_of_login_windows=0
    current_window=0
    exit_button['state']='normal'
#функция проверки верности пароля
def check_pass():
    global current_widget, number_of_opened_frames
    params_file=open(file_name_with_params, "r")
    while True:
        line=params_file.readline()
        if not line:
            break
        check=""
        for i in range (0,9):
            check+=line[i]
        if check=="Password:":
            check=""
            for i in range (9,len(line)):
                check+=line[i]
            if check==current_widget.get():
                login_out()
                login_button['state']='disabled'
                user_label.configure(text="Admin")
                if number_of_opened_frames==2:
                    pages.tab(2,state="normal")
            else:
                current_widget.delete(0,tk.END)
                current_widget.insert(tk.END,"Uncorrect password")
    params_file.close()
#функция создания окна для входа в учетную запись
def login():
    global number_of_login_windows, current_window, current_widget
    if number_of_login_windows==0:
        number_of_login_windows+=1
        exit_button['state']='disable'
        
        login_window=tk.Tk()
        login_window.title("Login window")
        login_window.geometry(str(math.floor(GetSystemMetrics(0)/4))+'x'+str(math.floor(GetSystemMetrics(1)/5)))
        login_window.attributes('-toolwindow', True)
        login_window.protocol("WM_DELETE_WINDOW", login_out)
        current_window=login_window

        login_window_label_1=tk.Label(login_window, text="Enter your password:")
        login_window_label_1.pack(anchor=CENTER)

        login_window_entry_password=tk.Entry(login_window,justify=CENTER)
        login_window_entry_password.pack(expand=True,anchor=CENTER,fill="both")
        current_widget=login_window_entry_password

        login_window_button=tk.Button(login_window, text="Enter special mode", command=check_pass)
        login_window_button.pack(anchor=CENTER)
#конец раздела функций, связанных с регистрацией

#раздел функций, связанных с первой страницей
def get_path():
    global number_of_opened_frames
    result_page_progressbar.configure(value=0)
    result_page_label3.configure(text="Progressbar info")
    file_path=filedialog.askopenfilename()
    files_page_file_path['state']='normal'
    files_page_file_path.delete(0,END)
    pages.tab(1,state="normal")
    result_page_job_tracert.configure(state="normal")
    result_page_job_tracert.delete("0.0",tk.END)
    result_page_job_tracert.configure(state="disabled")
    pages.tab(1,state="disabled")
    pages.tab(2,state="normal")
    for i in tracert_page_tree.get_children():
        tracert_page_tree.delete(i)
    pages.tab(2,state="disabled")
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
            files_page_file_path.insert(END,file_path)
            files_page_text_from_file['state']='normal'
            files_page_text_from_file.delete("0.0",END)
            xml_file=open(file_path, "r")
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
                    files_page_text_from_file.insert(END,line)
            files_page_text_from_file["state"]='disabled'
            pages.tab(1,state='normal')
            number_of_opened_frames=2
            if login_button['state']=='disabled':
                pages.tab(2,state='normal')
                number_of_opened_frames=3
        else:
            files_page_file_path.insert(END,"Uncorrect file format...")
            files_page_text_from_file['state']='normal'
            files_page_text_from_file.delete("0.0",END)
            files_page_text_from_file.insert("0.0","File contents...")
            files_page_text_from_file["state"]='disabled'
            pages.tab(1,state='disabled')
            pages.tab(2,state='disabled')
    else:
        files_page_text_from_file['state']='normal'
        files_page_text_from_file.delete("0.0",END)
        files_page_text_from_file.insert("0.0","File contents...")
        files_page_text_from_file["state"]='disabled'
        files_page_file_path.insert(END,"Uncorrect path...")
        pages.tab(1,state='disabled')
        pages.tab(2,state='disabled')
    files_page_file_path['state']='disabled'
#конец раздела функций, связанных с первой страницей

#функция обработки модели по нажатию кнопки
def start_analyze():
    global tracert_page_tree, our_model, tracert_page_tree_srcollbar
    result_page_progressbar.configure(value=0)
    xml_file_adress=files_page_file_path.get()
    with open(xml_file_adress) as fp:
        root=BeautifulSoup(fp)
    if our_model!=None:
        del our_model
        our_model=None
        result_page_job_tracert.delete("0.0",tk.END)
        for i in tracert_page_tree.get_children():
            tracert_page_tree.delete(i)
    our_model=Model("Our model")
    our_model.Parse_model(root)
    pages.tab(2,state="normal")
    our_list_of_objects=our_model.Get_list_of_objects()
    for i in range(0,len(our_list_of_objects)):
        local_numbers=1000000+i*1000
        if our_list_of_objects[i].Get_type()=="uml:Class":
            object_name=our_list_of_objects[i].Get_name()
            tracert_page_tree.insert("",tk.END,iid=i,text=object_name)
            tracert_page_tree.insert(i,index=END,text="Type: Class")
            tracert_page_tree.insert(i,index=END,text="Id: "+our_list_of_objects[i].Get_id())
            tracert_page_tree.insert(i,index=END,text="Name: "+our_list_of_objects[i].Get_name())
            our_parents=our_list_of_objects[i].Get_parents_id()
            if our_parents==[] or our_parents==[None]:
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Parents:None")
            else:
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Parents")
                for j in range(0,len(our_parents)):
                    tracert_page_tree.insert(local_numbers,index=END,text="Parent: "+our_parents[j])
            our_params=our_list_of_objects[i].Get_list_of_parametres()
            local_numbers+=1
            if our_params==[]:
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Parametres:None")
            else:
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Parametres")
                for j in range(0,len(our_params)):
                    local_numbers+=1
                    if len(our_params[j])==3:
                        tracert_page_tree.insert(local_numbers-j-1,index=END,iid=local_numbers,text=our_params[j][2])
                        tracert_page_tree.insert(local_numbers,index=END,text="Visibility level: "+our_params[j][0])
                        tracert_page_tree.insert(local_numbers,index=END,text="Type: "+our_params[j][1])
                    elif len(our_params[j])==4:
                        tracert_page_tree.insert(local_numbers-j-1,index=END,iid=local_numbers,text=our_params[j][2])
                        tracert_page_tree.insert(local_numbers,index=END,text="Visibility level: "+our_params[j][0])
                        tracert_page_tree.insert(local_numbers,index=END,text="Type: "+our_params[j][1])
                        tracert_page_tree.insert(local_numbers,index=END,text="Inital value: "+our_params[j][3])
                    else:
                        tracert_page_tree.insert(local_numbers-j-1,index=END,iid=local_numbers,text=our_params[j][1])
                        tracert_page_tree.insert(local_numbers,index=END,text="Visibility level: "+our_params[j][0])
            our_funcs=our_list_of_objects[i].Get_list_of_functions()
            if our_funcs==[]:
                tracert_page_tree.insert(i,index=END,text="Functions:None")
            else:
                local_numbers+=1
                root_funcs_number=local_numbers
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Functions")
                for j in range(0,len(our_funcs)):
                    tracert_page_tree.insert(root_funcs_number,index=END,iid=local_numbers+1,text=our_funcs[j][2])
                    local_numbers+=1
                    tracert_page_tree.insert(local_numbers,index=END,text="Visibility level: "+our_funcs[j][0])
                    tracert_page_tree.insert(local_numbers,index=END,text="Type: "+our_funcs[j][1])
                    if len(our_funcs[j])==3:
                        tracert_page_tree.insert(local_numbers,index=END,text="Paramtetres: None")
                    else:
                        tracert_page_tree.insert(local_numbers,index=END,iid=local_numbers+1,text="Parametres")
                        local_numbers+=1
                        root_func_number=local_numbers
                        for k in range(3,len(our_funcs[j]),2):
                            tracert_page_tree.insert(root_func_number,index=END,iid=local_numbers+1,text=our_funcs[j][k+1])
                            tracert_page_tree.insert(local_numbers+1,index=END,text="Type: "+our_funcs[j][k])
                            local_numbers+=1
        if our_list_of_objects[i].Get_type()=="uml:Association":
            if our_list_of_objects[i].Get_name()=="None":
                tracert_page_tree.insert("",tk.END,iid=i,text="No name")
            else:
                tracert_page_tree.insert("",tk.END,iid=i,text=our_list_of_objects[i].Get_name())
            tracert_page_tree.insert(i,index=tk.END,text="Type: Association")
            tracert_page_tree.insert(i,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
            tracert_page_tree.insert(i,index=tk.END,text="Sender id: "+our_list_of_objects[i].Get_sender_class_id()+"("+str(our_model.Find_name_to_ip(our_list_of_objects[i].Get_sender_class_id()))+")")
            tracert_page_tree.insert(i,index=tk.END,text="Sender role: "+our_list_of_objects[i].Get_role_sender())
            current_string="Sender type: "
            current_string+=our_list_of_objects[i].Take_type_string_from_type_number(our_list_of_objects[i].Get_type_of_the_number_of_sender_class())
            tracert_page_tree.insert(i,index=tk.END,text=current_string)
            tracert_page_tree.insert(i,index=tk.END,text="Recipient id: "+our_list_of_objects[i].Get_recipient_class_id()+"("+str(our_model.Find_name_to_ip(our_list_of_objects[i].Get_recipient_class_id()))+")")
            tracert_page_tree.insert(i,index=tk.END,text="Recipient role: "+our_list_of_objects[i].Get_role_recipient())
            current_string="Recipient type: "
            current_string+=our_list_of_objects[i].Take_type_string_from_type_number(our_list_of_objects[i].Get_type_of_the_number_of_recipient_class())
            tracert_page_tree.insert(i,index=tk.END,text=current_string)
    if login_button['state']=='normal':
        pages.tab(2,state="disabled")
    return
#конец раздела с разными командами интерфейса

#создание окна приложения
main_window=tk.Tk()
main_window.title("Procrust")
main_window.attributes("-fullscreen", True)

#создаем заголовок для входа в учетную запись администратора/разработчика
login_frame=tk.Frame(main_window)

user_label=tk.Label(login_frame, text="User")
user_label.pack(side=LEFT)
login_button=tk.Button(login_frame, text="Login",command=login)
login_button.pack(side=LEFT)
exit_button=tk.Button(login_frame, text="Exit",command=exit_procrust)
exit_button.pack(side=RIGHT)

login_frame.pack()
#закончили создание заголовка для входа в учетную запись администратора/разработчика

#создание вкладок для работы с приложением
pages=ttk.Notebook(main_window)

files_page=tk.Frame(pages)
result_page=tk.Frame(pages)
tracert_page=tk.Frame(pages)
pages.add(files_page,text="Analyzed file")
pages.add(result_page,text="Analysis result",state="disabled")
pages.add(tracert_page,text="Tracert model",state="disabled")

pages.pack(expand = True, fill ="both")
#конец создания вкладок для работы с приложением

#элементы первой страницы приложения
files_page_label1=tk.Label(files_page, text="Choice your file with '.xml' format:")
files_page_label1.pack(anchor=tk.N)

files_page_file_path=tk.Entry(files_page,justify=CENTER)
files_page_file_path.pack(anchor=tk.N,fill="x")
files_page_file_path.insert(END,"File path...")
files_page_file_path['state']='disabled'

files_page_get_path=tk.Button(files_page,text="Select a file",command=get_path)
files_page_get_path.pack(anchor=tk.N)

files_page_text_from_file=tk.Text(files_page,wrap="word")
files_page_text_from_file.pack(expand=True,side=tk.LEFT,fill="both")
files_page_text_from_file.insert("0.0","File contents...")
files_page_text_from_file.configure(state="disabled")

files_page_text_from_file_scrollbar=tk.Scrollbar(files_page,orient="vertical",command = files_page_text_from_file.yview)
files_page_text_from_file_scrollbar.pack(side=tk.RIGHT,fill="y")
files_page_text_from_file["yscrollcommand"] = files_page_text_from_file_scrollbar.set
#конец элементов первой страницы приложения

#элементы второй страницы приложения
result_page_frame_result=tk.Frame(result_page)
result_page_frame_result.pack(expand=True,fill="both",anchor=tk.CENTER)

result_page_start_button=tk.Button(result_page_frame_result,text="Start the analysis",command=start_analyze)
result_page_start_button.pack(anchor=tk.NE,side=tk.TOP,fill="x")

result_page_label3=tk.Label(result_page_frame_result,text="Progressbar info")
result_page_label3.pack(anchor=tk.CENTER)

result_page_progressbar=ttk.Progressbar(result_page_frame_result,orient=tk.HORIZONTAL,length=math.floor(GetSystemMetrics(0)/2))
result_page_progressbar.pack(anchor=tk.CENTER)

result_page_label1=tk.Label(result_page_frame_result,text="Recommends, warnings and errors:")
result_page_label1.pack(anchor=tk.NW,side=LEFT)

result_page_tree=ttk.Treeview(result_page_frame_result,show="tree")
result_page_tree.pack(expand=True,fill="both")

result_page_frame_tracert=tk.Frame(result_page)
result_page_frame_tracert.pack(expand=True,fill="both",anchor=tk.CENTER)

result_page_label2=tk.Label(result_page_frame_tracert,text="Job tracing:")
result_page_label2.pack(anchor=tk.SW)

result_page_job_tracert=tk.Text(result_page_frame_tracert,state='disabled')
result_page_job_tracert.pack(sid=tk.LEFT,expand=True, fill="both")

result_page_job_tracert_scrollbar=tk.Scrollbar(result_page_frame_tracert,orient="vertical",command=result_page_job_tracert.yview)
result_page_job_tracert_scrollbar.pack(side=tk.RIGHT,fill="y")
result_page_job_tracert["yscrollcommand"] = result_page_job_tracert_scrollbar.set
#конец элементов второй страницы приложения

#элементы третьей страницы приложения
tracert_page_label1=tk.Label(tracert_page,text="Tracert_info:")
tracert_page_label1.pack(anchor=tk.NW)

tracert_page_frame=tk.Frame(tracert_page)
tracert_page_frame.pack(expand=True,fill="both")

tracert_page_tree=ttk.Treeview(tracert_page_frame,show="tree")
tracert_page_tree.heading("#0",text="Our model",anchor=tk.NW)
tracert_page_tree.pack(side=tk.LEFT,expand=True, fill="both")

tracert_page_tree_srcollbar=tk.Scrollbar(tracert_page_frame,orient="vertical",command=tracert_page_tree.yview)
tracert_page_tree_srcollbar.pack(side=tk.RIGHT,fill="y")
tracert_page_tree["yscrollcommand"] = tracert_page_tree_srcollbar.set
#конец элементов третьей страницы приложения

#отображение окна
main_window.mainloop()