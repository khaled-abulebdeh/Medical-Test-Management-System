from re import *
import re
from datetime import *
import sys  #used to redirect the output to a file

class MedicalTestRecord:
    def __init__(self, patient_id, test_name, date, result, unit, status):
        self.patient_id = patient_id
        self.test_name = test_name
        self.date = date
        self.result = result
        self.unit = unit
        self.status = status
    
    def __str__(self):
        return f"{self.patient_id}: {self.test_name}, {self.date}, {self.result}, {self.unit}, {self.status}"


class Patient:
    def __init__(self, id) -> None:
        self.id=id
        self.records=[]

    def addRecord(self, test_name, date, result, unit, status):
        self.records.append(MedicalTestRecord(self.id, test_name, date, result, unit, status.lower()))  # Convert status to lowercase

    def load(self, record_file):
        with open(record_file, 'r') as file:
            for line in file:
                if line.startswith(self.id):
                    parts = line.strip().split(': ')
                    if len(parts) > 1:  # Ensure there is a second part
                        # Match the format as needed: test_name, date, result, unit, status
                        record_details = parts[1].split(', ')
                        if len(record_details) == 5:  # Ensure there are enough details
                            self.addRecord(record_details[0], record_details[1], record_details[2], record_details[3], record_details[4])
                    else:
                        print(f"Warning: Line format is incorrect: {line.strip()}")    
                        
    def __str__(self) -> str:
        if (len(self.records)==0):
            return "Patient is existed but having no tests"
        
        result=""
        for i in self.records:
            result+= ("\n"+str(i))
        return f"Tests are:{result}"
    
def load_tests():
    tests = {}
    with open("MedicalRecord.txt", 'r') as file:
        for line in file:
            parts = line.strip().split(';')
            full_name = parts[0].split('(')[0].strip() # to get full name of Hemoglobin 
            short_name = parts[0].split('(')[1].replace(')', '').strip() # to get short name Hgb
            unit = parts[2].split(':')[1].strip() # to get the unit of the test name
            tests[full_name] = (short_name, unit) 
            tests[short_name] = (short_name, unit)
    print(tests)

def check_YYYY_MM_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m")
        return True
    except ValueError:
        return False
      
def idFilter_forManyCriteria(records):
    while True:
        ID=(input("Enter an ID: "))
        if len(ID) != 7 or not ID.isdigit():
            print("ID must be 7 digits number")
            continue
        else:
            break
    ID=int(ID)
    records=list(records)
    result=[]
    for i in records:
        testID=int (i.split(" ")[0].split(":")[0])
        if testID==ID:
            result.append(i)
        
    return result

def nameFilter_forManyCriteria(records):
    name=input("Enter a name: ")
    name=name.strip()
    records=list(records)
    result=[]
    testName=""
    for i in records:
        parts = i.split(',')
        testName = parts[0].split(':')[1].strip()

        if testName.lower()==name.lower():
            result.append(i)
        
    return result
def periodFilter_forManyCriteria(records):
    while True:
        startingDate=input("Enter starting period in YYYY-MM: ")
        try:
            startingDate=datetime.strptime(startingDate, "%Y-%m")
            break
        except ValueError:
            print("Sorry, invalid format")
        
    while True:
        endingDate=input("Enter ending period in YYYY-MM: ")
        try:
            endingDate=datetime.strptime(endingDate, "%Y-%m")
            break
        except ValueError:
            print("Sorry, invalid format")
    result=[]
    for i in records:
        parts = i.split(',')
        testDate=datetime.strptime(parts[1].strip(), "%Y-%m")
        if startingDate<=testDate<=endingDate:
            result.append(i)
    return result

def parse_duration(input_str):
    try:
        # Split the input string into days, hours, and minutes
        days, hours, minutes = map(int, (input_str).split('-'))
        # Create a timedelta object with the parsed values
        return (days, hours, minutes)

    except ValueError:
        return None

