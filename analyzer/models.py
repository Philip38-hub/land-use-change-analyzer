from django.db import models
# from django.contrib.gis.db import models as gis_models
import uuid
import os

def get_upload_path(instance, filename):
    """Generate a unique path for the uploaded file."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class AnalysisProject(models.Model):
    """Model to store information about a land use change analysis project."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AerialImage(models.Model):
    """Model to store information about aerial images."""
    project = models.ForeignKey(AnalysisProject, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_path)
    year = models.IntegerField()
    name = models.CharField(max_length=255)
    classified_image = models.ImageField(upload_to='results', null=True, blank=True)
    
    # Geospatial fields
    extent_north = models.FloatField(null=True, blank=True)
    extent_south = models.FloatField(null=True, blank=True)
    extent_east = models.FloatField(null=True, blank=True)
    extent_west = models.FloatField(null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

class LandUseClass(models.Model):
    """Model to define land use classes."""
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)  # Hex color code
    
    def __str__(self):
        return self.name

class AnalysisResult(models.Model):
    """Model to store results of land use change analysis."""
    project = models.OneToOneField(AnalysisProject, on_delete=models.CASCADE, related_name='result')
    earlier_image = models.ForeignKey(AerialImage, on_delete=models.CASCADE, related_name='earlier_results')
    later_image = models.ForeignKey(AerialImage, on_delete=models.CASCADE, related_name='later_results')
    change_map = models.ImageField(upload_to='results', null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis result for {self.project.name}"

class LandUseStatistics(models.Model):
    """Model to store statistics about land use classes for each image."""
    image = models.ForeignKey(AerialImage, on_delete=models.CASCADE, related_name='statistics')
    land_use_class = models.ForeignKey(LandUseClass, on_delete=models.CASCADE)
    area_pixels = models.IntegerField()
    percentage = models.FloatField()
    
    def __str__(self):
        return f"{self.land_use_class.name} in {self.image.name}"

class ChangeStatistics(models.Model):
    """Model to store statistics about land use changes."""
    result = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name='change_statistics')
    from_class = models.ForeignKey(LandUseClass, on_delete=models.CASCADE, related_name='changes_from')
    to_class = models.ForeignKey(LandUseClass, on_delete=models.CASCADE, related_name='changes_to')
    area_pixels = models.IntegerField()
    percentage = models.FloatField()
    
    def __str__(self):
        return f"Change from {self.from_class.name} to {self.to_class.name}"