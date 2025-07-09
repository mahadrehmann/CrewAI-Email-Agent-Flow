# # scheduler/views.py

# from django.shortcuts import render
# from django.http import HttpResponse
# import sys, os

# # Add the emailcrew path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../emailcrew/src')))

# from emailcrew.main import run_crew_and_send_mail


# def schedule_create(request):
#     if request.method == 'POST':
#         receiver = request.POST.get('receiver')
#         file_path = request.POST.get('filepath')

#         try:
#             run_crew_and_send_mail(receiver, file_path)
#             return HttpResponse("✅ Email sent successfully!")
#         except Exception as e:
#             return HttpResponse(f"❌ Error: {str(e)}")
        
#     return render(request, 'index.html')

from django.shortcuts import render
from django.http import HttpResponse
import sys, os, threading

# Add the emailcrew path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../emailcrew/src')))

from emailcrew.main import run, _schedule_config, _schedule_event

# Global variable to start the scheduler only once
scheduler_started = False

def schedule_create(request):
    global scheduler_started

    if request.method == 'POST':
        receiver = request.POST.get('receiver')
        file_path = request.POST.get('filepath')
        day       = request.POST.get('day').lower()
        time      = request.POST.get('time')

        # Update the global config
        _schedule_config['receiver'] = receiver
        _schedule_config['filepath'] = file_path
        _schedule_config['day'] = day
        _schedule_config['time'] = time

        # Signal the event
        _schedule_event.set()

        return render(request, 'confirmation.html', {
            'day': day.capitalize(),
            'time': time,
            'filepath': file_path
        })

    # Start scheduler thread only once
    if not scheduler_started:
        threading.Thread(target=run, daemon=True).start()
        scheduler_started = True

    return render(request, 'index.html')