def isTimeBounded(startingTime, testTime, endingTime):

    #case1: days are in range
    if startingTime[0] < testTime[0] < endingTime[0]:
        return True
    
    #case2: days are out of range
    if testTime[0]<startingTime[0] or testTime[0]>endingTime[0]:
        return False
    
    #case 3:if days are equal
    elif startingTime[0]==testTime[0] and endingTime[0]==testTime[0]:
        #case a
        if startingTime[1] < testTime[1] < endingTime[1]:
            return True
        #case b
        if testTime[1]<startingTime[1] or testTime[1]>endingTime[1]:
            return False
        #case c
        elif startingTime[1]==testTime[1] and endingTime[1]==testTime[1]:
            #case a.1
            if startingTime[2] <= testTime[2] <= endingTime[2]:
                return True
            else:
                return False
        #case d
        elif startingTime[1]==testTime[1]:
            return testTime[2]>=startingTime[2]
            
        #case e: 
        elif endingTime[1]==testTime[1]:
            return testTime[2]<=endingTime[2]
                      
    #case4: if starting day equal testing day
    elif startingTime[0]==testTime[0]:
        if testTime[1]>startingTime[1]:
            return True
        elif testTime[1]==startingTime[1]:
            return testTime[2]>=startingTime[2]
        else:
            return False
    #case5: if ending day equal testing day
    elif endingTime[0]==testTime[0]:
        if testTime[1]<endingTime[1]:
            return True
        elif testTime[1]==endingTime[1]:
            return testTime[2]<=endingTime[2]
        else:
            return False
   
def turnaroundFilter_forManyCriteria(records):
    while True:
        startingTime=input("Enter starting time in DD-hh-mm: ")
        if match(r"^\d{2}-\d{2}-\d{2}$", startingTime):
            break
        else:
            print("Sorry, invalid format")
    startingTime=parse_duration(startingTime)

    while True:
        endingTime=input("Enter ending time in DD-hh-mm: ")
        if match(r"^\d{2}-\d{2}-\d{2}$", endingTime):
            break
        else:
            print("Sorry, invalid format")
    endingTime=parse_duration(endingTime)

    #load times from MedicalTests.txt
    f=open("MedicalTest.txt", "r")
    testDict={}
    for i in f:
        testName=i.split('(')[1].split(')')[0].strip()
        parts = i.split(';')
        testTime = parts[-1].strip()
        testTime=parse_duration(testTime)
        testDict[f"{testName}"]=testTime
    
    result=[]
    for i in records:
        parts = i.split(',')
        testName = parts[0].split(':')[1].strip()
        testTime=testDict[f"{testName}"]

        if isTimeBounded(startingTime,testTime, endingTime):
            result.append(i)

    return result
            
def statusFilter_forManyCriteria(records):
    testStatus = ["Pending", "Reviewed", "Completed"]  
    testStatus_lower = [status.lower() for status in testStatus]  # Convert to lowercase

    while True:
        status = input("Enter a status: ").lower()  # Convert input to lowercase
        if status not in testStatus_lower:  # Compare ignoring case
            print("Choose an accepted status")
            continue
        else:
            break
    result=[]
    for i in records:
        parts = i.split(',')
        testStatus = parts[4].strip()

        if testStatus==status:
            result.append(i)
        
    return result

def findTestLineFromMedicalTest(testName):
    #this function takes testName, and returns its information
    f=open("MedicalTest.txt", "r")
    for i in f:
        name=i.split('(')[1].split(')')[0].strip()
        if (testName.lower()==name.lower()):
            return str(i)
    f.close()

def abnormalFilter_forManyCriteria(records):
   
    #load avg ranges from MedicalTests.txt
    result=[]
    for i in records:
        testName=i.split(",")[0].split(" ")[1].strip()
        line=str(findTestLineFromMedicalTest(testName))
        parts = line.split(';')
        testRange = parts[1].strip().split(":")[1].strip()

        testResult=float (i.split(",")[2].strip())
        #to determine accepted ranges
        testRange=testRange.split(",")
        #if range is >lowerLimit, <upperLimit
        if (len(testRange)==2):
            upperLimit=float(testRange[1].strip().split(" ")[1])
            #print if it is abnormal
            if testResult>=upperLimit:
                result.append(i)

        #if range is <upperLimit or >lowerLimit
        elif (len(testRange)==1):
            #there are two cases

            #sign is either < or >
            sign=testRange[0].split(" ")[0].strip()
            upperLimit=float(testRange[0].split(" ")[1].strip())
            #case1: if testResult > upperLimit  -->>abnormal
            if sign=="<" and testResult>upperLimit:
                result.append(i)
            
            #case2: othersise, result is normal if it is > lowerLimit
            #no abnormal tests here
 
    return result
      
