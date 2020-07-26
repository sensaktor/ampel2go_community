from django.db import models
from django.utils import timezone
from datetime import datetime
from tinymce.models import HTMLField


# Create your models here.


class Occupancy(models.Model):
    ''' Class which handles occupancy '''
    capacity = models.IntegerField(default=3)
    person_count = models.IntegerField(default=1)
    date = models.DateTimeField(default=timezone.now)
    direction = models.IntegerField(default=1)




    def get_occupancy_color(self):
        '''calculate occupancy for object and return green or red 
        depending on positive or negative value'''
        occupancy_color = "green"
        occupancy = self.capacity - self.person_count
        if occupancy > 0:
            occupancy_color = "green"
        if occupancy <= 0:
            occupancy_color = "red"
        return occupancy_color

class AreaThreshold(models.Model):
    "Class which handles the areathreshold in the settings menu for adjustment in the store"
    area_threshold = models.IntegerField(default=10)


#########################
## _archive


"""


class Newsletter(models.Model):
    email = models.EmailField()




class WikiArticle(models.Model): 
    id = models.AutoField(primary_key=True)
    chapter_id = models.IntegerField(default=1)
    subchapter_id = models.IntegerField(default=1)
    title = models.CharField(default="title",max_length=100)
    title_short = models.CharField(default="title_short", max_length=27)
    body = HTMLField(default="body")
    date = models.DateField(default=timezone.now)


        
    def get_chapter_subchapter_id(self):
        self.chapter_subchapter_id= str(self.chapter_id) + "." +  str(self.subchapter_id)
        return self.chapter_subchapter_id

    def get_chapter_subchapter_id_hashed(self):
        self.chapter_subchapter_id_hashed = '#' + str(self.chapter_id) + "." + str(self.subchapter_id)

    class Meta:
        ordering = ['chapter_id', 'subchapter_id', 'date']



    def __str__(self):
        return self.title
    

class NewsArticle(models.Model): 
    id = models.AutoField(primary_key=True)
    title = models.CharField(default="title",max_length=100)
    title_short = models.CharField(default="title_short", max_length=27)
    body = HTMLField(default="body")
    date = models.DateField(default=timezone.now)


    class Meta:
        ordering = ['-date'] # descending with "-"



    def __str__(self):
        return self.title


 class TutorialCategory(models.Model):
    tutorial_category = models.CharField(max_length=200) 
    category_summary = models.CharField(max_length=200)
    category_slug = models.CharField(max_length=200, default=2 )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.tutorial_category


class TutorialSeries(models.Model):
    tutorial_series = models.CharField(max_length=200)
    tutorial_category = models.ForeignKey(TutorialCategory,
                                          default=2,
                                          verbose_name = "Category",
                                          on_delete=models.SET_DEFAULT)
    series_summary = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "Series"

    def __str__(self):
        return self.tutorial_series


class Tutorial(models.Model): 
    tutorial_title = models.CharField(max_length=200) 
    tutorial_content = models.TextField()
    tutorial_published = models.DateTimeField("date published", default=timezone.now) 
    tutorial_series = models.ForeignKey(TutorialSeries, default=2,
                                        verbose_name = "Series",
                                        on_delete=models.SET_DEFAULT)
    tutorial_slug = models.CharField(max_length=200, default=2)

    def __str__(self):
        return self.tutorial_title """