from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import AnalysisProject, AerialImage, LandUseClass, AnalysisResult, LandUseStatistics, ChangeStatistics
from .forms import AnalysisProjectForm, AerialImageForm
# from .utils import classify_image, detect_changes

def upload_image(request, project_id):
    """View to upload an image for a project."""
    project = get_object_or_404(AnalysisProject, id=project_id)
    
    if request.method == 'POST':
        form = AerialImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.project = project
            image.save()
            messages.success(request, 'Image uploaded successfully.')
            return redirect('project_detail', pk=project_id)
    else:
        form = AerialImageForm()
    
    return render(request, 'upload_image.html', {
        'form': form,
        'project': project
    })
