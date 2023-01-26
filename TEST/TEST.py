from distutils.command.check import check
import math
import tkinter as tk
from tkinter import CENTER, END, LEFT, RIGHT, ttk
from tkinter import filedialog
from win32api import GetSystemMetrics
from bs4 import BeautifulSoup
from rnnmorph.predictor import RNNMorphPredictor

#file_name_with_params="D:\Diplom\Params.txt"
number_of_login_windows=0;
current_window=0
current_widget=0
number_of_opened_frames=1#the number of open tabs of the main window
our_model=None
predictor = RNNMorphPredictor(language="en")

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
    list_of_diagrams=[]
    def __init__(self):
        self.list_of_diagrams=[]
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
    def Find_object_in_model(self,object_id):
        for i in range(0,len(self.list_of_diagrams)):
            if self.list_of_diagrams[i].Find_object(object_id)!=None:
                return self.list_of_diagrams[i].Find_object(object_id)
        return None
    def Parse_model(self,root):
        result_page_label3.configure(text="Reading model from XML file",foreground="#000000")
        result_page_progressbar.configure(value=0)
        local_root=root
        for child in local_root.descendants:
            if child.name=="packagedelement":
                local_root=child
                break
        self.Set_name(local_root["name"])
        for child in local_root.children:
            if child!='\n':
                result_page_label3.configure(text="Reading model from XML file:\nDigaram:"+child["name"])
                our_diagram=obj_Diagram(self)
                our_diagram.Set_name(child["name"])
                our_diagram.Parse_diaram(child)
                self.Add_diagram(our_diagram)
                del our_diagram
        #the final stage of the analysis of the expanded elements of the model
        self.Completion_of_the_model_formation()
        result_page_label3.configure(text="The model is successfully read and formed",foreground="#3C7F31")
    def Completion_of_the_model_formation(self):
        result_page_progressbar.configure(maximum=len(self.list_of_diagrams))
        for i in range(0,len(self.list_of_diagrams)):
            result_page_label3.configure(text="Post analize model:\nDiagram:"+self.list_of_diagrams[i].Get_name())
            self.list_of_diagrams[i].Completion_of_the_diagram_formation()
            result_page_progressbar.configure(value=result_page_progressbar["value"]+1)
            result_page.after(1,result_page.update())
        self.Search_for_recommendations()
        return 
    def Search_for_recommendations(self):
        for i in range(0,len(self.list_of_diagrams)):
            self.list_of_diagrams[i].Search_for_recommendations()
        return

