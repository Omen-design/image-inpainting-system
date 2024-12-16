
from django.db import models
from django.utils import timezone

from PIL import Image
from django.contrib.auth.models import User


# Create your models here.
class Photo(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ImageField()
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'photo'
        verbose_name_plural = 'photos'


class Gallery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_path = models.ImageField(upload_to='images')
    thumbnail_path = models.ImageField(upload_to='thumbnails')
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "Uploaded Images"

    def __str__(self):
        return str(f"{self.user.username}")


    def save(self, *args, **kwargs):
        super(Gallery, self).save(*args, **kwargs)
        imag = Image.open(self.image_path.path)
        width = imag.width
        height = imag.height
        if imag.width > 640:
            width = 640
        if imag.height > 480:
            height = 480
        output_size = (width, height)
        imag.thumbnail(output_size)
        imag.save(self.thumbnail_path.path)

    def delete(self, *args, **kwargs):
        storage, path = self.image_path.storage, self.image_path.path
        storage.delete(path)
        storage, path = self.thumbnail_path.storage, self.thumbnail_path.path
        super(Gallery, self).delete(*args, **kwargs)
        storage.delete(path)
        