def filterByManyCriteria():
    
    choice=""
    while True:
        print("\nChoose one or more criteria to filter based on:")
        print("1. Patient ID")
        print("2. Test Name")
        print("3. Abnormal tests")
        print("4. In a specific period")
        print("5. Test status")
        print("6. Test turnaround time within a period ")
        try:
            userInput=int(input())
        except:
            print("Sorry, wrong choice")
            continue


        if userInput>0 and userInput<7:
            choice+=str(userInput)
            print("\n1. Choose more criteria.")
            print("otherwise) No more criteria needed")
            userInput=input()
            if userInput=="1":
                continue
            else:
                break
                
        else:
            print("Sorry, wrong choice")

    fPTR=open("MedicalRecord.txt", "r")
    result=[]
    for i in fPTR:
        result.append(str(i))

    for i in choice:
        if i=="1":
            result=idFilter_forManyCriteria(result)
        elif i=="2":
            result=nameFilter_forManyCriteria(result)
        elif i=="3":
            result=abnormalFilter_forManyCriteria(result)
        elif i=="4":
            result=periodFilter_forManyCriteria(result)
        elif i=="5":
            result=statusFilter_forManyCriteria(result)
        elif i=="6":
            result=turnaroundFilter_forManyCriteria(result)
    
    if len(result)!=0:
        for i in result:
            print(f"{i}")
    else:
        print("No matched results")
            
def values_Summary ():
    f=open("MedicalTest.txt", "r")
    myDict={}
    #store all Medical Tests in a dictionary
    for i in f:
        testName=i.split('(')[1].split(')')[0].strip()
        #initialize values
        myDict[f"{testName}"]= {
            'min':999999999999999,
            'max':-1,
            'sum':0,
            'counter':0
        }

    f.close()
    f=open("MedicalRecord.txt", "r")
    for i in f:
        testName=i.split(",")[0].split(" ")[1].strip()
        if testName in myDict:

            testResult=float (i.split(",")[2].strip())
            myDict[f"{testName}"]["counter"]+=1
            myDict[f"{testName}"]["sum"]+=testResult

            if testResult < myDict[f"{testName}"]["min"]:
                myDict[f"{testName}"]["min"]=testResult
            if testResult > myDict[f"{testName}"]["max"]:
                myDict[f"{testName}"]["max"]=testResult
    print("---Summary for all tests---")
    
    for i,j in myDict.items():
        print(f"Test Name: {i}")
        print(f"Average Values= {j['sum']/j['counter']:.2f}")
        print(f"Max Value= {j['max']:.2f}")
        print(f"Min Value= {j['min']:.2f}")
        print("----------------------------")

def is_Min_turnaround(turnaround, min):
    turnaround=parse_duration(turnaround)
    min=parse_duration(min)

    #[0]:days,,, [1]:hours,,,[2]:minutes

    if turnaround[0]>min[0]:
        return False
    if turnaround[0]==min[0]:

        if turnaround[1]>min[1]:
                return False
        if turnaround[1]==min[1]:
                return turnaround[2]<=min[2]
        else:
            return True        
    else:
        return True
def is_Max_turnaround(turnaround, Max):
    turnaround=parse_duration(turnaround)
    Max=parse_duration(Max)

    #[0]:days,,, [1]:hours,,,[2]:minutes

    if turnaround[0]<Max[0]:
        return False
    if turnaround[0]==Max[0]:

        if turnaround[1]<Max[1]:
                return False
        if turnaround[1]==Max[1]:
                return turnaround[2]>=Max[2]
        else:
            return True        
    else:
        return True
