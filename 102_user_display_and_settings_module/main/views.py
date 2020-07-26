"vievs.py"


from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render

from .forms import OccupancyForm, AreaThresholdForm
from .models import Occupancy, AreaThreshold
from django.db.models import F, Count


def homepage(request):
    ''' returns the homepage context'''
    try:
        occupancy_latest = Occupancy.objects.order_by('id').last()
        area_threshold_latest = AreaThreshold.objects.order_by('id').last()
        if occupancy_latest is None:
            occupancy_latest = Occupancy()
        if area_threshold_latest is None:
            area_threshold_latest = AreaThreshold()
    except Occupancy.DoesNotExist:
        occupancy_latest = Occupancy()
    except AreaThreshold.DoesNotExist:
        area_threshold_latest = AreaThreshold()


    occupancy_color = occupancy_latest.get_occupancy_color()

    occupancy_color_smiley = '<img src="../../static/main/images/ampel2go_'+ \
        occupancy_color + '.png" alt="" class="responsive">'

    if occupancy_color == "green": 
        occupancy_color_number = '<span style="color: #00FF00;" >' + str(occupancy_latest.person_count) + '</span>'
    if occupancy_color == "red":
        occupancy_color_number = '<span style="color: #ff0505;" >' + str(occupancy_latest.person_count) + '</span>'

    #messages.success(request, f"aktuelle farbe {occupancy_color}")



    if request.method == "POST":
        if 'capacity_btn' in request.POST:
            form = OccupancyForm(request.POST)
            if form.is_valid():
                obj = Occupancy.objects.order_by('id').last()
                obj.capacity = form.cleaned_data['capacity']
                obj.save()
                messages.success(request, f"Neue Kapazität {obj.capacity}")
                area_threshold = AreaThresholdForm()
                return HttpResponseRedirect("/")

        elif 'area_threshold_btn' in request.POST:
            area_threshold_form = AreaThresholdForm(request.POST)
            if area_threshold_form.is_valid():
                obj = AreaThreshold.objects.order_by('id').last()
                obj.area_threshold = area_threshold_form.cleaned_data['area_threshold']
                obj.save()
                messages.success(request, f"Neuer Abstandsparameter {obj.area_threshold}")
                return HttpResponseRedirect("/")



    if(request.GET.get('minus_btn')):
        obj = Occupancy.objects.order_by('id').last()
        obj.person_count -= 1
        obj.save()

        messages.success(request, f"Neue Besucherzahl {obj.person_count}")
        print('Button clicked')
        return HttpResponseRedirect("/")

    if(request.GET.get('plus_btn')):
        obj = Occupancy.objects.order_by('id').last()
        obj.person_count += 1
        obj.save()

        messages.success(request, f"Neue Besucherzahl {obj.person_count}")
        print('Button clicked')
        return HttpResponseRedirect("/")

   
    if(request.GET.get('change_direction')):
        obj = Occupancy.objects.order_by('id').last()
        if (obj.direction == 1 or obj.direction == -1):
            obj.direction = obj.direction * -1
        else:     
            obj.direction = 1
        
        obj.save()

        messages.success(request, f"Zählrichtung getauscht")
        print(obj.direction)
        return HttpResponseRedirect("/")

    else:
        form = OccupancyForm()
        area_threshold = AreaThresholdForm()

    return render(request=request,
                  template_name='homepage.html',
                  context={"form":form,
                           "area_threshold": area_threshold,
                           "person_count":occupancy_latest.person_count,
                           "capacity": occupancy_latest.capacity,
                           "occupancy_color": occupancy_color,
                           "occupancy_color_smiley": occupancy_color_smiley,
                           "occupancy_color_number": occupancy_color_number,
                            }
                    )


def settings(request):
    ''' returns the homepage context'''
    try:
        occupancy_latest = Occupancy.objects.order_by('id').last()
        area_threshold_latest = AreaThreshold.objects.order_by('id').last()
        if occupancy_latest is None:
            occupancy_latest = Occupancy()
        if area_threshold_latest is None:
            area_threshold_latest = AreaThreshold()
    except Occupancy.DoesNotExist:
        occupancy_latest = Occupancy()
    except AreaThreshold.DoesNotExist:
        area_threshold_latest = AreaThreshold()


    occupancy_color = occupancy_latest.get_occupancy_color()

    occupancy_color_smiley = '<img src="../../static/main/images/ampel2go_'+ \
        occupancy_color + '.png" alt="" class="responsive">'

    if occupancy_color == "green": 
        occupancy_color_number = '<span style="color: #00FF00;" >' + str(occupancy_latest.person_count) + '</span>'
    if occupancy_color == "red":
        occupancy_color_number = '<span style="color: #ff0505;" >' + str(occupancy_latest.person_count) + '</span>'

    #messages.success(request, f"aktuelle farbe {occupancy_color}")



    if request.method == "POST":
        if 'capacity_btn' in request.POST:
            form = OccupancyForm(request.POST)
            if form.is_valid():
                obj = Occupancy.objects.order_by('id').last()
                obj.capacity = form.cleaned_data['capacity']
                obj.save()
                messages.success(request, f"Neue Kapazität {obj.capacity}")
                area_threshold = AreaThresholdForm()
                return HttpResponseRedirect("/settings")

        elif 'area_threshold_btn' in request.POST:
            area_threshold_form = AreaThresholdForm(request.POST)
            if area_threshold_form.is_valid():
                obj = AreaThreshold.objects.order_by('id').last()
                obj.area_threshold = area_threshold_form.cleaned_data['area_threshold']
                obj.save()
                messages.success(request, f"Neuer Abstandsparameter {obj.area_threshold}")
                return HttpResponseRedirect("/settings")



    if(request.GET.get('minus_btn')):
        obj = Occupancy.objects.order_by('id').last()
        obj.person_count -= 1
        obj.save()

        messages.success(request, f"Neue Besucherzahl {obj.person_count}")
        print('Button clicked')
        return HttpResponseRedirect("/settings")

    if(request.GET.get('plus_btn')):
        obj = Occupancy.objects.order_by('id').last()
        obj.person_count += 1
        obj.save()

        messages.success(request, f"Neue Besucherzahl {obj.person_count}")
        print('Button clicked')
        return HttpResponseRedirect("/settings")

   
    if(request.GET.get('change_direction')):
        obj = Occupancy.objects.order_by('id').last()
        if (obj.direction == 1 or obj.direction == -1):
            obj.direction = obj.direction * -1
        else:     
            obj.direction = 1
        
        obj.save()

        messages.success(request, f"Zählrichtung getauscht")
        print(obj.direction)
        return HttpResponseRedirect("/settings")

    else:
        form = OccupancyForm()
        area_threshold = AreaThresholdForm()

    return render(request=request,
                  template_name='settings.html',
                  context={"form":form,
                           "area_threshold": area_threshold,
                           "person_count":occupancy_latest.person_count,
                           "capacity": occupancy_latest.capacity,
                           "occupancy_color": occupancy_color,
                           "occupancy_color_smiley": occupancy_color_smiley,
                           "occupancy_color_number": occupancy_color_number,
                            }
                    )



