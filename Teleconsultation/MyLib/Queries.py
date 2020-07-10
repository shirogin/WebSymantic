class Queries():
    All_Symptoms="""
        prefix : <https://YoucefMadadi.com/Teleconsultation#>
        SELECT DISTINCT ?s ?name 
        WHERE {
            ?s rdf:type :Symptom ;
                :Symptom_Name ?name.
        }
    """
    Unchecked="""
        prefix : <https://YoucefMadadi.com/Teleconsultation#>
        SELECT ?s ?fname ?lname ?gender ?age ?district ?province ?chronic ?treatments ?started ?symptoms
        WHERE {
            ?s rdf:type :Patient ;
                :FirstName ?fname;
                :LastName ?lname;
                :District ?district;
                :Province ?province;
                :Age ?age;
                :Gender ?gender;
                :Chronic_diseases ?chronic;
                :Treatments ?treatments;
                :Started ?started;
                :Has ?symptom.
                OPTIONAL { ?s :Affected ?consultation. }
                FILTER(!bound(?consultation))
                
            ?symptom :Symptom_Name ?symptoms.
        }
    """