def turnaround_Summary():
    f=open("MedicalTest.txt", "r")
    numOfTests=0
    totalDays=0
    totalHours=0
    totalMinutes=0
    minTime="99-99-99"
    maxTime="00-00-00"
    minName=""
    maxName=""
    for i in f:
        numOfTests+=1
        testName=i.split('(')[1].split(')')[0].strip()
        parts = i.split(';')
        testTime = parts[-1].strip()
        #testTime[0]:Day | testTime[1]:Hour | testTime[2]: Minute
        timeList=testTime.strip().split("-")
        totalDays+=int(timeList[0])
        totalHours+=int(timeList[1])
        totalMinutes+=int(timeList[2])
        if is_Min_turnaround(testTime,minTime):
            minTime=testTime
            minName=testName
        if is_Max_turnaround (testTime,maxTime):
            maxTime=testTime
            maxName=testName
        
    #to calculate avg turnaround time
    totalMinutes+= totalDays*24*60 #convert to minutes
    totalMinutes+= totalHours*60

    avg_minutes=totalMinutes//numOfTests
    Avg_hours=0
    avg_days=0
    #convert to DD-HH-MM format
    while avg_minutes-(24*60) >0:
        avg_days+=1
        avg_minutes-= (24*60)
    
    #cnovert to hours
    while avg_minutes-(60)>0:
        Avg_hours+=1
        avg_minutes-=(60)
    print("-----------------------------------------")
    print(f"Test with MIN turnaround: {minName}. ", minTime)
    print(f"Test with MAX turnaround: {maxName}. ",maxTime)
    print(f"Average turanoud time is: {avg_days:2}-{Avg_hours}-{avg_minutes}")
    print("-----------------------------------------")
    
        

##############Load from file to dict
#for each line, check if id existed
#if true, add the test to patient's lest
#if not, create a new object patient and add the test
#never forget that add function must append to records file











