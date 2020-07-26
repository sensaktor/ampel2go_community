from django.contrib import admin
from tinymce.widgets import TinyMCE
from django.db import models

import pandas as pd








# archive

""" 
#from .models import WikiArticle, NewsArticle


class WikiArticleAdmin(admin.ModelAdmin):
    model = WikiArticle # obsolete, is implicitly given with Admin-class
    
    readonly_fields = ['chapter_subchapter_id']

    def chapter_subchapter_id(self, obj):
        return obj.get_chapter_subchapter_id()

    list_display = ['title','chapter_subchapter_id',  'date' , ]


class NewsArticleAdmin(admin.ModelAdmin):
    model = NewsArticle # obsolete, is implicitly given with Admin-class
    
    #readonly_fields = ['']


    list_display = ['title', 'date' , ]

# Register your models here.


admin.site.register(WikiArticle,WikiArticleAdmin)
admin.site.register(NewsArticle,NewsArticleAdmin)


class TutorialAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Title/date",  {"fields":["tutorial_title", "tutorial_published"]}),
        ("URL", {"fields": ["tutorial_slug"]}),
        ("Series", {"fields": ["tutorial_series"]}),
        ("Content", {"fields":["tutorial_content"]})
    ]
    


admin.site.register(TutorialCategory)
admin.site.register(TutorialSeries)
admin.site.register(Tutorial,TutorialAdmin)
 """


