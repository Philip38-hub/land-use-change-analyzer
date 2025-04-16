from django import forms
from .models import AnalysisProject, AerialImage, LandUseClass

class AerialImageForm(forms.ModelForm):
    """Form for uploading aerial images."""
    class Meta:
        model = AerialImage
        fields = ['name', 'year', 'image', 'extent_north', 'extent_south', 'extent_east', 'extent_west']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'extent_north': forms.NumberInput(attrs={'class': 'form-control'}),
            'extent_south': forms.NumberInput(attrs={'class': 'form-control'}),
            'extent_east': forms.NumberInput(attrs={'class': 'form-control'}),
            'extent_west': forms.NumberInput(attrs={'class': 'form-control'}),
        }