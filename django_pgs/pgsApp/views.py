from venv import logger

import numpy as np
from PIL import Image
from django.shortcuts import redirect, render
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from . import models, forms
import cv2 as cv
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from .models import Photo


def context_data():
    context = {
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'Image Inpainting System',
        'topbar' : True,
        'footer' : True,
    }

    return context


class impaint(forms.SaveUpload):
    # x = forms.FloatField(widget=forms.HiddenInput())
    # y = forms.FloatField(widget=forms.HiddenInput())
    # width = forms.FloatField(widget=forms.HiddenInput())
    # height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = models.Gallery
        fields = ('user', 'image_path', 'thumbnail_path',)

    def clean_user(self):
        userID = self.cleaned_data['user']
        try:
            user = User.objects.get(id=userID)
            return user
        except:
            raise forms.ValidationError("Invalid given User ID")

    def clean_thumbnails(self):
        print(self.data)
        raise forms.ValidationError("Test Error")

    def save(self):
        photo = super(impaint, self).save()

        # res = Image.open(photo.image_path)
        # imag = Image.open(photo.image_path)

        class Sketcher:
            def __init__(self, windowname, dests, colors_func):
                self.prev__pt = None
                self.windowname = windowname
                self.dests = dests
                self.colors_func = colors_func
                self.dirty = False
                self.show()
                cv.setMouseCallback(self.windowname, self.on_Mouse)

            def show(self):
                cv.imshow(self.windowname, self.dests[0])
                cv.imshow(self.windowname + "Masks", self.dests[1])

            def on_Mouse(self, event, x, y, flags, param):
                pt = (x, y)

                if event == cv.EVENT_LBUTTONDOWN:
                    self.prev__pt = pt

                elif event == cv.EVENT_LBUTTONUP:
                    self.prev__pt = None

                if self.prev__pt and flags & cv.EVENT_FLAG_LBUTTON:
                    for dst, color in zip(self.dests, self.colors_func()):
                        cv.line(dst, self.prev__pt, pt, color, 5)
                        self.dirty = True
                        self.prev__pt = pt
                        self.show()

        def main():
            print("Inpainting Python ")
            print("Keys: ")
            print("t- inpainting using Fast Marching method")
            print("n- Inpainting using NS technique")
            print("r-reset the mask")
            print("ESC-exit ")
            img = cv.imread(photo.image_path.path)

            if img is None:
                print("Failed to import the Image".format(img))
                return

            img_mask = img.copy()
            inpaintMask = np.zeros(img.shape[:2], np.uint8)
            sketch = Sketcher('image', [img_mask, inpaintMask], lambda: ((255, 255, 255,), 255))

            while True:
                ch = cv.waitKey(0)

                if ch == 27:
                    break
                if ch == ord('t'):
                    res = cv.inpaint(src=img_mask, inpaintMask=inpaintMask, inpaintRadius=4, flags=cv.INPAINT_TELEA)
                    cv.imshow("Inpaint using Fast March Methodology", res)

                if ch == ord('n'):
                    res = cv.inpaint(src=img_mask, inpaintMask=inpaintMask, inpaintRadius=4, flags=cv.INPAINT_NS)
                    cv.imshow("Inpaint using NS segmentation", res)

                if ch == ord('r'):
                    img_mask[:] = img
                    inpaintMask[:] = 0
                    sketch.show()
            #new code
            # Convert the image from BGR to HSV color space
            image = cv.cvtColor(res, cv.COLOR_RGB2HSV)

            # Adjust the hue, saturation, and value of the image
            # Adjusts the hue by multiplying it by 0.7
            #image[:, :, 0] = image[:, :, 0] * 0.7
            # Adjusts the saturation by multiplying it by 1.5
            #image[:, :, 1] = image[:, :, 1] * 1.5
            # Adjusts the value by multiplying it by 0.5
            #image[:, :, 2] = image[:, :, 2] * 0.5

            # Convert the image back to BGR color space
            #res = cv.cvtColor(image, cv.COLOR_HSV2BGR)

            #Above till new_code
            cv.imwrite("restor image.JPG", res)
            cv.destroyAllWindows()
            img = Image.open("restor image.JPG")
            newsize = (300, 300)
            img = img.resize(newsize)
            outfile = img.save(photo.image_path.path)
            img.close()
        main()
        return photo




