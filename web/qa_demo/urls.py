from django.conf.urls import include, url
import os,sys
from django.contrib import admin
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir)
print(cur_dir)
import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Examples:
    # url(r'^$', 'classify.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$',views.analyze, name='analyze'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'static/(?P<path>.*)$','diango.views.static.serve',{'document_root':'/opt/xiaoxue.ma/NER/web_ner/static'})
]
