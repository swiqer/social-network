from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static


handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('ya_admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
]

urlpatterns += [
    path('about_author/', views.flatpage, {'url': '/about_author/'},
         name='about-author'),
    path('about_spec/', views.flatpage, {'url': '/about_spec/'},
         name='about-spec'),
    path('', include('posts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