def userregister(request):
    context = context_data()
    context['topbar'] = False
    context['footer'] = False
    context['page_title'] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, 'register.html', context)

@login_required
def upload_modal(request):
    context = context_data()
    return render(request, 'upload.html', context)

@login_required
def upload_inpaint(request):
    context = context_data()
    return render(request, 'upload_inpaint.html', context)

def save_register(request):
    resp={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account has been created succesfully")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
            
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_profile(request):
    context = context_data()
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context =context_data()
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)


# Create your views here.
def login_page(request):
    context = context_data()
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request, 'CustomLogin.html', context)

def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username1']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

@login_required
def home(request):
    context = context_data()
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['uploads'] = models.Gallery.objects.filter(delete_flag = 0, user = request.user).count()
    context['trash'] = models.Gallery.objects.filter(delete_flag = 1, user = request.user).count()
    print(context)
    return render(request, 'home.html', context)

def logout_user(request):
    logout(request)
    return redirect('login-page')
    
@login_required
def profile(request):
    context = context_data()
    context['page'] = 'profile'
    context['page_title'] = "Profile"
    return render(request,'profile.html', context)

@login_required
def save_upload(request):
    resp ={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUpload(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        messages.success(request, "New Upload has been save succesfully.")
        resp['status'] = 'success'
    else:
        for field in form:
            for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def inpaint(request):
    # context = context_data()
    # context['page_title'] = "Inpaint"
    # # photos = Photo.objects.all()
    # # context['photos']=photos
    # if request.method == 'POST':
    #     form = impaint(request.POST, request.FILES)
    #     context['form']=form
    #     if form.is_valid():
    #         form.save()
    #         return redirect('inpaint')
    # else:
    #     form = impaint()
    #     context['form'] = form
    # return render(request, 'inpaint.html',context)
    resp = {'status': 'failed', 'msg': ''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = impaint(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        messages.success(request, "New Restored Image Upload has been save succesfully.")
        resp['status'] = 'success'
    else:
        for field in form:
            for error in field.errors:
                if resp['msg'] != '':
                    resp['msg'] += str('<br />')
                resp['msg'] += str(f"[{field.name}] {error}.")
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_gallery(request):
    context = context_data()
    context['page_title'] ="Gallery"
    context['photos'] = models.Gallery.objects.filter(user = request.user, delete_flag = 0).all()
    return render(request, 'gallery.html', context) 

@login_required
def view_trash(request):
    context = context_data()
    context['page_title'] ="Trashed Images"
    context['photos'] = models.Gallery.objects.filter(user = request.user, delete_flag = 1).all()
    return render(request, 'trash.html', context) 

@login_required
def trash_upload(request, pk =None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'No data sent in this request'
    else:
        try:
            upload = models.Gallery.objects.filter(id=pk).update(delete_flag = 1)
            resp['status'] = 'success'
            messages.success(request, 'Image has been moved to trash successfully')
        except:
            resp['msg'] = 'Invalid data to delete'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def restore_upload(request, pk =None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'No data sent in this request'
    else:
        try:
            upload = models.Gallery.objects.filter(id=pk).update(delete_flag = 0)
            resp['status'] = 'success'
            messages.success(request, 'Image has been restore successfully')
        except:
            resp['msg'] = 'Invalid data to delete'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_upload(request, pk =None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'No data sent in this request'
    else:
        try:
            upload = models.Gallery.objects.get(id=pk).delete()
            resp['status'] = 'success'
            messages.success(request, 'Image has been deleted forever successfully')
        except Exception as e:
            logger.error('Failed to upload to ftp: %s', repr(e))
            resp['msg'] = 'Invalid data to delete'+str(e)
    return HttpResponse(json.dumps(resp), content_type="application/json")
    
