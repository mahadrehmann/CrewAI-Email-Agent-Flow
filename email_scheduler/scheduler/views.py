# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from .models import Schedule
# # import your crew runner
# import sys, os, threading
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../emailcrew/src')))
# from emailcrew.main import run, set_schedule_config
# import datetime as dt


# '''
# TODO:

# - User Signup Using 
# '''


# '''
# conda deactivate
# cd emailcrew
# conda activate venv/
# cd email_scheduler

# HOW TO RUN
# python manage.py runserver
# '''

# # Start the background scheduler loop once
# if not hasattr(run, "_started"):
#     threading.Thread(target=run, daemon=True).start()
#     run._started = True


# @login_required
# def schedule_create(request):
#     user = request.user

#     if request.method == 'POST':
#         # 1. collect POST data
#         receiver = request.POST['receiver']
#         filepath = request.POST['filepath']
#         day_str  = request.POST['day'].lower()
#         time_str = request.POST['time']            # e.g. "14:30"

#         # 2. parse into a real time object
#         try:
#             time_obj = dt.datetime.strptime(time_str, "%H:%M").time()
#         except ValueError:
#             return render(request, 'scheduler/index.html', {
#                 'schedules': user.schedules.filter(active=True),
#                 'error': "Invalid time format. Use HH:MM."
#             })

#         # 3. save/update the Schedule model
#         sched, created = Schedule.objects.update_or_create(
#             user=user,
#             defaults={
#                 'receiver': receiver,
#                 'filepath': filepath,
#                 'day': day_str,
#                 'time': time_obj,
#                 'active': True,
#             }
#         )

#         # 4. tell your background runner
#         set_schedule_config(
#             receiver=sched.receiver,
#             filepath=sched.filepath,
#             day=sched.day,
#             time=time_str         # pass the original string
#         )

#         # 5. render confirmation (use the raw string, not strftime)
#         return render(request, 'scheduler/confirmation.html', {
#             'day': sched.day.capitalize(),
#             'time': time_str,
#             'filepath': sched.filepath
#         })

#     # GET → show form + existing user schedules
#     schedules = user.schedules.filter(active=True)
#     return render(request, 'scheduler/index.html', {
#         'schedules': schedules
#     })


# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import login
# from django.shortcuts import render, redirect

# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('schedule_create')
#     else:
#         form = UserCreationForm()
#     return render(request, 'scheduler/signup.html', {'form': form})


# ------------------------------------------------------------------------------------------------------------------------------------------------------
# views.py

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from .models import Schedule
# import sys, os, threading
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../emailcrew/src')))
# from emailcrew.main import run, set_schedule_config
# import datetime as dt

# # MSAL + OAuth
# import msal
# from django.conf import settings
# from django.http import HttpResponseRedirect

# # Thread runner (starts once)
# if not hasattr(run, "_started"):
#     threading.Thread(target=run, daemon=True).start()
#     run._started = True

# @login_required
# def schedule_create(request):
#     user = request.user

#     if request.method == 'POST':
#         receiver = request.POST['receiver']
#         filepath = request.POST['filepath']
#         day_str  = request.POST['day'].lower()
#         time_str = request.POST['time']

#         try:
#             dt.datetime.strptime(time_str, "%H:%M")
#         except ValueError:
#             return render(request, 'scheduler/index.html', {
#                 'schedules': user.schedules.filter(active=True),
#                 'error': "Invalid time format. Use HH:MM."
#             })

#         # Save to session for OAuth callback
#         request.session['schedule_form_data'] = {
#             'receiver': receiver,
#             'filepath': filepath,
#             'day': day_str,
#             'time': time_str
#         }

#         # Redirect to MS login
#         return redirect('start_oauth')

#     schedules = user.schedules.filter(active=True)
#     return render(request, 'scheduler/index.html', {'schedules': schedules})


# def start_oauth(request):
#     client_id = settings.MS_CLIENT_ID
#     redirect_uri = request.build_absolute_uri('/auth/callback/')
#     authority = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID}"

#     msal_app = msal.PublicClientApplication(client_id=client_id, authority=authority)
#     flow = msal_app.initiate_device_flow(scopes=settings.MS_SCOPES)

#     if 'user_code' not in flow:
#         return render(request, 'scheduler/error.html', {'error': "Failed to initiate device flow."})

#     request.session['msal_flow'] = flow
#     return HttpResponseRedirect(flow['verification_uri'] + "?user_code=" + flow['user_code'])


# def oauth_callback(request):
#     # For simplicity, just simulate successful login
#     form_data = request.session.get('schedule_form_data')

#     if not form_data:
#         return render(request, 'scheduler/error.html', {'error': "Missing session data. Please re-submit."})

#     # Save schedule to DB
#     user = request.user
#     sched, created = Schedule.objects.update_or_create(
#         user=user,
#         defaults={
#             'receiver': form_data['receiver'],
#             'filepath': form_data['filepath'],
#             'day': form_data['day'],
#             'time': dt.datetime.strptime(form_data['time'], "%H:%M").time(),
#             'active': True,
#         }
#     )