class obj_Diagram(Object):
    list_of_objects=[]
    model=None
    list_of_nouns=[]
    def __init__(self,init_model):
        self.list_of_objects=[]
        self.model=init_model
        self.list_of_nouns=[]
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
        if flag_life_line==True:
            self.Set_type("Sequence diagram")
        elif flag_use_case==True:
            self.Set_type("Use Case diagram")
        elif flag_actor==False:
            self.Set_type("Class diagram")
        else:
            self.Set_type("Use Case diagram")
        return
    def Parse_diaram(self,root):
        local_root=root
        for child in local_root.descendants:
            if child!="\n":
                if child.name=="xmi:Extension":
                    break
                elif child.name=="packagedelement" or child.name=="nestedclassifier" or child.name=="lifeline" or child.name=="message" or child.name=="fragment" or child.name=="ownedattribute" or child.name=="ownedcomment":
                    if child["xmi:type"]=="uml:Class" or child["xmi:type"]=="uml:Component" or child["xmi:type"]=="uml:Interface" or child["xmi:type"]=="uml:AssociationClass":
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" '"+child["name"]+"' being read\n")
                        new_obj_class=obj_Class()
                        new_obj_class.Set_id(child["xmi:id"])
                        new_obj_class.Set_name(child["name"])
                        new_obj_class.Set_type(child["xmi:type"])
                        new_obj_class.Parse_class(child)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" '"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" '"+child["name"]+"' is added to the model\n")
                        self.Add_object(new_obj_class)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" '"+child["name"]+"' added to the model\n")
                        del new_obj_class
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
                        self.Add_object(new_obj_connection)
                        result_page_job_tracert.insert(tk.END,tracert_string+"' added to the model\n")
                        del new_obj_connection
                    if child["xmi:type"]=="uml:UseCase":
                        new_use_case=obj_Use_Case()
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' being read\n")
                        new_use_case.Set_id(child["xmi:id"])
                        new_use_case.Set_name(child["name"])
                        new_use_case.Set_type(child["xmi:type"])
                        new_use_case.Parse_use_case(child)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is added to the model\n")
                        self.Add_object(new_use_case)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' added to the model\n")
                        del new_use_case
                    if child["xmi:type"]=="uml:Actor":
                        new_actor=Object()
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' being read\n")
                        new_actor.Set_name(child["name"])
                        new_actor.Set_id(child["xmi:id"])
                        new_actor.Set_type(child["xmi:type"])
                        if len(child.contents)!=0:
                           for i in range(0,len(child.contents)):
                            if child.contents[i].name=="generalization":
                                new_actor.Add_parents(child.contents[i]["general"])
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is added to the model\n")
                        self.Add_object(new_actor)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' added to the model\n")
                        del new_actor
                    if child["xmi:type"]=="uml:Lifeline":
                        new_obj_lifeLine=obj_LifeLine()
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' being read\n")
                        new_obj_lifeLine.Set_id(child["xmi:id"])
                        new_obj_lifeLine.Set_type(child["xmi:type"])
                        new_obj_lifeLine.Set_name(child["name"])
                        new_obj_lifeLine.Set_connected_object_id(child["represents"])
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is added to the model\n")
                        self.Add_object(new_obj_lifeLine)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' added to the model\n")
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
                        result_page_job_tracert.configure(state="normal")
                        current_name=""
                        if child.has_attr("name")==True:
                            current_name=child["name"]
                        else:
                            current_name=child["xmi:id"]
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+current_name+"' being read\n")
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
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+current_name+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+current_name+"' is added to the model\n")
                        self.Add_object(our_obj_time_connection)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+current_name+"' added to the model\n")
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
                        result_page_job_tracert.configure(state="normal")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' being read\n")
                        our_alternative.Set_id(child["xmi:id"])
                        our_alternative.Set_type(child["xmi:type"])
                        our_alternative.Set_name(child["name"])
                        our_alternative.Set_type_alternative(child["interactionoperator"])
                        our_alternative.Parse_alternative(child)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' is added to the model\n")
                        self.Add_object(our_alternative)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["name"]+"' added to the model\n")
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
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["body"]+"' being read\n")
                        our_comment.Set_id(child["xmi:id"])
                        our_comment.Set_type(child["xmi:type"])
                        our_comment.Set_name(child["body"])
                        if len(child.contents)!=0:
                            our_comment.Add_parents(child.contents[1]["xmi:idref"])
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["body"]+"' is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["body"]+"' is added to the model\n")
                        self.Add_object(our_comment)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+"'"+child["body"]+"' added to the model\n")
                        del our_comment
                    if child["xmi:type"]=="uml:Dependency" or child["xmi:type"]=="uml:Realization":
                        our_dependency=obj_Connection()
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" being read\n")
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
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" is read\n")
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" is added to the model\n")
                        self.Add_object(our_dependency)
                        result_page_job_tracert.insert(tk.END,child["xmi:type"]+" being read\n")
                        del our_dependency
                    result_page.after(1,result_page.update())
                    result_page_job_tracert.yview_moveto('1.0')
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
                            our_extention=[]
                            our_extention.append(current_node.Get_id())
                            for k in range(0,len(self.list_of_objects)):
                                if self.list_of_objects[k].Get_type()=="uml:Comment":
                                    parents_list=self.list_of_objects[k].Get_parents_id()
                                    for l in range(0,len(parents_list)):
                                        if parents_list[l]==our_list_of_extentions[j][0]:
                                            our_extention.append(self.list_of_objects[k].Get_name())
                                            break
                            self.Find_object(our_list_of_extentions[j][1]).Add_extention(our_extention)
                            current_node.Delete_extention(j)
                if current_node.Get_type()=="uml:Class":
                    current_node.Set_type("System boundary")
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
                            current_association=self.model.Find_object_in_model(current_param[0])
                            if current_association.Get_recipient_class_id()==current_param[1]:
                                current_association.Set_recipient_class_id(current_param[2])
                                current_association.Set_flag_composite(True)
                        else:
                            current_string=current_param[1]
                            if current_string[0:4]=="EAID":
                                current_node.Change_param(j,1,self.model.Find_object_in_model(current_param[1]).Get_name())               
                    for j in range(0,len(current_node.Get_list_of_functions())):
                        current_func=current_node.Get_info_about_func(j)
                        for k in range(0,len(current_func)):
                            current_string=current_func[k]
                            if current_string[0:4]=="EAID":
                                current_node.Change_func(j,k,self.model.Find_object_in_model(current_string).Get_name())
        list_of_objects=self.list_of_objects
        for i in range(0,len(list_of_objects)):
            current_node=list_of_objects[i]
            if current_node.Get_type()=="uml:Association":
                if current_node.Get_flag_composite()==True:
                    current_node.Set_type("uml:Composition")
                    sender=self.model.Find_object_in_model(current_node.Get_sender_class_id())
                    recipient=self.model.Find_object_in_model(current_node.Get_recipient_class_id())
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
                    if current_node.Get_flag_shared()==False:
                        sender.Set_independent_existence(False)
                    else:
                        current_node.Set_type("uml:Aggregation")
                    for j in range(0,len(sender.Get_list_of_parametres())):
                        if sender.Get_parent(j)==recipient.Get_id():
                            sender.Delete_parent(j)
                            break
                elif self.model.Find_object_in_model(current_node.Get_sender_class_id()).Get_type()=="uml:Actor":
                    flag=False
                    our_actors=self.model.Find_object_in_model(current_node.Get_recipient_class_id()).Get_list_of_actors()
                    for j in range(0,len(our_actors)):
                        if our_actors[j]==current_node.Get_sender_class_id():
                            flag=True
                            break
                    if flag==False:
                        self.model.Find_object_in_model(current_node.Get_recipient_class_id()).Add_actor(current_node.Get_sender_class_id())
        return
    def Search_for_recommendations(self):
        global predictor
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
                            result_page_tree.insert("",index=tk.END,text="It is recommended to create a sequence diagram for the '"+self.list_of_objects[i].Get_name()+"' use case")
                        else:
                            list_of_actors=self.list_of_objects[i].Get_list_of_actors()
                            sequence_diagram_objects=self.model.Get_diagram(number_of_an_existing_diagram).Get_list_of_objects()
                            for j in range(0,len(list_of_actors)):
                                flag_extention=False
                                for k in range(0,len(sequence_diagram_objects)):
                                    if sequence_diagram_objects[k].Get_type()=="uml:Actor" and sequence_diagram_objects[k].Get_name()==self.model.Find_object_in_model(list_of_actors[j]).Get_name():
                                        flag_extention=True
                                        break
                                if flag_extention==False:
                                    result_page_tree.insert("",index=tk.END,text="It is recommended to add the actor '"+self.model.Find_object_in_model(list_of_actors[j]).Get_name()+"' to the sequence diagram '"+self.model.Get_diagram(number_of_an_existing_diagram).Get_name()+"'")

                    current_fraze=self.list_of_objects[i].Get_name()
                    words=[]
                    begin=0
                    end=0
                    for j in range(0,len(current_fraze)):
                        if current_fraze[j]==" ":
                            end=j
                            if begin!=0:
                                begin+=1
                            words.append(current_fraze[begin:end])
                            begin=end
                        elif j==(len(current_fraze)-1):
                            end=j
                            words.append(current_fraze[begin+1:end+1])
                    words=predictor.predict(words)
                    for j in range(0,len(words)):
                        if words[j].pos=="NOUN":
                            flag_extention=False
                            for k in range(0,len(self.list_of_nouns)):
                                if self.list_of_nouns[k][0]==words[j].normal_form:
                                    self.list_of_nouns[k][1]+=1
                                    flag_extention=True
                                    break
                            if flag_extention==False:
                                new_noun=[]
                                new_noun.append(words[j].normal_form)
                                new_noun.append(1)
                                self.list_of_nouns.append(new_noun)
            list_of_class_diagams=[]
            for i in range(0,len(self.model.Get_list_of_diagrams())):
                if self.model.Get_diagram(i).Get_type()=="Class diagram":
                    list_of_class_diagams.append(self.model.Get_diagram(i))
            for i in range(0,len(self.list_of_nouns)):                
                if self.list_of_nouns[i][1]>2:
                    flag_exist=False
                    for j in range(0,len(list_of_class_diagams)):
                        list_of_objects=list_of_class_diagams[j].Get_list_of_objects()
                        for k in range(0,len(list_of_objects)):
                            if list_of_objects[k].Get_name()==self.list_of_nouns[i][0]:
                                flag_exist=True
                                break
                    if flag_exist==False:
                        result_page_tree.insert("",index=tk.END,text="It is recommended to create a class named '"+self.list_of_nouns[i][0]+"'")
        return
  
