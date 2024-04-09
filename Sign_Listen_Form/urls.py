from django.urls import re_path as url

from Sign_Listen_Form.views import FormDataView

urlpatterns = [
    url('listen/form',FormDataView.as_view()),
]