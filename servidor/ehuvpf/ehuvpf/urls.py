"""
URL configuration for ehuvpf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("map/", include("api.urls")),
    path("admin/", admin.site.urls),
]

from .settings import DEBUG
if DEBUG:
    from django.http import HttpRequest, HttpResponse
    from django.template import loader
    from django.urls import include, re_path
    def serve_smap(request: HttpRequest):
        file_name = request.path.split("smap/")[-1]
        extension = request.path.split(".")[-1]
        content_type = None
        if extension == "js":
            content_type = "text/javascript"
        if extension == "css":
            content_type = "text/css"
        if extension == "svg":
            content_type = "image/svg+xml"
        print(f"/var/www/map/{file_name}")
        with open(f"/var/www/map/{file_name}", "rb") as f:
            static_file = f.read()
        context = {
        }
        response = HttpResponse(static_file)
        # Al ser estáticas se les puede indicar que se guarden en el caché
        response.headers["Cache-Control"] = f"max-age={60*24*14}"
        if content_type is not None:
            response.headers["Content-Type"] = content_type
            print(content_type)
        return response
    urlpatterns.append(re_path("smap/*", serve_smap))
