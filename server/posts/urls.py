from django.urls import path
from . import views
from applications import views as application_views

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('job/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('job/create/', views.JobCreateView.as_view(), name='job_create'),
    path('job/<int:pk>/update/', views.JobUpdateView.as_view(), name='job_update'),
    path('job/<int:pk>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    path('api/jobs/', views.JobListCreateAPIView.as_view(), name='api_job_list_create'),
    path('api/jobs/<int:pk>/', views.JobRetrieveUpdateDestroyAPIView.as_view(), name='api_job_detail'),
    path('api/applications/', application_views.ApplicationListCreateAPIView.as_view(), name='api_application_list_create'),
    path('api/applications/<int:pk>/', application_views.ApplicationRetrieveUpdateDestroyAPIView.as_view(), name='api_application_detail'),
    path('api/applications/<int:pk>/resume/', application_views.application_resume, name='api_application_resume'),
    path('api/crm/customers-statistic', application_views.CustomerStatisticAPIView.as_view(), name='api_crm_customers_statistic'),
    path('api/sales/dashboard', application_views.SalesDashboardAPIView.as_view(), name='api_sales_dashboard'),
]
