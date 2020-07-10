OntologyFile = "Files/Ontology.owl"
RdfFile = "Files/Ontology.rdf"
from owlready2 import default_world,get_ontology,Thing,DataProperty,FunctionalProperty,ObjectProperty
from Teleconsultation.MyLib.Queries import *
import datetime
def SaveOnto():
    open(RdfFile,"w+")
    graphe = default_world.as_rdflib_graph()
    graphe.serialize(RdfFile,"turtle")
    default_world.save()
    ont.save(file = OntologyFile, format = "rdfxml")
    return graphe
default_world.set_backend(filename = "db2.sqlite3", exclusive = False)
ont=get_ontology("https://YoucefMadadi.com/Teleconsultation")
with ont :
    class Symptom(Thing):
        @staticmethod
        def Create(Symp):
           symptom = Symptom()
           symptom.Symptom_Name = Symp
           return symptom
        @staticmethod
        def GetAll():
            graphe = default_world.as_rdflib_graph()
            res= [ [i[0].replace("https://YoucefMadadi.com/Teleconsultation#",""),str(i[1])] for i in graphe.query(Queries.All_Symptoms) ]
            return res
    class Symptom_Name(DataProperty, FunctionalProperty):
        domain = [Symptom]
        range  = [str]
    class Disease(Thing):
        @staticmethod
        def CreateMany(Diseases):
            if Diseases:
                for disease in Diseases:
                    Disease.Create(disease)
        @staticmethod
        def Create(Data):
            disease = Disease()
            disease.Disease_Name = Data["Name"]
            disease.Disease_Code = Data["Code"]
            for symp in Data["Symptoms"]:
                disease.Causes.append(Symptom.Create(symp))
            return disease
        @staticmethod
        def LoadCsv(File):
            import csv
            try:
                data=list(csv.DictReader(open("Files/"+File) ,restkey="Symptoms", delimiter=',', quotechar='"')) 
                Disease.CreateMany( data)
                SaveOnto()
                return True
            except:
                print("Wrong Format of csv,  delimiter is , and quotechar is \"")
                return None
        @staticmethod
        def LoadJson(File):
            import json
            try:
                Disease.CreateMany( json.loads(open("Files/"+File).read()))
                SaveOnto()
                return True
            except:
                print("this File not a correct Json")
                return None
    class Disease_Name(DataProperty, FunctionalProperty):
        domain = [Disease]
        range  = [str]
    class Disease_Code(DataProperty, FunctionalProperty):
        domain = [Disease]
        range  = [str] 
    class Person(Thing):
        pass
    class Has(ObjectProperty):
        domain    = [Person]
        range     = [Symptom]
    class Patient(Person):
        equivalent_to = [ Person & Has.some(Symptom)]
        @staticmethod
        def Create(Data):
            id="P_"+Data["FirstName"]+Data["Age"]+Data["LastName"]
            length=0
            ID=id
            while(ont[ID]!=None):
                ID=id+str(length)
                length+=1
            patient=Patient(ID)
            patient.FirstName = Data["FirstName"]
            patient.LastName = Data["LastName"]
            patient.Gender = Data["Gender"]
            patient.Age = int(Data["Age"])
            patient.District = Data["District"]
            patient.Province = Data["Province"]
            patient.Has=Data["Symptoms"]
            patient.Chronic_diseases=Data["Chronic"]
            patient.Treatments=Data["Treatments"]
            Started=Data["Started"].split("-")
            Started=[int(v) for v in Started]
            Started=datetime.date(*Started)
            patient.Started = Started
            SaveOnto()
            return patient
        @staticmethod
        def FindOne(PatientID):
            patient=ont[PatientID]
            if(patient==None):
                return None
            Symp=[i.Symptom_Name for i in patient.Has]
            consultation={}
            if(patient.Affected!=None):
                doctor=patient.Affected.Wrote_by
                consultation={
                    "Note":patient.Affected.Note,
                    "Suggestions":patient.Affected.Suggestions,
                    "Doctor":doctor.FirstName+" "+doctor.LastName
                }
            return {
                "FirstName" :patient.FirstName,
                "LastName" :patient.LastName,
                "Gender" :patient.Gender,
                "Age" :patient.Age,
                "District" :patient.District,
                "Province" :patient.Province,
                "Started" : str(patient.Started),
                "Symptoms": Symp,
                "Chronic" : patient.Chronic_diseases,
                "Treatments" : patient.Treatments,
                "Consultation":consultation
            }
        @staticmethod
        def GetUnchecked():
            graphe = default_world.as_rdflib_graph()
            result= {}
            query = [[str(j) for j in i] for i in graphe.query(Queries.Unchecked)]
            for q in query:
                a=dict(zip(["PatientID","FirstName","LastName","Gender","Age","District","Province","Chronic","Treatments","Started","Symptoms"],q))
                a["PatientID"]=a["PatientID"].replace("https://YoucefMadadi.com/Teleconsultation#","")
                try:
                    result[a["PatientID"]]["Symptoms"].append(a["Symptoms"])
                except:
                    result[a["PatientID"]]=a
                    result[a["PatientID"]]["Symptoms"]=[ a["Symptoms"] ]
            return result.values()
            #return [[str(j) for j in i] for i in graphe.query(Queries["Unchecked"])]
    class is_Sick_with(ObjectProperty):
        domain    = [Patient]
        range     = [Disease]
    class Doctor(Person):
        @staticmethod
        def Create(Data):
            doctor=Doctor(Data["DoctorID"])
            doctor.FirstName = Data["FirstName"]
            doctor.LastName = Data["LastName"]
            doctor.Gender = Data["Gender"]
            doctor.Age = int(Data["Age"])
            doctor.District = Data["District"]
            doctor.Province = Data["Province"]
            SaveOnto()
            return doctor
        @staticmethod
        def CreateMany(Doctors):
            if Doctors:
                for doctor in Doctors:
                    Doctor.Create(doctor)
        @staticmethod
        def LoadCsv(File):
            import csv
            try:
                Doctor.CreateMany( list(csv.DictReader(open("Files/"+File) , delimiter=',', quotechar='"')) )
                SaveOnto()
                return True
            except:
                print("Wrong Format of csv,  delimiter is , and quotechar is \"")
                return None
        @staticmethod
        def LoadJson(File):
            import json
            try:
                Doctor.CreateMany(  json.loads(open("Files/"+File).read()) )
                SaveOnto()
                return True
            except:
                print("this File not a correct Json")
                return None
    class Consulted(ObjectProperty, FunctionalProperty):
        domain    = [Doctor]
        range     = [Patient]
    class Consultation(Thing):
        @staticmethod
        def Create(Data):
            consultation = Consultation()
            doctor=ont[Data["DoctorID"]]
            patient=ont[Data["PatientID"]]
            consultation.Affected_by=patient
            patient.Affected=consultation
            doctor.Wrote=consultation
            consultation.Wrote_by=doctor
            doctor.Consulter=patient
            consultation.Note=Data["Note"]
            consultation.Suggestions=Data["Suggestions"]
            SaveOnto()
            return consultation
    class Wrote(ObjectProperty,FunctionalProperty):
        domain    = [Doctor]
        range     = [Consultation]
    class Wrote_by(ObjectProperty,FunctionalProperty):
        domain    = [Consultation]
        range     = [Doctor]
        inverse_property = Wrote
    class Affected(ObjectProperty,FunctionalProperty):
        domain    = [Patient]
        range     = [Consultation] 
    class Affected_by(ObjectProperty,FunctionalProperty):
        domain    = [Consultation]
        range     = [Patient] 
        inverse_property = Affected
    class Note(DataProperty, FunctionalProperty):
        domain=[Consultation]
        range=[str]
    class Suggestions(DataProperty, FunctionalProperty):
        domain=[Consultation]
        range=[str]
    class FirstName(DataProperty, FunctionalProperty):
        domain=[Person]
        range=[str]
    class LastName(DataProperty, FunctionalProperty):
        domain=[Person]
        range=[str]
    class Chronic_diseases(DataProperty, FunctionalProperty):
        domain=[Patient]
        range=[str]
    class Treatments(DataProperty, FunctionalProperty):
        domain=[Person]
        range=[str]
    class Location(DataProperty, FunctionalProperty):
        domain=[Person]
        range=[str]
    class District(Location, FunctionalProperty):
        pass
    class Province(Location, FunctionalProperty):
        pass
    class Age(DataProperty, FunctionalProperty):
        domain=[Person]
        range=[int]
    class Gender(DataProperty, FunctionalProperty):
        domain=[Person]
        range=[str]
    class Started(DataProperty, FunctionalProperty):
        domain=[Patient]
        range=[datetime.date]
    class CausedBy(ObjectProperty):
        domain = [Symptom]
        range = [Disease]
    class Causes(ObjectProperty):
        domain = [Disease]
        range = [Symptom]
        inverse_property = CausedBy
for i in ont.individuals():
    print(i) 
SaveOnto()