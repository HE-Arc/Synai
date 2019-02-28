from django.shortcuts import render
from django.views import generic, View

# Create your views here.

def home(request):
    return render(request, 'home.html')

class FeedView(generic.TemplateView):
    template_name = "feed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        return context

class HistoryView(generic.TemplateView):
    template_name = "history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        return context

class DashboardView(generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add context data
        return context