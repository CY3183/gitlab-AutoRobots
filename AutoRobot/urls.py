"""
URL configuration for AutoRobot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
# from django.contrib.staticfiles.views import serve  # 添加这行
# from django.views.static import serve
from django.conf.urls.static import serve
from django.urls import re_path
from AutoRobot import settings


urlpatterns = [
    path('llapi/admin/v1/', admin.site.urls),
    path(r'llapis/autorobot/', include([
        path(r'sign/', include('Sign_Listen_Form.urls')),  # 自动签收---监听表单
        path(r'reply/', include('Reply_Listen_Flow.urls'))  # 自动回复--监听流程
    ])),
    re_path(r'^llapi/admin/static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]
