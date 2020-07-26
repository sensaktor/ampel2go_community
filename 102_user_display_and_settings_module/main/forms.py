
"Forms "
from django import forms
from .models import Occupancy, AreaThreshold



class OccupancyForm(forms.Form):
    "capacity form docstring"
    capacity = forms.IntegerField(label="capacity")

    class Meta:
        model = Occupancy
        fields = ("id", "capacity", "date", "person_count")

#    screen_orientation = forms.RadioSelect(choices="hoch" )

class AreaThresholdForm(forms.Form):
    "capacity form docstring"
    area_threshold = forms.IntegerField(label="area_threshold")

    class Meta:
        model = AreaThreshold
        fields = ("area_threshold")




########################################################
## _archive


""" 
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1" , "password2" )
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class EmailNewsletterSignup(forms.Form): 
    email=forms.EmailField(label='Email Address', max_length=100)
     """

