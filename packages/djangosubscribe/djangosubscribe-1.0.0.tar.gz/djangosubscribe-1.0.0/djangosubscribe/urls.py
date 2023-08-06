from django.conf.urls import re_path
from djangosubscribe import views


app_name = "djangosubscribe"


urlpatterns = [
    re_path(r"^$", views.SubscriberView.as_view(), name="subscriber")
]