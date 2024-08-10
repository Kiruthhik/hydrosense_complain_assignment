from django.http import JsonResponse
from firebase_admin import credentials, firestore, initialize_app
from django.views.decorators.csrf import csrf_exempt
import json

# Initialize the Firebase Admin SDK
#cred = credentials.Certificate("complaint_assignment/firebase_credentials.json")
#initialize_app(cred)

db = firestore.client()

def retrieve_complaints(request):
    complaints_ref = db.collection('complaints')
    docs = complaints_ref.stream()

    for doc in docs:
        print(f'Document ID: {doc.id}')
        print(f'Document Data: {doc.to_dict()}')

@csrf_exempt
def new_complaint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaintId')
            
            if complaint_id:
                # Update Firestore document with assigned employee
                result = assign_employee(complaint_id)
                if result:
                    return JsonResponse({"status": "Complaint processed and employee assigned"})
                else:
                    return JsonResponse({"status": "No employee available"}, status=404)
            else:
                return JsonResponse({"status": "Complaint ID not provided"}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({"status": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "Invalid request"}, status=400)

def assign_employee(complaint_id):
    employees_ref = db.collection('employees')
    available_employees = employees_ref.where('availability', '==', True).stream()

    assigned = False  # Track if an employee is assigned

    for employee in available_employees:
        employee_id = employee.id
        employee_ref = employees_ref.document(employee_id)
        
        # Mark employee as assigned
        employee_ref.update({
            'availability': False,
            'assignedComplaint': complaint_id  # Store the complaint ID in the employee document
        })
        
        # Assign employee to complaint
        complaint_ref = db.collection('complaints').document(complaint_id)
        complaint_ref.update({
            'employee_id': employee_id,
            'employee_assigned': True,
        })

        assigned = True
        break

    if not assigned:
        return False  # No available employee was found

    return True
