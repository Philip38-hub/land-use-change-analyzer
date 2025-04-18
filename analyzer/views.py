from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import AnalysisProject, AerialImage, LandUseClass, AnalysisResult, LandUseStatistics, ChangeStatistics
from .forms import AnalysisProjectForm, AerialImageForm
from .utils import classify_image, detect_changes

def index(request):
    """Home page view."""
    projects = AnalysisProject.objects.all().order_by('-created_at')[:5]
    return render(request, 'index.html', {'projects': projects})

class ProjectListView(ListView):
    """View to list all projects."""
    model = AnalysisProject
    template_name = 'project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']

class ProjectDetailView(DetailView):
    """View to display details of a project."""
    model = AnalysisProject
    template_name = 'project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        images = project.images.all().order_by('year')
        context['images'] = images
        
        # Count classified images
        classified_count = images.filter(classified_image__isnull=False).count()
        context['classified_count'] = classified_count
        
        # Check if this project has a result
        try:
            result = project.result
            context['result'] = result
            context['has_result'] = True
        except AnalysisResult.DoesNotExist:
            context['has_result'] = False
            
        return context

class ProjectCreateView(CreateView):
    """View to create a new project."""
    model = AnalysisProject
    form_class = AnalysisProjectForm
    template_name = 'project_form.html'
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(UpdateView):
    """View to update a project."""
    model = AnalysisProject
    form_class = AnalysisProjectForm
    template_name = 'project_form.html'
    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(DeleteView):
    """View to delete a project."""
    model = AnalysisProject
    template_name = 'project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

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

def classify_land_use(request, image_id):
    """View to classify land use in an image."""
    image = get_object_or_404(AerialImage, id=image_id)
    
    # Perform classification
    if request.method == 'POST':
        success, message = classify_image(image)
        
        if success:
            messages.success(request, 'Land use classification completed successfully.')
        else:
            messages.error(request, f'Error during classification: {message}')
            
        return redirect('project_detail', pk=image.project.id)
    
    return render(request, 'classify_confirm.html', {'image': image})

def analyze_changes(request, project_id):
    """View to analyze changes between two images."""
    project = get_object_or_404(AnalysisProject, id=project_id)
    images = project.images.all().order_by('year')
    
    if images.count() < 2:
        messages.error(request, 'At least two images are required for change analysis.')
        return redirect('project_detail', pk=project_id)
    
    # Check if images have been classified
    if not all(img.classified_image for img in images):
        messages.error(request, 'All images must be classified before analyzing changes.')
        return redirect('project_detail', pk=project_id)
    
    if request.method == 'POST':
        # Get the two images to compare
        earlier_image = images.first()
        later_image = images.last()
        
        # Perform change detection
        success, message = detect_changes(project, earlier_image, later_image)
        
        if success:
            messages.success(request, 'Land use change analysis completed successfully.')
        else:
            messages.error(request, f'Error during analysis: {message}')
            
        return redirect('project_detail', pk=project_id)
    
    return render(request, 'analyze_confirm.html', {'project': project, 'images': images})