class MedicalRecordSystem:
    def __init__(self, record_file, tests_file):
        self.record_file = record_file
        self.tests = {}  # Initialize tests attribute here
        self.load_tests(tests_file)  # Ensure this is called to load tests
        self.patients = {}

    def load_tests(self, tests_file):
        tests = {}
        with open(tests_file, 'r') as file:
            for line in file:
                parts = line.strip().split(';')
                if len(parts) < 3:  # Ensure there are enough parts
                    print(f"Skipping invalid line: {line.strip()}")
                    continue  # Skip this line if it doesn't have enough parts
                full_name = parts[0].split('(')[0].strip()
                short_name = parts[0].split('(')[1].replace(')', '').strip()
                unit = parts[2].split(':')[1].strip() if ':' in parts[2] else parts[2].strip()  # Handle unit extraction
                tests[full_name] = (short_name, unit)
                tests[short_name] = (short_name, unit)
        self.tests = tests  # Assign loaded tests to the instance variable

    def validate_patient_id_format(self, patient_id):
        return len(patient_id) == 7 and patient_id.isdigit()

    def validate_patient_id_exists(self, patient_id):
        if self.validate_patient_id_format(patient_id):
            with open(self.record_file, 'r') as file:
                for line in file:
                    if line.startswith(patient_id):
                        return True
        return False

    def validate_test_name(self, test_name):
        return test_name in self.tests

    def validate_date(self, date_str):
        parts = date_str.split('-')
        if len(parts) != 2:
            print("ERROR! Date should be in the format YYYY-MM.")
            return False

        year, month = parts[0], parts[1]
        if not (year.isdigit() and month.isdigit()):
            print("ERROR! Year and month should be numeric.")
            return False

        if len(year) != 4 or len(month) != 2:
            print("ERROR! Year should have 4 digits and month should have 2 digits.")
            return False

        year = int(year)
        month = int(month)
        if not (1 <= month <= 12):
            print("ERROR! Month should be between 01 and 12.")
            return False

        today = datetime.today()
        try:
            input_date = datetime(year, month, 1)
        except ValueError:
            print("ERROR! Invalid date.")
            return False

        if input_date > today:
            print("ERROR! Date cannot be in the future.")
            return False

        return True

    def validate_result(self, result):
        try:
            float(result)
            return True
        except ValueError:
            return False

    def validate_status(self, status):
        return status.lower() in ["pending", "completed", "reviewed"]

    def get_valid_patient_id(self, require_existing=True):
        while True:
            patient_id = input("Enter patient ID: ")
            if self.validate_patient_id_format(patient_id):
                if require_existing and self.validate_patient_id_exists(patient_id):
                    return patient_id
                elif not require_existing:
                    return patient_id
            print("Invalid or non-existent patient ID.")

    def get_valid_test_name(self):
        while True:
            test_name = input("Enter test name: ")
            if self.validate_test_name(test_name):
                unit = self.tests[test_name][1]  # Extract unit
                return test_name, unit
            print("Invalid test name.")

    def get_valid_date(self):
        while True:
            date = input("Enter date (YYYY-MM): ")
            if self.validate_date(date):
                return date

    def get_valid_result(self):
        while True:
            result = input("Enter test result: ")
            if self.validate_result(result):
                return result
            print("Invalid result. Please enter a numeric value.")

    def get_valid_status(self):
        while True:
            status = input("Enter test status (pending, completed, reviewed): ")
            if self.validate_status(status):
                return status.lower()  # Return status in lowercase
            print("Invalid status.")

    def add_test_record(self):
        patient_id = self.get_valid_patient_id(require_existing=False)
        if patient_id not in self.patients:
            self.patients[patient_id] = Patient(patient_id)
            update_patient_dict(patient_id, self.patients[patient_id])
    
        test_name, unit = self.get_valid_test_name()
        date = self.get_valid_date()
        result = self.get_valid_result()
        status = self.get_valid_status()

        # Add current time if status is 'completed'
        if status == 'completed':
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")  # Format current time
            self.patients[patient_id].addRecord(test_name, date, result, unit, status)
            # Ensure the time is included in the record if status is 'completed'
            record_to_add = f"{self.patients[patient_id].records[-1]}, {current_time}"
        else:
            self.patients[patient_id].addRecord(test_name, date, result, unit, status)
            record_to_add = str(self.patients[patient_id].records[-1])

        # Remove any unwanted time fields from the record
        record_parts = record_to_add.split(", ")
        filtered_parts = [part for part in record_parts if not re.match(r'^\d{2}-\d{2}-\d{2}$', part)]
        final_record = ", ".join(filtered_parts)

        with open(self.record_file, 'a') as file:
            file.write(final_record + "\n")  # Ensure only one newline is added

    def update_test_result(self):
        patient_id = self.get_valid_patient_id(require_existing=True)
        if not patient_id:
            print("Error: Patient ID does not exist.")
            return
        
        test_name = self.get_valid_test_name_from_record(patient_id)
        date = self.get_valid_date_from_record(patient_id, test_name)

        while True:
            print("What would you like to update?")
            print("1. Result")
            print("2. Date")
            print("3. Status")
            print("4. Exit")
            choice = input("Enter your choice (1/2/3/4): ")

            if choice == '1':
                new_result = self.get_valid_result()
                self.update_record(patient_id, test_name, date, 'result', new_result)
                print("Result updated successfully.")
                break
            elif choice == '2':
                new_date = self.get_valid_date()
                self.update_record(patient_id, test_name, date, 'date', new_date)
                print("Date updated successfully.")
                break
            elif choice == '3':
                new_status = self.get_valid_status()
                self.update_record(patient_id, test_name, date, 'status', new_status)
                print("Status updated successfully.")
                break
            elif choice == '4':
                print("Exiting update...")
                break
            else:
                print("Invalid choice, please select 1, 2, 3, or 4.")

    def delete_test(self):
        patient_id = self.get_valid_patient_id(require_existing=True)
        if not patient_id:
            print("Error: Patient ID does not exist.")
            return

        test_name = self.get_valid_test_name_from_record(patient_id)
        date = self.get_valid_date_from_record(patient_id, test_name)

        while True:
            confirmation = input("Are you sure you want to delete this record? (yes/no): ").lower()
            if confirmation == 'yes':
                self.delete_record(patient_id, test_name, date)
                print("Record deleted successfully :)")
                break
            elif confirmation == 'no':
                print("Deletion canceled.")
                break
            else:
                print("Invalid input, please type 'yes' or 'no'.")

    def delete_record(self, patient_id, test_name, date):
        with open(self.record_file, 'r') as file:
            lines = file.readlines()

        with open(self.record_file, 'w') as file:
            for line in lines:
                if not line.startswith(f"{patient_id}: {test_name}, {date},"):
                    file.write(line)

    def get_valid_test_name_from_record(self, patient_id):
        while True:
            test_name = input("Enter Test Name: ")
            if self.validate_test_name(test_name):
                with open(self.record_file, 'r') as file:
                    for line in file:
                        if line.startswith(f"{patient_id}: {test_name},"):
                            return test_name
                print("Test Name not found for this Patient ID in MedicalRecord.")
            else:
                print("Invalid test name. Please try again.")

    def get_valid_date_from_record(self, patient_id, test_name):
        while True:
            date = input("Enter Date (YYYY-MM): ")
            if self.validate_date(date):
                with open(self.record_file, 'r') as file:
                    for line in file:
                        if line.startswith(f"{patient_id}: {test_name}, {date},"):
                            return date
                print("Date not found for this Test Name and Patient ID in MedicalRecord.")
            else:
                print("Invalid date format. Please try again.")

    def update_record(self, patient_id, test_name, date, field, new_value):
        updated_lines = []
        with open(self.record_file, 'r') as file:
            for line in file:
                if line.startswith(f"{patient_id}: {test_name}, {date},"):
                    parts = line.strip().split(', ')
                    if field == 'result':
                        parts[2] = new_value
                    elif field == 'date':
                        parts[1] = new_value
                    elif field == 'status':
                        if parts[4] == 'completed' and len(parts) > 5:  # Check if status is completed and time field exists
                            if new_value.lower() in ['pending', 'reviewed']:
                                parts[4] = new_value.lower()  # Update status
                                parts = parts[:5]  # Remove the time field
                        else:
                            parts[4] = new_value.lower()  # Convert status to lowercase
                            if new_value.lower() == 'completed':
                                current_time = datetime.now().strftime("%Y-%m-%d %H:%M")  # Format current time
                                parts.append(current_time)  # Add current time to the parts
                    updated_line = f"{parts[0]}, {parts[1]}, {parts[2]}, {parts[3]}, {parts[4]}" + (f", {parts[5]}" if len(parts) > 5 else "") + "\n"
                    updated_lines.append(updated_line)
                else:
                    updated_lines.append(line)

        with open(self.record_file, 'w') as file:
            file.writelines(updated_lines)


