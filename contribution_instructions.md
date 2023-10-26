<h1>Contribution Instructions for dynairxSnomedFinder</h1>

<p>Aim: This document aims to be an instruction manual for how we can contribute towards the dynairxSnomedFinder library.
The library encodes over 100 long-term conditions (LTC) in SNOMED format, which were intially built for use with the NIHR DynAIRx project.
They primarily consist of codes from the Electronic Frailty Index 2, and from previous work by the University of Liverpool, 
in addition to some manual SNOMED code searching by the research team.

This library is intended for use with the associated codelist <a href="https://github.com/DynAIRx/Codelists">HERE</a></p>

<h2>Functionality</h2>
<p>The purpose of this library is to process CPRD primary care records into a format suitable for statistical modelling for DynAIRx.
There is one function per LTC, most of which are very simple but some require additional processing (e.g. check BMI score associated with SNOMED code).

<h2>Usage</h2>
<b>Fill later...</b>

<h2>Structure</h2>
<p>There are two primary functions utilised throughout the code:</p>

```python
    # snomed_codes_for_disease: Function to find SNOMED codes associated with a given disease / condition
    # Input:
    # disease_name: Name of the disease /condition to return codes for
    #
    # Output:
    # snomed_codes: List of SNOMED codes for the given disease / condition
    def snomed_codes_for_disease(self, disease_name):
        snomed_codes = list(self.codelist[self.codelist['Disease'] == disease_name].SnomedCTConceptId)
        return snomed_codes
```

<p>and</p>

```python
    # check_presence_snomed: Function to find presence of SNOMED codes within dataframe of patient medcodes
    # Input:
    # patient_df: Dataframe of patient record taken from CPRD primary care
    # disease_codes: List of SNOMED codes indicating presence of a disease / condition (use snomed_codes_for_disease helper function)
    #
    # Output:
    # condition_active: True if SNOMED codes present, otherwise False
    def check_presence_snomed(self, patient_df, disease_codes):
        patient_snomed_codes = list(map(self.medcode2snomed, patient_df.medcode))
        condition_active = any(patient_snomed_codes in disease_codes)
        return condition_active
```

<p>There is also one function which loops through all the LTC specific functions and runs them all on the same patient dataframe.
This function is used to generate the tables used for statistical modelling within DynAIRx.</p>

<h2>Adding new diseases</h2>
<p>To add a new disease, we first need to have an associated SNOMED codelist <a href="https://github.com/DynAIRx/Codelists">HERE</a>.
  
  Most of the disease-specific functions use these two functions exclusively, but some require additional checks of numerical values associated to certain SNOMED codes.

  An example of an straightforwards condition would be Alcohol Related Brain-Injury with the following code.</p>
  
```python
    # alcohol_related_brain_injury
    # Simple check
    # Input:
    # patientdf: Dataframe of patient medcode ids
    # Output:
    # disease_active: True if disease is present, otherwise False
    def alcohol_related_brain_injury(self, patientdf):
        snomed_codes = self.snomed_codes_for_disease('Alcohol-related Brain Injury')
        disease_active = self.check_presence_snomed(patient_df, snomed_codes)
        return disease_active
```

<p>Meanwhile, a more complicated example would be Alcohol Problems. 
  In this case there are explicit SNOMED codes that indicate Alcohol Problems, 
  plus some (the number of units drank per day/week) that require us to check the numerical values. 
  This leads to some more involved logic as follow.</p>

```python
    # alcohol_problems
    # Complex logic for numerical values
    # Input:
    # patientdf: Dataframe of patient medcode ids
    # Output:
    # disease_active: True if disease is present, otherwise False
    def alcohol_problems(self, patientdf):
        snomed_codes = self.snomed_codes_for_disease('Alcohol Problem')
        # This includes 4 codes that need extra logic, remove these for now
        snomed_codes.remove('10800000000000000') # Units per week
        snomed_codes.remove('228958009') # Units per week
        snomed_codes.remove('10800000000000000') # Units per day
        snomed_codes.remove('228957004') # Units per day

        # snomed_codes is now an "easy" search
        disease_active = self.check_presence_snomed(patient_df, snomed_codes)

        # If alcohol now active can skip the numerical checks
        if disease_active:
            return True
        # Otherwise check the numerical values
        # Units per day
        # Convert to medcode and check if weekly units > 20
        day_codes = map(self.snomed2medcode, ['10800000000000000', '228957004'])
        if (patient_df[patient_df.medcodeid.isin(day_codes)].numeric * 7 > 20):
            return True
        # Units per week
        # Convert to medcode and check if weekly units > 20
        week_codes = map(self.snomed2medcode, ['10800000000000000', '228958009'])
        if (patient_df[patient_df.medcodeid.isin(week_codes)].numeric > 20):
            return True
        # If still here then no alcohol problems and can return False
        return False
```
