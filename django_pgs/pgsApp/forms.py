from secrets import choice

from PIL import Image
from django import forms

from . import models

from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User

from .models import Photo


class SaveUser(UserCreationForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)


    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name','password1', 'password2',)

class UpdateProfile(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")

class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Confirm New Password")
    class Meta:
        model = User
        fields = ('old_password','new_password1', 'new_password2')

class SaveUpload(forms.ModelForm):
    user = forms.CharField(max_length=30)
    image_path = forms.ImageField()
    thumbnail_path = forms.ImageField()

    class Meta:
        model = models.Gallery
        fields = ('user','image_path', 'thumbnail_path', )

    def clean_user(self):
        userID = self.cleaned_data['user']
        try:
            user = User.objects.get(id = userID)
            return user
        except:
            raise forms.ValidationError("Invalid given User ID")
    
    def clean_thumbnails(self):
        print(self.data)
        raise forms.ValidationError("Test Error")

class PhotoForm(forms.ModelForm):
    # x = forms.FloatField(widget=forms.HiddenInput())
    # y = forms.FloatField(widget=forms.HiddenInput())
    # width = forms.FloatField(widget=forms.HiddenInput())
    # height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Photo
    #     fields = ('file', 'x', 'y', 'width', 'height', )
        fields = "__all__"
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'image/*'  # this is not an actual validation! don't rely on that!
            })
        }
    def clean_user(self):
        userID = self.cleaned_data['user']
        try:
            user = User.objects.get(id = userID)
            return user
        except:
            raise forms.ValidationError("Invalid given User ID")

    def save(self):
        photo = super(PhotoForm, self).save()

        # x = self.cleaned_data.get('x')
        # y = self.cleaned_data.get('y')
        # w = self.cleaned_data.get('width')
        # h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        # cropped_image = image.crop((x, y, w+x, h+y))
        # resized_image = image.resize((200, 200), Image.ANTIALIAS)
        # resized_image.save(photo.file.path)

        return photo