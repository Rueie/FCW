from distutils.command.check import check
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
    parents_id=[]
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
        if number_of_parent>len(self.parents_id) or len(self.parents_id)==0:
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
        result_page_label3.configure(text="Reading the model...",foreground="#000000")
        result_page_label4.configure(text="",foreground="#000000")
        result_page_progressbar.configure(maximum=10000)
        for child in local_root.descendants:
            if child!="\n":
                if child.name=="xmi:Extension":
                    break
                elif child.name=="packagedelement" or child.name=="nestedclassifier" or child.name=="lifeline" or child.name=="message" or child.name=="fragment" or child.name=="ownedattribute":
                    if child["xmi:type"]=="uml:Class" or child["xmi:type"]=="uml:Component":
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
                        del new_obj_class
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page_job_tracert.configure(state="disabled")
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
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page_job_tracert.configure(state="disabled")
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:UseCase":
                        new_use_case=obj_Use_Case()
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,"Use case '"+child["name"]+"' being read\n")
                        new_use_case.Set_id(child["xmi:id"])
                        new_use_case.Set_name(child["name"])
                        new_use_case.Set_type(child["xmi:type"])
                        result_page_job_tracert.insert(tk.END,"Use case '"+child["name"]+"' is read\n")
                        new_use_case.Parse_use_case(child)
                        result_page_job_tracert.insert(tk.END,"Use case '"+child["name"]+"' is added to the model\n")
                        self.Add_obj_to_model(new_use_case)
                        result_page_job_tracert.insert(tk.END,"Use case '"+child["name"]+"' added to the model\n")
                        del new_use_case
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page_job_tracert.configure(state="disabled")
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:Actor":
                        new_actor=Object()
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,"Actor '"+child["name"]+"' being read\n")
                        new_actor.Set_name(child["name"])
                        new_actor.Set_id(child["xmi:id"])
                        new_actor.Set_type(child["xmi:type"])
                        if len(child.contents)!=0:
                           for i in range(0,len(child.contents)):
                            if child.contents[i].name=="generalization":
                                new_actor.Add_parents(child.contents[i]["general"])
                        result_page_job_tracert.insert(tk.END,"Actor '"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,"Actor '"+child["name"]+"' is added to the model\n")
                        self.Add_obj_to_model(new_actor)
                        result_page_job_tracert.insert(tk.END,"Actor '"+child["name"]+"' added to the model\n")
                        del new_actor
                        result_page_job_tracert.configure(state="disabled")
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:Lifeline":
                        new_obj_lifeLine=obj_LifeLine()
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,"Lifeline '"+child["name"]+"' being read\n")
                        new_obj_lifeLine.Set_id(child["xmi:id"])
                        new_obj_lifeLine.Set_type(child["xmi:type"])
                        new_obj_lifeLine.Set_name(child["name"])
                        new_obj_lifeLine.Set_connected_object_id(child["represents"])
                        result_page_job_tracert.insert(tk.END,"Lifeline '"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,"Lifeline '"+child["name"]+"' is added to the model\n")
                        self.Add_obj_to_model(new_obj_lifeLine)
                        result_page_job_tracert.insert(tk.END,"Lifeline '"+child["name"]+"' added to the model\n")
                        del new_obj_lifeLine
                        result_page_job_tracert.configure(state="disabled")
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:OccurrenceSpecification":
                        our_point=Object()
                        our_point.Set_id(child["xmi:id"])
                        our_point.Set_type(child["xmi:type"])
                        our_point.Set_name(child["covered"])
                        self.Add_obj_to_model(our_point)
                        del our_point
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:Message":
                        our_obj_time_connection=obj_Time_connection()
                        result_page_job_tracert.configure(state="normal")
                        current_name=""
                        if child.has_attr("name")==True:
                            current_name=child["name"]
                        else:
                            current_name=child["xmi:id"]
                        result_page_job_tracert.insert(tk.END,"Lifeline connection '"+current_name+"' being read\n")
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
                        result_page_job_tracert.insert(tk.END,"Lifeline connection '"+current_name+"' is read\n")
                        result_page_job_tracert.insert(tk.END,"Lifeline connection '"+current_name+"' is added to the model\n")
                        self.Add_obj_to_model(our_obj_time_connection)
                        result_page_job_tracert.insert(tk.END,"Lifeline connection '"+current_name+"' added to the model\n")
                        del our_obj_time_connection
                        result_page_job_tracert.configure(state="disabled")
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:Property" and child.has_attr("name")==False and child.has_attr("visibility")==False:
                        our_life_line=None
                        for i in range(0,len(self.list_of_objects)):
                            if self.list_of_objects[i].Get_type()=="uml:Lifeline" and self.list_of_objects[i].Get_connected_object_id()==child["xmi:id"]:
                                our_life_line=self.list_of_objects[i]
                                break
                        if len(child.contents)!=0:
                            our_life_line.Set_connected_object_id(child.contents[1]["xmi:idref"])
                    if child["xmi:type"]=="uml:CombinedFragment":
                        our_alternative=obj_Alternative()
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,"Alternative '"+child["name"]+"' being read\n")
                        our_alternative.Set_id(child["xmi:id"])
                        our_alternative.Set_type(child["xmi:type"])
                        our_alternative.Set_name(child["name"])
                        our_alternative.Set_type_alternative(child["interactionoperator"])
                        our_alternative.Parse_alternative(child)
                        result_page_job_tracert.insert(tk.END,"Alternative '"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,"Alternative '"+child["name"]+"' is added to the model\n")
                        self.Add_obj_to_model(our_alternative)
                        result_page_job_tracert.insert(tk.END,"Alternative '"+child["name"]+"' added to the model\n")
                        del our_alternative
                        result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                        result_page_job_tracert.configure(state="disabled")
                        result_page.after(1,result_page.update())
                    if child["xmi:type"]=="uml:InstanceSpecification":
                        for i in range(0,len(self.list_of_objects)):
                            if self.list_of_objects[i].Get_type()=="uml:Lifeline":
                                if child["xmi:id"]==self.list_of_objects[i].Get_connected_object_id():
                                    self.list_of_objects[i].Set_connected_object_id(child["classifier"])
                                    break
                    result_page_job_tracert.yview_moveto('1.0')
        result_page_progressbar.configure(maximum=len(self.list_of_objects))
        result_page_progressbar.configure(value=0)
        result_page_label3.configure(text="Post-processing of classes, components, actors, lifelines...")
        #конечный этап анализа распаршенных элементов модели
        for i in range(0,len(self.list_of_objects)):
            current_node=self.list_of_objects[i]
            if current_node.Get_type()=="uml:Class":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Class '"+current_node.Get_name()+"' is post-analyzed\n")
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
            elif current_node.Get_type()=="uml:Component":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Component '"+current_node.Get_name()+"' is post-analyzed\n")
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.insert(tk.END,"Changes related to the component '"+current_node.Get_name()+"' have been made to the model\n")
                result_page_job_tracert.configure(state="disabled")
                result_page_job_tracert.yview_moveto('1.0')
                result_page.after(1,result_page.update())
            elif current_node.Get_type()=="uml:Actor":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Actor '"+current_node.Get_name()+"' is post-analyzed\n")
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.insert(tk.END,"Changes related to the actor '"+current_node.Get_name()+"' have been made to the model\n")
                result_page_job_tracert.configure(state="disabled")
                result_page_job_tracert.yview_moveto('1.0')
            elif current_node.Get_type()=="uml:Lifeline":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Lifeline '"+current_node.Get_name()+"' is post-analyzed\n")
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.insert(tk.END,"Changes related to the lifeline '"+current_node.Get_name()+"' have been made to the model\n")
                result_page_job_tracert.configure(state="disabled")
                result_page.after(1,result_page.update())
                result_page_job_tracert.yview_moveto('1.0')
        result_page_label3.configure(text="Post-processing of use cases...")
        for i in range(0,len(self.list_of_objects)):
            current_node=self.list_of_objects[i]
            if current_node.Get_type()=="uml:UseCase":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Use case '"+current_node.Get_name()+"' is post-analyzed\n")
                if len(current_node.Get_list_of_extentions())!=0:
                    our_list_of_extentions=current_node.Get_list_of_extentions()
                    for j in range(0,len(our_list_of_extentions)):
                        self.Find_obj_to_ip(our_list_of_extentions[j]).Add_extention(current_node.Get_id())
                        current_node.Delete_extention(j)
                result_page_job_tracert.insert(tk.END,"Changes related to the association '"+current_node.Get_name()+"' have been made to the model\n")
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
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
                    for j in range(0,len(sender.Get_list_of_parametres())):
                        if sender.Get_parent(j)==recipient.Get_id():
                            sender.Delete_parent(j)
                            break
                    result_page_job_tracert.insert(tk.END,"Changes related to the association '"+current_node.Get_id()+"' have been made to the model\n")
                elif self.Find_obj_to_ip(current_node.Get_sender_class_id()).Get_type()=="uml:Actor":
                    flag=False
                    our_actors=self.Find_obj_to_ip(current_node.Get_recipient_class_id()).Get_list_of_actors()
                    for j in range(0,len(our_actors)):
                        if our_actors[j]==current_node.Get_sender_class_id():
                            flag=True
                            break
                    if flag==False:
                        self.Find_obj_to_ip(current_node.Get_recipient_class_id()).Add_actor(current_node.Get_sender_class_id())
                    result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.configure(state="disabled")
                result_page.after(1,result_page.update())
                result_page_job_tracert.yview_moveto('1.0')
        result_page_label3.configure(text="Post-processing of lifeline connections...")
        for i in range(0,len(self.list_of_objects)):
            if self.list_of_objects[i].Get_type()=="uml:Message":
                result_page_job_tracert.configure(state="normal")
                result_page_job_tracert.insert(tk.END,"Lifeline connection '"+current_node.Get_name()+"' is post-analyzed\n")
                if self.list_of_objects[i].Get_id_point_from()!="None":
                    our_point=self.Find_obj_to_ip(self.list_of_objects[i].Get_id_point_from())
                    self.list_of_objects[i].Set_id_point_from(our_point.Get_name())
                if self.list_of_objects[i].Get_id_point_to()!="None":
                    our_point=self.Find_obj_to_ip(self.list_of_objects[i].Get_id_point_to())
                    self.list_of_objects[i].Set_id_point_to(our_point.Get_name())
                result_page_job_tracert.insert(tk.END,"Changes related to the lifeline connection '"+current_node.Get_name()+"' have been made to the model\n")
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.yview_moveto('1.0')
                result_page_job_tracert.configure(state="disabled")
                result_page.after(1,result_page.update())
        result_page_label3.configure(text="Cleaning the model from auxiliary elements...")
        i=0
        while i<len(self.list_of_objects):
            if self.list_of_objects[i].Get_type()=="uml:OccurrenceSpecification":
                result_page_job_tracert.configure(state="normal")
                self.list_of_objects.pop(i)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page_job_tracert.configure(state="disabled")
                result_page.after(1,result_page.update())
            else:
                i+=1
        result_page_label3.configure(text="Model processing is completed",foreground="#3B973B")
        result_page_progressbar.configure(value=result_page_progressbar["maximum"])
        return
    def Check_model(self):
        global_number=0
        check_list=[]
        check_position=0
        new_check_elem=[]
        if len(self.list_of_objects)!=0:
        #проверка на повторение имен
            result_page_label4.configure(text="Search for warnings...")
            result_page_progressbar.configure(maximum=len(self.list_of_objects))
            result_page_progressbar.configure(value=0)
            result_page.after(1,result_page.update())
            for i in range(0,len(self.list_of_objects)):
                flag_check=False
                if self.list_of_objects[i].Get_type()=="uml:Class" or self.list_of_objects[i].Get_type()=="uml:UseCase" or self.list_of_objects[i].Get_type()=="uml:Actor" or self.list_of_objects[i].Get_type()=="uml:Component":
                    for j in range(0,len(check_list)):
                        if check_list[j][0]==self.list_of_objects[i].Get_name():
                            flag_check=True
                            check_position=j
                    if flag_check==True:
                        check_list[check_position].append(self.list_of_objects[i].Get_id())
                    else:
                        new_check_elem=[]
                        new_check_elem.append(self.list_of_objects[i].Get_name())
                        new_check_elem.append(self.list_of_objects[i].Get_id())
                        check_list.append(new_check_elem)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            result_page_progressbar.configure(maximum=len(check_list))
            result_page_progressbar.configure(value=0)
            result_page.after(1,result_page.update())
            for i in range(0,len(check_list)):
                if len(check_list[i])>2:
                    global_number+=1
                    result_page_tree.insert("",tk.END,iid=global_number,text="WARNING: several objects with same names")
                    result_page_tree.insert(global_number,index=tk.END,text="Obects name: "+check_list[i][0])
                    for j in range(1,len(check_list[i])):
                        result_page_tree.insert(global_number,index=tk.END,text="Object id: "+check_list[i][j])
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
        #проверка на связность с другими объектами 
            result_page_label4.configure(text="Search for unrelated elements...")
            check_list=[]
            result_page_progressbar.configure(maximum=len(self.list_of_objects))
            result_page_progressbar.configure(value=0)
            result_page.after(1,result_page.update())
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_type()=="uml:Class" or self.list_of_objects[i].Get_type()=="uml:UseCase" or self.list_of_objects[i].Get_type()=="uml:Actor" or self.list_of_objects[i].Get_type()=="uml:Lifeline":
                    new_check_elem=[]
                    new_check_elem.append(self.list_of_objects[i].Get_id())
                    check_list.append(new_check_elem)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            new_check_elem=[]
            result_page_progressbar.configure(maximum=result_page_progressbar["maximum"]+len(check_list)*2)
            result_page_progressbar.configure(value=0)
            result_page.after(1,result_page.update())
            for i in range(0,len(check_list)):
                new_check_elem=[]
                for j in range(0,len(check_list)):
                    new_check_elem.append(0)
                check_list[i].append(new_check_elem)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_type()=="uml:Association":
                    sender=self.list_of_objects[i].Get_sender_class_id()
                    recipient=self.list_of_objects[i].Get_recipient_class_id()
                    sender_number=0
                    recipient_number=0
                    for j in range(0,len(check_list)):
                        if check_list[j][0]==sender:
                            sender_number=j
                        elif check_list[j][0]==recipient:
                            recipient_number=j
                    check_list[sender_number][1][recipient_number]=1
                    check_list[recipient_number][1][sender_number]=1
                elif self.list_of_objects[i].Get_type()=="uml:Class" and len(self.list_of_objects[i].Get_parents_id())!=0:
                    parents_list=self.list_of_objects[i].Get_parents_id()
                    for j in range(0,len(parents_list)):
                        sender=parents_list[j]
                        recipient=self.list_of_objects[i].Get_id()
                    sender_number=0
                    recipient_number=0
                    for j in range(0,len(check_list)):
                        if check_list[j][0]==sender:
                            sender_number=j
                        elif check_list[j][0]==recipient:
                            recipient_number=j
                    check_list[sender_number][1][recipient_number]=1
                    check_list[recipient_number][1][sender_number]=1
                elif self.list_of_objects[i].Get_type()=="uml:UseCase":
                    sender=""
                    recipient=""
                    sender_number=0
                    recipient_number=0
                    include_list=self.list_of_objects[i].Get_list_of_includions()
                    extention_list=self.list_of_objects[i].Get_list_of_extentions()
                    parents_list=self.list_of_objects[i].Get_parents_id()
                    if len(include_list)!=0:
                        recipient=self.list_of_objects[i].Get_id()
                        for j in range(0,len(include_list)):
                            sender=include_list[j]
                            for j in range(0,len(check_list)):
                                if check_list[j][0]==sender:
                                    sender_number=j
                                elif check_list[j][0]==recipient:
                                    recipient_number=j
                            check_list[sender_number][1][recipient_number]+=1
                            check_list[recipient_number][1][sender_number]+=1
                    if len(extention_list)!=0:
                        recipient=self.list_of_objects[i].Get_id()
                        for j in range(0,len(extention_list)):
                            sender=extention_list[j]
                            for j in range(0,len(check_list)):
                                if check_list[j][0]==sender:
                                    sender_number=j
                                elif check_list[j][0]==recipient:
                                    recipient_number=j
                            check_list[sender_number][1][recipient_number]+=1
                            check_list[recipient_number][1][sender_number]+=1
                    if len(parents_list)!=0:
                        recipient=self.list_of_objects[i].Get_id()
                        for j in range(0,len(parents_list)):
                            sender=parents_list[j]
                            for j in range(0,len(check_list)):
                                if check_list[j][0]==sender:
                                    sender_number=j
                                elif check_list[j][0]==recipient:
                                    recipient_number=j
                            check_list[sender_number][1][recipient_number]+=1
                            check_list[recipient_number][1][sender_number]+=1
                elif self.list_of_objects[i].Get_type()=="uml:Message":
                    sender=self.list_of_objects[i].Get_id_point_from()
                    recipient=self.list_of_objects[i].Get_id_point_to()
                    sender_number=-1
                    recipient_number=-1
                    for j in range(0,len(check_list)):
                        if check_list[j][0]==sender:
                            sender_number=j
                        elif check_list[j][0]==recipient:
                            recipient_number=j
                    if sender_number!=-1 and recipient_number!=-1:
                        check_list[sender_number][1][recipient_number]+=1
                        check_list[recipient_number][1][sender_number]+=1
                elif self.list_of_objects[i].Get_type()=="uml:Lifeline":
                    sender=self.list_of_objects[i].Get_id()
                    recipient=self.list_of_objects[i].Get_connected_object_id()
                    sender_number=-1
                    recipient_number=-1
                    for j in range(0,len(check_list)):
                        if check_list[j][0]==sender:
                            sender_number=j
                        elif check_list[j][0]==recipient:
                            recipient_number=j
                    if sender_number!=-1 and recipient_number!=-1:
                        check_list[sender_number][1][recipient_number]+=1
                        check_list[recipient_number][1][sender_number]+=1
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            flag_check=False
            for i in range(0,len(check_list)):
                counter=0
                for j in range(0,len(check_list[i][1])):
                    if check_list[i][1][j]>0:
                        counter+=1
                if counter==0:
                    global_number+=1
                    result_page_job_tracert.configure(state="normal")
                    result_page_label4.configure(text="Was found the unrelated element.",foreground="#FF0000")
                    result_page_job_tracert.configure(state="disabled")
                    result_page_tree.insert("",tk.END,iid=global_number,text="ERROR: object with no connections")
                    result_page_tree.insert(global_number,index=tk.END, text="Name: "+self.Find_obj_to_ip(check_list[i][0]).Get_name())
                    result_page_tree.insert(global_number,index=tk.END, text="Id: "+self.Find_obj_to_ip(check_list[i][0]).Get_id())
                    return False
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
        #проверка на циклы наследования
            result_page_label4.configure(text="Search for inheritance cycles...")
            check_list=[]
            result_page_progressbar.configure(maximum=len(self.list_of_objects))
            result_page_progressbar.configure(value=0)
            result_page.after(1,result_page.update())
            for i in range(0,len(self.list_of_objects)):
                if self.list_of_objects[i].Get_type()=="uml:Class" or self.list_of_objects[i].Get_type()=="uml:Component" or self.list_of_objects[i].Get_type()=="uml:UseCase" or self.list_of_objects[i].Get_type()=="uml:Actor":
                    new_check_elem=[]
                    new_check_elem.append(self.list_of_objects[i].Get_id())
                    new_check_elem.append([])
                    check_list.append(new_check_elem)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            result_page_progressbar.configure(maximum=len(check_list)*2)
            result_page_progressbar.configure(value=0)
            result_page.after(1,result_page.update())
            for i in range(0,len(check_list)):
                for j in range(0,len(check_list)):
                    check_list[i][1].append(0)
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            for i in range(0,len(check_list)):
                sender=self.Find_obj_to_ip(check_list[i][0])
                our_list_of_parents=sender.Get_parents_id()
                if len(our_list_of_parents)!=0:
                    for j in range(0,len(our_list_of_parents)):
                        position_parent=-1
                        for k in range(0,len(check_list)):
                            if our_list_of_parents[j]==check_list[k][0]:
                                position_parent=k
                                break
                        if position_parent!=-1:
                            check_list[i][1][position_parent]=1
                result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
                result_page.after(1,result_page.update())
            stack=[]
            number_of_object=0
            position=0
            while True:
                #1-есть связь
                #2-уже прошли данную вершину
                #stack-стек из фершин, показывающий нам цикл
                if len(stack)==0 and position==len(check_list):
                    number_of_object+=1
                    position=0
                elif position==len(check_list):
                    position=number_of_object
                    number_of_object=stack.pop()
                    check_list[number_of_object][1][position]=1
                    position+=1
                elif check_list[number_of_object][1][position]==1:
                    check_list[number_of_object][1][position]=2
                    stack.append(number_of_object)
                    number_of_object=position
                    position=0
                elif check_list[number_of_object][1][position]==2:
                    stack.append(number_of_object)
                    lust_number=number_of_object
                    for i in range(len(stack)-2,0,-1):
                        if stack[i]==lust_number and i!=0:
                            while stack[0]!=lust_number:
                                stack.pop(0)
                    global_number+=1
                    result_page_tree.insert("",tk.END,iid=global_number,text="ERROR: inheritance cycle found")
                    for i in range(len(stack)):
                        result_page_tree.insert(global_number,index=tk.END, text="Name: "+self.Find_obj_to_ip(check_list[stack[i]][0]).Get_name())
                        result_page_tree.insert(global_number,index=tk.END, text="Id: "+self.Find_obj_to_ip(check_list[stack[i]][0]).Get_id())
                    result_page_job_tracert.configure(state="normal")
                    result_page_label4.configure(text="Was found the inheritance cycle.",foreground="#FF0000")
                    result_page_job_tracert.configure(state="disabled")
                    return False
                    #position=stack.pop()
                    #number_of_object=stack.pop()
                    #check_list[number_of_object][1][position]=1
                    #position+=1
                else:
                    position+=1
                if number_of_object==len(check_list):
                    break
        result_page_job_tracert.configure(state="normal")
        result_page_progressbar.configure(value=result_page_progressbar["maximum"])
        result_page_label4.configure(text="The error analysis has been completed.",foreground="#3B973B")
        result_page_job_tracert.configure(state="disabled")
        result_page.after(1,result_page.update())
        return True
    