#     # Trigger email scheduler
#     set_schedule_config(
#         receiver=form_data['receiver'],
#         filepath=form_data['filepath'],
#         day=form_data['day'],
#         time=form_data['time']
#     )

#     # Clean session
#     del request.session['schedule_form_data']

#     return render(request, 'scheduler/confirmation.html', {
#         'day': sched.day.capitalize(),
#         'time': form_data['time'],
#         'filepath': sched.filepath
#     })


# # signup stays unchanged
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import login

# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('schedule_create')
#     else:
#         form = UserCreationForm()
#     return render(request, 'scheduler/signup.html', {'form': form})

# ?---------------------------------------------------------------------------------------------------------------------------------------
# At top:
from django.conf import settings
from emailcrew.msal_cache import build_persistence
import msal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime as dt
from .models import Schedule
from emailcrew.main import run, set_schedule_config
token_cache = build_persistence()


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Schedule
import sys, os, threading
from emailcrew.main import run, set_schedule_config
import datetime as dt

import msal
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Start CrewAI scheduler once
if not hasattr(run, "_started"):
    threading.Thread(target=run, daemon=True).start()
    run._started = True


@login_required
def schedule_create(request):
    user = request.user

    if request.method == 'POST':
        receiver = request.POST['receiver']
        filepath = request.POST['filepath']
        day_str  = request.POST['day'].lower()
        time_str = request.POST['time']

        try:
            dt.datetime.strptime(time_str, "%H:%M")
        except ValueError:
            return render(request, 'scheduler/index.html', {
                'schedules': user.schedules.filter(active=True),
                'error': "Invalid time format. Use HH:MM."
            })

        request.session['schedule_form_data'] = {
            'receiver': receiver,
            'filepath': filepath,
            'day': day_str,
            'time': time_str
        }

        return redirect('start_oauth')

    schedules = user.schedules.filter(active=True)
    return render(request, 'scheduler/index.html', {'schedules': schedules})


def start_oauth(request):
    client_id = settings.MS_CLIENT_ID
    client_secret = settings.MS_CLIENT_SECRET
    authority = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID}"
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))
    
    # redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")  # force localhost

    print("\n\nUsing redirect_uri:", redirect_uri, "\n\n")

    # msal_app = msal.ConfidentialClientApplication(
    #     client_id=client_id,
    #     client_credential=client_secret,
    #     authority=authority
    # )
    msal_app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
        token_cache=token_cache  # ✅ Add this
    )

    auth_url = msal_app.get_authorization_request_url(
        scopes=settings.MS_SCOPES,
        redirect_uri=redirect_uri,
        state="dummy_state"
    )

    return HttpResponseRedirect(auth_url)


def oauth_callback(request):
    code = request.GET.get('code', None)
    if not code:
        return render(request, 'scheduler/error.html', {'error': 'Missing authorization code.'})

    client_id = settings.MS_CLIENT_ID
    client_secret = settings.MS_CLIENT_SECRET
    authority = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID}"
    redirect_uri = request.build_absolute_uri(reverse('oauth_callback'))

    # redirect_uri = redirect_uri.replace("127.0.0.1", "localhost")  # force localhost
    print("Session key:", request.session.session_key)
    print("Session data:", dict(request.session.items()))

    
    # msal_app = msal.ConfidentialClientApplication(
    #     client_id=client_id,
    #     client_credential=client_secret,
    #     authority=authority
    # )
    msal_app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
        token_cache=token_cache  # ✅ Add this
    )

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=settings.MS_SCOPES,
        redirect_uri=redirect_uri
    )

    if "access_token" not in result:
        return render(request, 'scheduler/error.html', {'error': "Failed to acquire token."})

    # request.session["access_token"] = result["access_token"]
    # After acquiring result:
    if "access_token" in result:
        request.session["access_token"] = result["access_token"]

    # Continue flow
    form_data = request.session.get('schedule_form_data')
    if not form_data:
        return render(request, 'scheduler/error.html', {'error': "Missing session data. Please re-submit."})

    user = request.user
    sched, created = Schedule.objects.update_or_create(
        user=user,
        defaults={
            'receiver': form_data['receiver'],
            'filepath': form_data['filepath'],
            'day': form_data['day'],
            'time': dt.datetime.strptime(form_data['time'], "%H:%M").time(),
            'active': True,
        }
    )

    set_schedule_config(
        receiver=form_data['receiver'],
        filepath=form_data['filepath'],
        day=form_data['day'],
        time=form_data['time']
    )

    del request.session['schedule_form_data']

    return render(request, 'scheduler/confirmation.html', {
        'day': sched.day.capitalize(),
        'time': form_data['time'],
        'filepath': sched.filepath
    })


# signup stays unchanged
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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