class obj_Class(Object):
    list_of_parametres=[]#[visibility,type,name,calculability,initial value]
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
                    if our_elem.has_attr("href"):
                        new_attribute.append(our_elem["href"])
                    else:
                        new_attribute.append(our_elem["xmi:idref"])
                    if child.has_attr("name"):
                        new_attribute.append(child["name"])
                    else:
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
                        new_alernative_variavnt.append(elements.contents[1]["body"])
                    elif elements.name=="fragment":
                        new_alernative_variavnt.append(elements["covered"])
                self.Add_alternative(new_alernative_variavnt)
        return
#end of the xml class section

#section with different interface commands
#application closure processing function
def exit_procrust():
    global number_of_login_windows, current_window
    if number_of_login_windows==1:
        login_out
    main_window.destroy()
    exit

#section of functions related to registration
#the function of exiting the account login window
def login_out():
    global number_of_login_windows, current_window
    current_window.destroy()
    number_of_login_windows=0
    current_window=0
    exit_button['state']='normal'
#password verification function
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
#the function of creating a window to log in to an account
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
#end of the registration-related functions section

#section of functions related to the first page
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
#end of the functions section related to the first page

#the function of processing the model at the touch of a button
def start_analyze():
    global tracert_page_tree, our_model, tracert_page_tree_srcollbar
    result_page_progressbar.configure(value=0)
    result_page_job_tracert['state']="normal"
    result_page_job_tracert.delete("0.0",tk.END)
    result_page_job_tracert['state']="disabled"
    result_page_label3.configure(foreground="#000000")
    result_page_label4.configure(text="",foreground="#000000")
    xml_file_adress=files_page_file_path.get()
    result_page_start_button['state']="disabled"
    with open(xml_file_adress) as fp:
        root=BeautifulSoup(fp)
    if our_model!=None:
        del our_model
        our_model=None
        for i in tracert_page_tree.get_children():
            tracert_page_tree.delete(i)
        for i in result_page_tree.get_children():
            result_page_tree.delete(i)
    our_model=Model()
    our_model.Parse_model(root)
    pages.tab(2,state="normal")
    for k in range(0,len(our_model.Get_list_of_diagrams())):
        tracert_page_tree.insert("",tk.END,iid=k,text=our_model.Get_diagram(k).Get_name())
        tracert_page_tree.insert(k,index=tk.END,text="Type: "+our_model.Get_diagram(k).Get_type())
        our_list_of_objects=our_model.Get_diagram(k).Get_list_of_objects()
        for i in range(0,len(our_list_of_objects)):
            local_numbers=100000*(k+1)+i*100
            if our_list_of_objects[i].Get_type()=="uml:Class" or our_list_of_objects[i].Get_type()=="uml:Component" or our_list_of_objects[i].Get_type()=="uml:Interface" or our_list_of_objects[i].Get_type()=="uml:AssociationClass":
                object_name=our_list_of_objects[i].Get_name()
                tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=object_name)
                tracert_page_tree.insert(local_numbers,index=END,text="Tyep: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=END,text="Id: "+our_list_of_objects[i].Get_id())
                tracert_page_tree.insert(local_numbers,index=END,text="Independent existence: "+str(our_list_of_objects[i].Get_independent_existence()))
                if our_list_of_objects[i].Get_type()=="uml:AssociationClass":
                    tracert_page_tree.insert(local_numbers,index=END,text="Sender class: "+our_list_of_objects[i].Get_sender_class_id()+"("+our_model.Find_object_in_model(our_list_of_objects[i].Get_sender_class_id()).Get_name()+")")
                    tracert_page_tree.insert(local_numbers,index=END,text="Recipient class: "+our_list_of_objects[i].Get_recipient_class_id()+"("+our_model.Find_object_in_model(our_list_of_objects[i].Get_recipient_class_id()).Get_name()+")")
                our_parents=our_list_of_objects[i].Get_parents_id()
                if our_parents==[] or our_parents==[None]:
                    tracert_page_tree.insert(local_numbers,index=END,text="Parents:None")
                else:
                    local_numbers+=1
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=END,iid=local_numbers,text="Parents")
                    for j in range(0,len(our_parents)):
                        tracert_page_tree.insert(local_numbers,index=END,text="Parent: "+our_model.Find_object_in_model(our_parents[j]).Get_name())
                        tracert_page_tree.insert(local_numbers,index=END,text="Parent id: "+our_parents[j])
                our_params=our_list_of_objects[i].Get_list_of_parametres()
                local_numbers+=1
                if our_params==[]:
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=END,iid=local_numbers,text="Parametres:None")
                else:
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=END,iid=local_numbers,text="Parametres")
                    for j in range(0,len(our_params)):
                        local_numbers+=1
                        tracert_page_tree.insert(local_numbers-j-1,index=END,iid=local_numbers,text=our_params[j][2])
                        tracert_page_tree.insert(local_numbers,index=END,text="Visibility level: "+our_params[j][0])
                        tracert_page_tree.insert(local_numbers,index=END,text="Type: "+our_params[j][1])
                        tracert_page_tree.insert(local_numbers,index=END,text="Calculability: "+our_params[j][3])
                        tracert_page_tree.insert(local_numbers,index=END,text="Inital value: "+our_params[j][4])
                our_funcs=our_list_of_objects[i].Get_list_of_functions()
                if our_funcs==[]:
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=END,text="Functions:None")
                else:
                    local_numbers+=1
                    root_funcs_number=local_numbers
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=END,iid=local_numbers,text="Functions")
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
                            for l in range(3,len(our_funcs[j]),2):
                                tracert_page_tree.insert(root_func_number,index=END,iid=local_numbers+1,text=our_funcs[j][l+1])
                                tracert_page_tree.insert(local_numbers+1,index=END,text="Type: "+our_funcs[j][l])
                                local_numbers+=1
            if our_list_of_objects[i].Get_type()=="uml:Association" or our_list_of_objects[i].Get_type()=="uml:Composition" or our_list_of_objects[i].Get_type()=="uml:Aggregation" or our_list_of_objects[i].Get_type()=="uml:Dependency" or our_list_of_objects[i].Get_type()=="uml:Realization":
                if our_list_of_objects[i].Get_name()=="None":
                    our_name=""
                    our_name+=our_model.Find_object_in_model(our_list_of_objects[i].Get_sender_class_id()).Get_name()+"->"+our_model.Find_object_in_model(our_list_of_objects[i].Get_recipient_class_id()).Get_name()
                    tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_name)
                else:
                    tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Sender id: "+our_list_of_objects[i].Get_sender_class_id()+"("+str(our_model.Find_object_in_model(our_list_of_objects[i].Get_sender_class_id()).Get_name())+")")
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Sender role: "+our_list_of_objects[i].Get_role_sender())
                current_string="Sender type: "
                current_string+=our_list_of_objects[i].Take_type_string_from_type_number(our_list_of_objects[i].Get_type_of_the_number_of_sender_class())
                tracert_page_tree.insert(local_numbers,index=tk.END,text=current_string)
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Recipient id: "+our_list_of_objects[i].Get_recipient_class_id()+"("+str(our_model.Find_object_in_model(our_list_of_objects[i].Get_recipient_class_id()).Get_name())+")")
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Recipient role: "+our_list_of_objects[i].Get_role_recipient())
                current_string="Recipient type: "
                current_string+=our_list_of_objects[i].Take_type_string_from_type_number(our_list_of_objects[i].Get_type_of_the_number_of_recipient_class())
                tracert_page_tree.insert(local_numbers,index=tk.END,text=current_string)
            if our_list_of_objects[i].Get_type()=="uml:Actor":
                tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
                if len(our_list_of_objects[i].Get_parents_id())==0:
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Parents: None")
                else:
                    our_list_of_parents=our_list_of_objects[i].Get_parents_id()
                    local_numbers+=1
                    tracert_page_tree.insert(local_numbers-1,tk.END,iid=local_numbers,text="Parents")
                    for j in range(0,len(our_list_of_parents)):
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent: "+our_model.Find_object_in_model(our_list_of_parents[j]).Get_name())
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent id: "+our_list_of_parents[j])
            if our_list_of_objects[i].Get_type()=="uml:UseCase":
                tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
                if len(our_list_of_objects[i].Get_list_of_actors())==0:
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="Actors: None")
                else:
                    local_numbers+=1
                    tracert_page_tree.insert(100000*(k+1)+i*100,iid=local_numbers,index=tk.END,text="Actors")
                    our_list_of_actors=our_list_of_objects[i].Get_list_of_actors()
                    for j in range(0,len(our_list_of_actors)):
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent: "+our_model.Find_object_in_model(our_list_of_actors[j]).Get_name())
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent id: "+our_list_of_actors[j])
                if len(our_list_of_objects[i].Get_parents_id())==0:
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=tk.END,text="Parents: None")
                else:
                    local_numbers+=1
                    tracert_page_tree.insert(100000*(k+1)+i*100,iid=local_numbers,index=tk.END,text="Parents")
                    our_list_of_parents=our_list_of_objects[i].Get_parents_id()
                    for j in range(0,len(our_list_of_parents)):
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent: "+our_model.Find_object_in_model(our_list_of_parents[j]).Get_name())
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Parent id: "+our_list_of_parents[j])
                if len(our_list_of_objects[i].Get_list_of_includions())==0:
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=tk.END,text="Includions: None")
                else:
                    local_numbers+=1
                    tracert_page_tree.insert(100000*(k+1)+i*100,iid=local_numbers,index=tk.END,text="Includions")
                    our_list_of_includions=our_list_of_objects[i].Get_list_of_includions()
                    for j in range(0,len(our_list_of_includions)):
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Includion: "+our_model.Find_object_in_model(our_list_of_includions[j]).Get_name())
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Includion id: "+our_list_of_includions[j])
                if len(our_list_of_objects[i].Get_list_of_extentions())==0:
                    tracert_page_tree.insert(100000*(k+1)+i*100,index=tk.END,text="Extentions: None")
                else:
                    local_numbers+=1
                    tracert_page_tree.insert(100000*(k+1)+i*100,iid=local_numbers,index=tk.END,text="Extentions")
                    our_list_of_extentions=our_list_of_objects[i].Get_list_of_extentions()
                    for j in range(0,len(our_list_of_extentions)):
                        tracert_page_tree.insert(local_numbers,index=tk.END,text="Extention: "+our_list_of_extentions[j][0]+"("+our_model.Find_object_in_model(our_list_of_extentions[j][0]).Get_name()+")")
                        if len(our_list_of_extentions[j])==2:
                            tracert_page_tree.insert(local_numbers,index=tk.END,text="Extention condition: "+our_list_of_extentions[j][1])
                        else:
                            tracert_page_tree.insert(local_numbers,index=tk.END,text="Extention condition: None")
            if our_list_of_objects[i].Get_type()=="System boundary":
                tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
            if our_list_of_objects[i].Get_type()=="uml:Lifeline":
                tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
                our_string="Connected object: "+our_list_of_objects[i].Get_connected_object_id()+"("
                if our_model.Find_object_in_model(our_list_of_objects[i].Get_connected_object_id())!=None:
                    our_string+=our_model.Find_object_in_model(our_list_of_objects[i].Get_connected_object_id()).Get_name()+")"+"["+our_model.Find_object_in_model(our_list_of_objects[i].Get_connected_object_id()).Get_type()+"]"
                else:
                    our_string+="None)"
                tracert_page_tree.insert(local_numbers,index=tk.END,text=our_string)
            if our_list_of_objects[i].Get_type()=="uml:Message":
                if our_list_of_objects[i].Get_name()=="None":
                    tracert_page_tree.insert(k,tk.END,iid=local_numbers,text="No name")
                else:
                    tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id sender lifeline: "+our_list_of_objects[i].Get_id_point_from()+"("+our_model.Find_object_in_model(our_list_of_objects[i].Get_id_point_from()).Get_name()+")")
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id recipient lifeline: "+our_list_of_objects[i].Get_id_point_to()+"("+our_model.Find_object_in_model(our_list_of_objects[i].Get_id_point_to()).Get_name()+")")
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type connection: "+our_list_of_objects[i].Get_type_connection())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Kind connection: "+our_list_of_objects[i].Get_kind_connection())
            if our_list_of_objects[i].Get_type()=="uml:CombinedFragment":
                tracert_page_tree.insert(k,tk.END,iid=local_numbers,text=our_list_of_objects[i].Get_name())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Type: "+our_list_of_objects[i].Get_type())
                tracert_page_tree.insert(local_numbers,index=tk.END,text="Id: "+our_list_of_objects[i].Get_id())
                local_numbers+=1
                tracert_page_tree.insert(100000*(k+1)+i*100,tk.END,iid=local_numbers,text="Covered lifelines")
                our_list_covered_lifelines=our_list_of_objects[i].Get_list_of_covered_lifeline()
                for j in range(0,len(our_list_covered_lifelines)):
                    tracert_page_tree.insert(local_numbers,index=tk.END,text="ID lifeline: "+our_list_covered_lifelines[j]+"("+our_model.Find_object_in_model(our_list_covered_lifelines[j]).Get_name()+")")
                our_list_of_alternatives=our_list_of_objects[i].Get_list_of_alternatives()
                local_numbers+=1
                tracert_page_tree.insert(100000*(k+1)+i*100,tk.END,iid=local_numbers,text="Alternatives")
                for j in range(0,len(our_list_of_alternatives)):
                    tracert_page_tree.insert(local_numbers,tk.END,iid=local_numbers+1+j,text=our_list_of_alternatives[j][0])
                    tracert_page_tree.insert(local_numbers+1+j,index=tk.END,text="Id sender lifeline: "+our_list_of_alternatives[j][1]+"("+our_model.Find_object_in_model(our_list_of_alternatives[j][1]).Get_name()+")")
                    tracert_page_tree.insert(local_numbers+1+j,index=tk.END,text="Id recipient lifeline: "+our_list_of_alternatives[j][2]+"("+our_model.Find_object_in_model(our_list_of_alternatives[j][2]).Get_name()+")")
    result_page_start_button['state']="normal"
    if login_button['state']=='normal':
        pages.tab(2,state="disabled")
    return
