from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from likeSys import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('likeSys/',include('likeSys.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)