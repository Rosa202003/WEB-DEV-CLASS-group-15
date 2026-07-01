from django.http import HttpResponse

def home(request):
    return HttpResponse("Complaint Management System")