def update_patient_dict(patient_id, patient_obj):
    if patient_id not in myDict:
        myDict[patient_id] = patient_obj

def get_range():
    print("Select the range input method:")
    print("1: Enter a range (e.g., 60-70)")
    print("2: Enter a single value to be less than (e.g., < 70)")
    print("3: Enter a single value to be more than (e.g., > 60)")
    print("4: Enter a range that is less than a value or greater than another (e.g., < 60 or > 80)")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        while True:
            range_input = input("Enter the range (e.g., 60-70): ")
            try:
                lower_bound, upper_bound = map(float, range_input.split('-'))
                if lower_bound <= upper_bound:
                    return lower_bound, upper_bound, 1  # Case 1
                else:
                    print("Invalid range. Upper bound cannot be less than lower bound. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid range in the format 'lower-upper'.")
    elif choice == '2':
        value = float(input("Enter the value (e.g., 70): "))
        return None, value, 2  # Case 2
    elif choice == '3':
        value = float(input("Enter the value (e.g., 60): "))
        return value, None, 3  # Case 3
    elif choice == '4':
        while True:
            try:
                lower_value = float(input("Enter the value for less than (e.g., 60): "))
                upper_value = float(input("Enter the value for greater than (e.g., 80): "))
                if lower_value < upper_value:
                    return lower_value, upper_value, 4  # Case 4
                else:
                    print("Invalid range. Upper value must be greater than lower value. Please try again.")
            except ValueError:
                print("Invalid input. Please enter numeric values.")
    else:
        print("Invalid choice. Please try again.")
        return get_range()  # Retry if invalid choice

def save_test(full_name, short_name, lower_bound, upper_bound, unit, time_format, case):
    # Determine the range representation based on the case
    if case == 1:  # Case for a range
        range_representation = f"Range: > {lower_bound}, < {upper_bound}"
    elif case == 2:  # Case for single value less than
        range_representation = f"Range: < {upper_bound}"
    elif case == 3:  # Case for single value greater than
        range_representation = f"Range: > {lower_bound}"
    elif case == 4:  # Case for less than and greater than
        range_representation = f"Range: < {lower_bound}, > {upper_bound}"

    # Implement the logic to save the test details to MedicalTest.txt
    with open("MedicalTest.txt", 'a') as file:
        file.write(f"{full_name} ({short_name}); {range_representation}; Unit: {unit}, {time_format}\n")

    print("Medical test added successfully.")

