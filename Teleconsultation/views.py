from django.shortcuts import render
from django.core.files.storage import FileSystemStorage


from Teleconsultation.MyLib import Ontology
from django import forms
import json

def Home(request):
    return render(request, "index.html")
def Admin(request):
    if(request.method=="POST"):
        for i in request.FILES:
            file=request.FILES[i]
            fs= FileSystemStorage()
            Name=fs.save(file.name,file)
            if i == "DiseasesJSON":
                Ontology.Disease.LoadJson(Name)
            elif i == "DiseasesCSV":
                Ontology.Disease.LoadCsv(Name)
            elif i == "DoctorsJSON":
                Ontology.Doctor.LoadJson(Name)
            elif i == "DoctorsCSV":
                Ontology.Doctor.LoadCsv(Name)
    return render(request,"Admin.html",{"Title":"Admin"})
def Consultaion(request):
    if(request.method=="POST"):
        Data=dict(request.POST.lists())
        Data={
            "FirstName" : Data["FirstName"][0],
            "LastName" : Data["LastName"][0],
            "Gender" : Data["Gender"][0],
            "Age" : Data["Age"][0],
            "District" : Data["Daira"][0],
            "Province" : Data["Wilaya"][0],
            "Symptoms" : Data["Symptoms"],
            "Started" : Data["SymptomsTime"][0]
        }
        Data['Symptoms']=[Ontology.ont[i] for i in Data['Symptoms']]
        patient=Ontology.Patient.Create(Data)
        Data['Symptoms']=[i.Symptom_Name for i in Data['Symptoms']]
        return render(request, "Result.html",{"Title":"Result","PatientID":patient.name,"Data":Data})
    else:
        symptoms=Ontology.Symptom.GetAll()
        return render(request, "Consultaion.html",{"Title":"Consultaion", "Symptoms":symptoms})
def Results(request):
    ID=None
    ID=request.GET.dict().get("PatientID")
    if(ID==None):
        return render(request, "SignIn.html",{"Title":"SignIn" })
    else:
        data=Ontology.Patient.FindOne(ID)
        if(data==None):
            return render(request, "SignIn.html",{"Title":"SignIn" ,"Message":"This ID Doesn't Exist","PatientID":ID})
        else:
            return render(request, "Result.html",{"Title":"Result" ,"PatientID":ID,"Data":data})  
def Learn(request,Learn_id):
    return render(request, "Learn/"+Learn_id+".html",{"Title":"Learn"})
def Doctor(request):
    #request.GET.dict()
    if(request.method=="POST"):
        data=request.POST.dict()
        print(data)
        ID=data.get("DoctorID")
        if(ID==None or Ontology.ont[ID]==None):
            return render(request, "Doctor.html",{"Title":"Doctor-SignIn","Message":"Enter a valid Doctor ID"})
        doctor=Ontology.ont[ID]
        if data.get("PatientID"):
            Ontology.Consultation.Create(data)
        return render(request, "ConsultD.html",{"Title":"Doctor-Consutling","Doctor":{
            "FullName": doctor.FirstName+" "+doctor.LastName,
            "ID":ID
        },"Patiens":Ontology.Patient.GetUnchecked()})
    else:
        return render(request, "Doctor.html",{"Title":"Doctor-SignIn"})