#end of the section with different interface commands

#creating an application window
main_window=tk.Tk()
main_window.title("Procrust")
main_window.attributes("-fullscreen", True)

#creating a header to log in to the administrator/developer account
login_frame=tk.Frame(main_window)

user_label=tk.Label(login_frame, text="User")
user_label.pack(side=LEFT)
login_button=tk.Button(login_frame, text="Login",command=login)
login_button.pack(side=LEFT)
exit_button=tk.Button(login_frame, text="Exit",command=exit_procrust)
exit_button.pack(side=RIGHT)

login_frame.pack()
#finished creating the header to log in to the administrator/developer account

#creating tabs for working with the application
pages=ttk.Notebook(main_window)

files_page=tk.Frame(pages)
result_page=tk.Frame(pages)
tracert_page=tk.Frame(pages)
pages.add(files_page,text="Analyzed file")
pages.add(result_page,text="Analysis result",state="disabled")
pages.add(tracert_page,text="Tracert model",state="disabled")

pages.pack(expand = True, fill ="both")
#end of creating tabs for working with the application

#elements of the first page of the application
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
#end of the elements of the first page of the application

#elements of the second page of the application
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
#end of the elements of the second page of the application

#elements of the third page of the application
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
#end of the elements of the third page of the application

#window display
main_window.mainloop()