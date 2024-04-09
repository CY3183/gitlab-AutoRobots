from django.urls import re_path as url

from Reply_Listen_Flow.views import FlowDataView

urlpatterns = [
    url('listen/flow',FlowDataView.as_view()),
]