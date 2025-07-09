# from django.shortcuts import render
# from django.http import HttpResponse
# import sys, os, threading

# # Add the emailcrew path for import
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../emailcrew/src')))

# from emailcrew.main import run, _schedule_config, _schedule_event

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Schedule
# import your crew runner
import sys, os, threading
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../emailcrew/src')))
from emailcrew.main import run, set_schedule_config
import datetime as dt


'''
conda deactivate
cd emailcrew
conda activate venv/
cd email_scheduler
'''

# Start the background scheduler loop once
if not hasattr(run, "_started"):
    threading.Thread(target=run, daemon=True).start()
    run._started = True


@login_required
def schedule_create(request):
    user = request.user

    if request.method == 'POST':
        # 1. collect POST data
        receiver = request.POST['receiver']
        filepath = request.POST['filepath']
        day_str  = request.POST['day'].lower()
        time_str = request.POST['time']            # e.g. "14:30"

        # 2. parse into a real time object
        try:
            time_obj = dt.datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return render(request, 'scheduler/index.html', {
                'schedules': user.schedules.filter(active=True),
                'error': "Invalid time format. Use HH:MM."
            })

        # 3. save/update the Schedule model
        sched, created = Schedule.objects.update_or_create(
            user=user,
            defaults={
                'receiver': receiver,
                'filepath': filepath,
                'day': day_str,
                'time': time_obj,
                'active': True,
            }
        )

        # 4. tell your background runner
        set_schedule_config(
            receiver=sched.receiver,
            filepath=sched.filepath,
            day=sched.day,
            time=time_str         # pass the original string
        )

        # 5. render confirmation (use the raw string, not strftime)
        return render(request, 'scheduler/confirmation.html', {
            'day': sched.day.capitalize(),
            'time': time_str,
            'filepath': sched.filepath
        })

    # GET → show form + existing user schedules
    schedules = user.schedules.filter(active=True)
    return render(request, 'scheduler/index.html', {
        'schedules': schedules
    })


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('schedule_create')
    else:
        form = UserCreationForm()
    return render(request, 'scheduler/signup.html', {'form': form})