def add_medical_test():
    try:
        # Get user input
        full_name = input("Enter full name of the test: ")
        short_name = input("Enter short name of the test: ")
        
        # Get and validate range
        lower_bound, upper_bound, case = get_range()
        
        unit = input("Enter unit (e.g., g/dL): ")
        time_format = input("Enter time format (DD-HH-MM): ")
        
        # Save the test (assuming a function save_test exists)
        save_test(full_name, short_name, lower_bound, upper_bound, unit, time_format, case)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def update_medical_test():
    test_name = input("Enter the name or short name of the medical test to update: ")
    found = False
    lines = []

    # Read existing tests from the file
    with open("MedicalTest.txt", 'r') as file:
        lines = file.readlines()

    # Check if the test name or short name exists
    for line in lines:
        if test_name in line:  # Check if the test name or short name is in the line
            found = True
            current_line = line  # Store the current line for updates
            break

    if not found:
        print("Test name or short name not found.")
        return

    # Extract current range, unit, and time format from the current line
    parts = current_line.strip().split('; ')
    short_name = parts[0]  # Get the full name with short name
    range_part = parts[1]  # Get the range part
    unit_part = parts[2]  # Get the unit part
    time_format = unit_part.split(', ')[1]  # Extract time format from unit part
    unit = unit_part.split(': ')[1].split(', ')[0]  # Extract unit from unit part

    # Ask what to update
    while True:
        print("What would you like to update?")
        print("1. Range")
        print("2. Unit")
        print("3. Time Format")
        print("4. Exit")
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            # Get the new range using the same concept as save_test
            lower_bound, upper_bound, case = get_range()  # Reuse existing function
            range_representation = ""
            if case == 1:  # Case for a range
                range_representation = f"Range: > {lower_bound}, < {upper_bound}"
            elif case == 2:  # Case for single value less than
                range_representation = f"Range: < {upper_bound}"
            elif case == 3:  # Case for single value greater than
                range_representation = f"Range: > {lower_bound}"
            elif case == 4:  # Case for less than and greater than
                range_representation = f"Range: < {lower_bound}, > {upper_bound}"

            # Update the line with new range, keeping the original short name, unit, and time format
            lines[lines.index(current_line)] = f"{short_name}; {range_representation}; Unit: {unit}, {time_format}\n"
            print("Range updated successfully.")
            break
        elif choice == '2':
            unit = input("Enter new unit: ")
            # Update the line with new unit, keeping the original short name, range, and time format
            lines[lines.index(current_line)] = f"{short_name}; {range_part}; Unit: {unit}, {time_format}\n"
            print("Unit updated successfully.")
            break
        elif choice == '3':
            time_format = input("Enter new time format (DD-HH-MM): ")
            # Update the line with new time format, keeping the original short name and unit
            lines[lines.index(current_line)] = f"{short_name}; {range_part}; Unit: {unit}, {time_format}\n"
            print("Time format updated successfully.")
            break
        elif choice == '4':
            print("Exiting update...")
            break
        else:
            print("Invalid choice, please select 1, 2, 3, or 4.")

    # Write the updated lines back to the file
    with open("MedicalTest.txt", 'w') as file:
        file.writelines(lines)




record_file = "MedicalRecord.txt"
test_file = "MedicalTest.txt" 
system = MedicalRecordSystem(record_file, test_file)

myDict = {}
with open(record_file, 'r') as file:
    for line in file:
        patient_id = line.split(':')[0]
        myDict[patient_id] = Patient(patient_id)
        myDict[patient_id].load(record_file)


while True:
        print("\nMedical Test Management System")
        print("1. Add a new medical test record")
        print("2. Update a medical test record")
        print("3. Add a new medical test")
        print("4. Update a medical test")
        print("5. Filter medical tests")
        print("6. Generate a summary for tests' values")
        print("7. Generate a summary for tests' turnaround time")
        print("8. Delete a medical test record")
        print("9. Exit")
        choice = input("Please enter your choice: ")

        if choice == '1':
            system.add_test_record()
        elif choice == '2':
            system.update_test_result()  #  to execute the update function
        elif choice == '3':
            add_medical_test()  #  to execute the function to add a medical test
        elif choice == '4':
            update_medical_test()  #  to execute the update function
        elif choice == '5':
            filterByManyCriteria()
        elif choice == '6':
            values_Summary()
        elif choice == '7':
            turnaround_Summary()
        elif choice == '8':
            system.delete_test()  #  to execute the delete function
        elif choice == '9':
            print("Exiting the system...")
            break
        else:
            print("\nInvalid choice, please try again.")



