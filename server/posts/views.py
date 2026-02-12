from django.shortcuts import render

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from .models import Job
from rest_framework import generics, permissions
from .serializers import JobSerializer
from users.authentication import CsrfExemptSessionAuthentication
from .permissions import JobAccessPermission
class JobListView(ListView):
    model = Job
    template_name = 'posts/job_list.html'
    context_object_name = 'jobs'  # default is object_list
    
    def get_queryset(self):
        user = self.request.user
        return Job.objects.visible_to(user)

class JobDetailView(DetailView):
    model = Job
    template_name = 'posts/job_detail.html'
    context_object_name = 'job'
    
    def get_queryset(self):
        user = self.request.user
        return Job.objects.visible_to(user)

class JobCreateView(CreateView):
    model = Job
    template_name = 'posts/job_form.html'
    fields = [
        'title', 'description', 'status', 'jobtype', 'jobtime',
        'shift', 'required_skills', 'domain'
    ]
    success_url = reverse_lazy('job_list')
    
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.created_by = self.request.user
        return super().form_valid(form)

class JobUpdateView(UpdateView):
    model = Job
    template_name = 'posts/job_form.html'
    fields = [
        'title', 'description', 'status', 'jobtype', 'jobtime',
        'shift', 'required_skills', 'domain'
    ]
    success_url = reverse_lazy('job_list')
    
    def get_queryset(self):
        user = self.request.user
        return Job.objects.visible_to(user)

class JobDeleteView(DeleteView):
    model = Job
    template_name = 'posts/job_confirm_delete.html'
    success_url = reverse_lazy('job_list')
    
    def get_queryset(self):
        user = self.request.user
        return Job.objects.visible_to(user)


class JobListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    
    def get_queryset(self):
        return Job.objects.visible_to(self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class JobRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [JobAccessPermission]
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    
    def get_queryset(self):
        return Job.objects.visible_to(self.request.user)