def testpage(request):
    ''' returns the homepage context'''
    try:
        occupancy_latest = Occupancy.objects.order_by('id').last()
    except Occupancy.DoesNotExist:
        occupancy_latest = Occupancy()


    occupancy_color = occupancy_latest.get_occupancy_color()


    occupancy_color_smiley = '<img src="../../static/main/images/ampel2go_'+ \
        occupancy_color+'.png" alt="" class="responsive">'

    if(request.GET.get('print_btn')):
        obj = Occupancy.objects.order_by('id').last()
        obj.person_count += 1
        obj.save()
        messages.success(request, f"Neuer Besucherzahl {obj.person_count}")
        print('Button clicked')
        return HttpResponseRedirect("/testpage")



    return render(request=request,
                  template_name='testpage.html',
                  context={
                           "person_count":occupancy_latest.person_count,
                           "capacity": occupancy_latest.capacity,
                           "occupancy_color": occupancy_color,
                           "occupancy_color_smiley": occupancy_color_smiley,
                            }
                    )
    #messages.success(request, f"aktuelle farbe {occupancy_color}")






def homepage_ajax_update(request):
    "homepage_ajax-update"
    # here you return whatever data you need updated in your template

    try:
        occupancy_latest = Occupancy.objects.order_by('id').last()
    except Occupancy.DoesNotExist:
        occupancy_latest = Occupancy()

    occupancy_color = occupancy_latest.get_occupancy_color()
    occupancy_color_smiley = '<img src="../../static/main/images/ampel2go_'\
        +occupancy_color+'.png" alt="" class="responsive">'

    if occupancy_color == "green": 
        occupancy_color_number = '<span style="color: #00FF00;" >' + str(occupancy_latest.person_count) + '</span>'
    if occupancy_color == "red":
        occupancy_color_number = '<span style="color: #ff0505;" >' + str(occupancy_latest.person_count) + '</span>'

    return JsonResponse({
        'person_count': occupancy_latest.person_count,
        'capacity': occupancy_latest.capacity,
        'occupancy_color': occupancy_color,
        'occupancy_color_smiley':occupancy_color_smiley,
        'occupancy_color_number':occupancy_color_number,
    })

#--------------------------

# def testpage(request):
#     ''' returns the testpage context'''
#     form = ""
#     try:
#         occupancy_latest = Occupancy.objects.values("capacity").latest("date")
#     except Occupancy.DoesNotExist:
#         occupancy_latest = Occupancy()


#     #return JsonResponse(occupancy_latest)
    
#     return render(request=request,
#                    template_name='testpage.html',
#                    context={"form":form}, )





# def validate_username(request):
#     username = request.GET.get('username', None)
#     exists = Occupancy.objects.order_by('id').last()
#     if exists:
#         is_taken = True
#     if not exists:
#         is_taken = False
#     data = {
#         'is_taken': is_taken
#     }
#     return JsonResponse(data)




#-----------------

def imprint(request):
    ''' returns the imprint context'''
    form = ""
    return render(request=request,
                  template_name='imprint.html',
                  context={"form":form}, )

def data_privacy(request):
    ''' returns the data privacy context'''
    form = ""
    return render(request=request,
                  template_name='data-privacy.html',
                  context={"form":form}, )



###########################################
## _archive



# from .forms import NewUserForm, EmailNewsletterSignup


# # Create your views here.
# def homepage(request):
#     if request.method == "POST":
#         form = EmailNewsletterSignup(request.POST)
#         if form.is_valid(): 
#             obj = Newsletter()
#             obj.email = form.cleaned_data['email']
#             obj.save()
#             messages.success(request, f"Vielen lieben Dank für Deine Unterstützung, {obj.email} !!!")
#     else:
#         form = EmailNewsletterSignup
 
#     return render(request=request,
#                   template_name='homepage.html',
#                   context={"form":form}, ) 


# def imprint(request): 
#     form = "" 
#     return render(request=request,
#                   template_name='imprint.html',
#                   context={"form":form}, ) 

# def data_privacy(request): 
#     form = "" 
#     return render(request=request,
#                   template_name='data-privacy.html',
#                   context={"form":form}, ) 

