import os
import numpy as np
from skimage import io
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, to_rgb
from django.conf import settings
from .models import LandUseClass

def ensure_default_classes():
    """Ensure default land use classes exist."""
    default_classes = [
        {'name': 'Urban', 'color': '#FF0000'},  # Red
        {'name': 'Vegetation', 'color': '#00FF00'},  # Green
        {'name': 'Water', 'color': '#0000FF'},  # Blue
        {'name': 'Barren', 'color': '#FFFF00'},  # Yellow
    ]
    
    for cls in default_classes:
        LandUseClass.objects.get_or_create(name=cls['name'], color=cls['color'])

def classify_image(image_obj):
    """
    Classify an aerial image into land use categories.
    
    Args:
        image_obj: AerialImage model instance
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Ensure default classes exist
        ensure_default_classes()
        
        # Get land use classes
        land_use_classes = list(LandUseClass.objects.all())
        num_classes = len(land_use_classes)
        
        # Load the image
        img_path = os.path.join(settings.MEDIA_ROOT, image_obj.image.name)
        img = io.imread(img_path)
        
        # Reshape the image for clustering
        h, w, d = img.shape
        img_array = img.reshape(h * w, d)
        
        # Perform k-means clustering
        kmeans = KMeans(n_clusters=num_classes, random_state=42)
        labels = kmeans.fit_predict(img_array)
        
        # Reshape back to image dimensions
        segmented = labels.reshape(h, w)
        
        # Create a colored image for visualization
        colors = [to_rgb(cls.color) for cls in land_use_classes]
        cmap = ListedColormap(colors)
        
        # Create the classified image
        plt.figure(figsize=(10, 10))
        plt.imshow(segmented, cmap=cmap)
        plt.axis('off')
        
        # Save the classified image
        classified_image_path = f'results/classified_{os.path.basename(image_obj.image.name)}'
        full_path = os.path.join(settings.MEDIA_ROOT, classified_image_path)
        plt.savefig(full_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        
        # Update the image object with the classified image path
        image_obj.classified_image = classified_image_path
        image_obj.save()
        
        # Calculate and save statistics
        calculate_land_use_statistics(image_obj, segmented, land_use_classes)
        
        return True, "Classification successful"
    
    except Exception as e:
        return False, str(e)