class obj_Class(Object):
    list_of_parametres=[]
    list_of_functions=[]
    def __init__(self):
        self.parents_id=[]
        self.list_of_parametres=[]
        self.list_of_functions=[]
        return
    def Add_param(self,new_param):
        self.list_of_parametres.append(new_param)
        return
    def Add_func(self,new_func):
        self.list_of_functions.append(new_func)
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
            if child.name=="generalization":
                flag=False
                for i in range(0,len(self.parents_id)):
                    if self.parents_id[i]==child["general"]:
                        flag=True
                        break
                if flag==False:
                    self.Add_parents(child["general"])
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
    
class obj_Use_Case(Object):
    list_of_actors=[]
    #list_of_parents=[]
    list_of_includions=[]#что входит в данный Use Case (обязательно)
    list_of_extentions=[]#что расширяет данный Use Case (необязательно, но возможно)
    def __init__(self):
        self.list_of_actors=[]
        #self.list_of_parents=[]
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
    #def Add_parent(self,new_parent):
    #    self.list_of_parents.append(new_parent)
    #    return
    #def Change_parent(self,number_of_parent,changed_parent):
    #    if number_of_parent<0 or (number_of_parent-1)>len(self.list_of_parents):
    #        return None
    #    else:
    #        self.list_of_parents[number_of_parent]=changed_parent
    #    return
    #def Get_info_about_parent(self,number_of_parent):
    #    if number_of_parent<0 or (number_of_parent-1)>len(self.list_of_parents):
    #        return None
    #    else:
    #        return self.list_of_parents[number_of_parent]
    #def Get_list_of_parents(self):
    #    return self.list_of_parents
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
                self.list_of_extentions.append(child["extendedcase"])
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
    direction=""
    type_connection=""
    kind_connection=""
    def __init__(self):
        self.id_point_from=""
        self.id_point_to=""
        self.direction=""
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
    def Set_direction(self,new_direction):
        self.direction=new_direction
        return
    def Get_direction(self):
        return self.direction
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
                        new_alernative_variavnt.append(elements.contents[1]["body"])
                    elif elements.name=="fragment":
                        new_alernative_variavnt.append(elements["covered"])
                self.Add_alternative(new_alernative_variavnt)
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
    result_page_label3.configure(text="Progressbar info",foreground="#000000")
    result_page_label4.configure(text="",foreground="#000000")
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
    for i in result_page_tree.get_children():
        result_page_tree.delete(i)
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
    result_page_label3.configure(foreground="#000000")
    result_page_label4.configure(text="",foreground="#000000")
    xml_file_adress=files_page_file_path.get()
    with open(xml_file_adress) as fp:
        root=BeautifulSoup(fp)
    if our_model!=None:
        del our_model
        our_model=None
        result_page_job_tracert.delete("0.0",tk.END)
        for i in tracert_page_tree.get_children():
            tracert_page_tree.delete(i)
        for i in result_page_tree.get_children():
            result_page_tree.delete(i)
    our_model=Model("Our model")
    our_model.Parse_model(root)
    pages.tab(2,state="normal")
    our_list_of_objects=our_model.Get_list_of_objects()
    for i in range(0,len(our_list_of_objects)):
        local_numbers=1000000+i*1000
        if our_list_of_objects[i].Get_type()=="uml:Class" or our_list_of_objects[i].Get_type()=="uml:Component":
            object_name=our_list_of_objects[i].Get_name()
            tracert_page_tree.insert("",tk.END,iid=i,text=object_name)
            if our_list_of_objects[i].Get_type()=="uml:Class":
                tracert_page_tree.insert(i,index=END,text="Type: Class")
            else:
                tracert_page_tree.insert(i,index=END,text="Type: Component")
            tracert_page_tree.insert(i,index=END,text="Id: "+our_list_of_objects[i].Get_id())
            tracert_page_tree.insert(i,index=END,text="Name: "+our_list_of_objects[i].Get_name())
            our_parents=our_list_of_objects[i].Get_parents_id()
            if our_parents==[] or our_parents==[None]:
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Parents:None")
            else:
                tracert_page_tree.insert(i,index=END,iid=local_numbers,text="Parents")
                for j in range(0,len(our_parents)):
                    tracert_page_tree.insert(local_numbers,index=END,text="Parent: "+our_model.Find_name_to_ip(our_parents[j]))
                    tracert_page_tree.insert(local_numbers,index=END,text="Parent id: "+our_parents[j])
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
        if our_list_of_objects[i].Get_type()=="uml:Actor":
            tracert_page_tree.insert("",tk.END,iid=i,text=our_list_of_objects[i].Get_name())
            tracert_page_tree.insert(i,index=tk.END,text="Type: Actor")
            tracert_page_tree.insert(i,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
            if len(our_list_of_objects[i].Get_parents_id())==0:
                tracert_page_tree.insert(i,index=tk.END,text="Parents: None")
            else:
                our_list_of_parents=our_list_of_objects[i].Get_parents_id()
                local_numbers+=1
                tracert_page_tree.insert(i,tk.END,iid=local_numbers,text="Parents")
                for j in range(0,len(our_list_of_parents)):
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent: "+our_model.Find_name_to_ip(our_list_of_parents[j]))
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent id: "+our_list_of_parents[j])
        if our_list_of_objects[i].Get_type()=="uml:UseCase":
            tracert_page_tree.insert("",tk.END,iid=i,text=our_list_of_objects[i].Get_name())
            tracert_page_tree.insert(i,index=tk.END,text="Type: Use Case")
            tracert_page_tree.insert(i,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
            if len(our_list_of_objects[i].Get_list_of_actors())==0:
                tracert_page_tree.insert(i,index=tk.END,text="Actors: None")
            else:
                local_numbers+=1
                tracert_page_tree.insert(i,iid=local_numbers,index=tk.END,text="Actors")
                our_list_of_actors=our_list_of_objects[i].Get_list_of_actors()
                for j in range(0,len(our_list_of_actors)):
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent: "+our_model.Find_name_to_ip(our_list_of_actors[j]))
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent id: "+our_list_of_actors[j])
            if len(our_list_of_objects[i].Get_parents_id())==0:
                tracert_page_tree.insert(i,index=tk.END,text="Parents: None")
            else:
                local_numbers+=1
                tracert_page_tree.insert(i,iid=local_numbers,index=tk.END,text="Parents")
                our_list_of_parents=our_list_of_objects[i].Get_parents_id()
                for j in range(0,len(our_list_of_parents)):
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent: "+our_model.Find_name_to_ip(our_list_of_parents[j]))
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent id: "+our_list_of_parents[j])
            if len(our_list_of_objects[i].Get_list_of_includions())==0:
                tracert_page_tree.insert(i,index=tk.END,text="Includions: None")
            else:
                local_numbers+=1
                tracert_page_tree.insert(i,iid=local_numbers,index=tk.END,text="Includions")
                our_list_of_includions=our_list_of_objects[i].Get_list_of_includions()
                for j in range(0,len(our_list_of_includions)):
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Includion: "+our_model.Find_name_to_ip(our_list_of_includions[j]))
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Includion id: "+our_list_of_includions[j])
            if len(our_list_of_objects[i].Get_list_of_extentions())==0:
                tracert_page_tree.insert(i,index=tk.END,text="Extentions: None")
            else:
                local_numbers+=1
                tracert_page_tree.insert(i,iid=local_numbers,index=tk.END,text="Extentions")
                our_list_of_extentions=our_list_of_objects[i].Get_list_of_extentions()
                for j in range(0,len(our_list_of_extentions)):
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Extention: "+our_model.Find_name_to_ip(our_list_of_extentions[j]))
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Extention id: "+our_list_of_extentions[j])
        if our_list_of_objects[i].Get_type()=="uml:Lifeline":
            tracert_page_tree.insert("",tk.END,iid=i,text=our_list_of_objects[i].Get_name())
            tracert_page_tree.insert(i,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
            tracert_page_tree.insert(i,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
            our_string="Connected object: "+our_list_of_objects[i].Get_connected_object_id()+"("
            if our_model.Find_name_to_ip(our_list_of_objects[i].Get_connected_object_id())!=None:
                our_string+=our_model.Find_name_to_ip(our_list_of_objects[i].Get_connected_object_id())
            else:
                our_string+="None"
            our_string+=")"
            tracert_page_tree.insert(i,index=tk.END,text=our_string)
        if our_list_of_objects[i].Get_type()=="uml:Message":
            if our_list_of_objects[i].Get_name()=="None":
                tracert_page_tree.insert("",tk.END,iid=i,text="No name")
            else:
                tracert_page_tree.insert("",tk.END,iid=i,text=our_list_of_objects[i].Get_name())
            tracert_page_tree.insert(i,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
            tracert_page_tree.insert(i,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
            tracert_page_tree.insert(i,index=tk.END,text="Id sender lifeline: "+our_list_of_objects[i].Get_id_point_from()+"("+our_model.Find_name_to_ip(our_list_of_objects[i].Get_id_point_from())+")")
            tracert_page_tree.insert(i,index=tk.END,text="Id recipient lifeline: "+our_list_of_objects[i].Get_id_point_to()+"("+our_model.Find_name_to_ip(our_list_of_objects[i].Get_id_point_to())+")")
            tracert_page_tree.insert(i,index=tk.END,text="Type connection: "+our_list_of_objects[i].Get_type_connection())
            tracert_page_tree.insert(i,index=tk.END,text="Kind connection: "+our_list_of_objects[i].Get_kind_connection())
        if our_list_of_objects[i].Get_type()=="uml:CombinedFragment":
            tracert_page_tree.insert("",tk.END,iid=i,text=our_list_of_objects[i].Get_name())
            tracert_page_tree.insert(i,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
            tracert_page_tree.insert(i,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
            local_numbers+=1
            tracert_page_tree.insert(i,tk.END,iid=local_numbers,text="Covered lifelines")
            our_list_covered_lifelines=our_list_of_objects[i].Get_list_of_covered_lifeline()
            for j in range(0,len(our_list_covered_lifelines)):
                tracert_page_tree.insert(local_numbers,index=tk.END,text="ID lifeline: "+our_list_covered_lifelines[j])
            our_list_of_alternatives=our_list_of_objects[i].Get_list_of_alternatives()
            local_numbers+=1
            tracert_page_tree.insert(i,tk.END,iid=local_numbers,text="Alternatives")
            for j in range(0,len(our_list_of_alternatives)):
                tracert_page_tree.insert(local_numbers,tk.END,iid=local_numbers+1+j,text=our_list_of_alternatives[j][0])
                tracert_page_tree.insert(local_numbers+1+j,index=tk.END,text="Id sender lifeline: "+our_list_of_alternatives[j][1])
                tracert_page_tree.insert(local_numbers+1+j,index=tk.END,text="Id recipient lifeline: "+our_list_of_alternatives[j][2])
    if login_button['state']=='normal':
        pages.tab(2,state="disabled")
    if our_model.Check_model()==False:
        return
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
result_page_label3.pack(anchor=tk.N)

result_page_label4=tk.Label(result_page_frame_result,text="")
result_page_label4.pack(anchor=tk.N)

result_page_progressbar=ttk.Progressbar(result_page_frame_result,orient=tk.HORIZONTAL,length=math.floor(GetSystemMetrics(0)/2))
result_page_progressbar.pack(anchor=tk.CENTER)

result_page_label1=tk.Label(result_page_frame_result,text="Recommends, warnings and errors:")
result_page_label1.pack(anchor=tk.NW,side=LEFT)

result_page_tree=ttk.Treeview(result_page_frame_result,show="tree")
result_page_tree.pack(side=tk.LEFT,expand=True,fill="both")

result_page_tree_srollbar=tk.Scrollbar(result_page_frame_result,orient="vertical",command=result_page_tree.yview)
result_page_tree_srollbar.pack(side=tk.LEFT,fill="y")
result_page_tree["yscrollcommand"] = result_page_tree_srollbar.set

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