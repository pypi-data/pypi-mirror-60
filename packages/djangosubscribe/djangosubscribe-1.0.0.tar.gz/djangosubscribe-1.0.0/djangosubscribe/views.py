from django.shortcuts import render, redirect
from django.views.generic import View
from djangosubscribe.forms import SubscriberForm


# Create your views here.
class SubscriberView(View):
    template_name = "djangoadmin/djangosubscribe/create_subscriber_formview.html"

    def get(self, request, *args, **kwargs):
        subscriberform = SubscriberForm()
        context = {"subscriberform": subscriberform}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        subscriberform = SubscriberForm(request.POST or None)
        if subscriberform.is_valid():
            subscriberform.save()
        return redirect("djangosubscribe:subscriber")
