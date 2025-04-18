import os
import numpy as np
from skimage import io
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, to_rgb
from django.conf import settings
from .models import LandUseClass, LandUseStatistics, AnalysisResult, ChangeStatistics

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

def calculate_land_use_statistics(image_obj, segmented, land_use_classes):
    """
    Calculate and save statistics about land use classes in an image.
    
    Args:
        image_obj: AerialImage model instance
        segmented: Numpy array with class labels
        land_use_classes: List of LandUseClass instances
    """
    # Delete existing statistics for this image
    LandUseStatistics.objects.filter(image=image_obj).delete()
    
    # Count pixels for each class
    total_pixels = segmented.size
    
    for i, cls in enumerate(land_use_classes):
        # Count pixels of this class
        pixels = np.sum(segmented == i)
        percentage = (pixels / total_pixels) * 100
        
        # Save statistics
        LandUseStatistics.objects.create(
            image=image_obj,
            land_use_class=cls,
            area_pixels=pixels,
            percentage=percentage
        )

def detect_changes(project, earlier_image, later_image):
    """
    Detect land use changes between two classified images.
    
    Args:
        project: AnalysisProject model instance
        earlier_image: AerialImage model instance (earlier date)
        later_image: AerialImage model instance (later date)
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Load classified images
        earlier_path = os.path.join(settings.MEDIA_ROOT, earlier_image.classified_image.name)
        later_path = os.path.join(settings.MEDIA_ROOT, later_image.classified_image.name)
        
        earlier_img = io.imread(earlier_path)
        later_img = io.imread(later_path)
        
        # Convert to grayscale if they're RGB
        if len(earlier_img.shape) > 2:
            earlier_img = earlier_img[:, :, 0]
        if len(later_img.shape) > 2:
            later_img = later_img[:, :, 0]
        
        # Ensure same dimensions
        h = min(earlier_img.shape[0], later_img.shape[0])
        w = min(earlier_img.shape[1], later_img.shape[1])
        earlier_img = earlier_img[:h, :w]
        later_img = later_img[:h, :w]
        
        # Create change map
        change_map = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Get land use classes
        land_use_classes = list(LandUseClass.objects.all())
        num_classes = len(land_use_classes)
        
        # Create change matrix
        change_matrix = np.zeros((num_classes, num_classes), dtype=int)
        
        # Calculate changes
        for i in range(h):
            for j in range(w):
                # Safely convert pixel to class index in [0, num_classes-1]
                from_class = int(np.clip(earlier_img[i, j], 0, 1) * (num_classes - 1))
                to_class = int(np.clip(later_img[i, j], 0, 1) * (num_classes - 1))
                
                # Increment change matrix
                change_matrix[from_class, to_class] += 1
                
                # Set change map color
                if from_class != to_class:
                    # Changed area - use "to" class color
                    color_hex = land_use_classes[to_class].color
                    rgb = to_rgb(color_hex)
                    change_map[i, j] = np.array(rgb) * 255
                else:
                    # Unchanged area - gray
                    change_map[i, j] = [200, 200, 200]
        
        # Save change map
        change_map_path = f'results/change_map_{project.id}.png'
        full_path = os.path.join(settings.MEDIA_ROOT, change_map_path)
        io.imsave(full_path, change_map)
        
        # Create or update result
        result, created = AnalysisResult.objects.update_or_create(
            project=project,
            defaults={
                'earlier_image': earlier_image,
                'later_image': later_image,
                'change_map': change_map_path
            }
        )
        
        # Save change statistics
        save_change_statistics(result, change_matrix, land_use_classes)
        
        return True, "Change detection successful"
    
    except Exception as e:
        return False, str(e)

def save_change_statistics(result, change_matrix, land_use_classes):
    """
    Save statistics about land use changes.
    
    Args:
        result: AnalysisResult model instance
        change_matrix: Numpy array with change counts
        land_use_classes: List of LandUseClass instances
    """
    # Delete existing statistics for this result
    ChangeStatistics.objects.filter(result=result).delete()
    
    total_pixels = np.sum(change_matrix)
    
    for i, from_class in enumerate(land_use_classes):
        for j, to_class in enumerate(land_use_classes):
            pixels = change_matrix[i, j]
            percentage = (pixels / total_pixels) * 100
            
            # Only save if there's a change
            if pixels > 0:
                ChangeStatistics.objects.create(
                    result=result,
                    from_class=from_class,
                    to_class=to_class,
                    area_pixels=pixels,
                    percentage=percentage
                )