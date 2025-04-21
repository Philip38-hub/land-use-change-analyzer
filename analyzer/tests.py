from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import AnalysisProject, AerialImage, LandUseClass, AnalysisResult
from . import utils
import numpy as np

class UtilsTests(TestCase):
    def setUp(self):
        LandUseClass.objects.create(name='Urban', color='#FF0000')
        LandUseClass.objects.create(name='Vegetation', color='#00FF00')
        LandUseClass.objects.create(name='Water', color='#0000FF')
        LandUseClass.objects.create(name='Barren', color='#FFFF00')

    @patch('analyzer.utils.io.imread')
    @patch('analyzer.utils.KMeans')
    @patch('analyzer.utils.plt')
    @patch('analyzer.utils.os.path.join', side_effect=lambda *args: '/tmp/' + args[-1])
    @patch('analyzer.utils.settings')
    def test_classify_image_success(self, mock_settings, mock_join, mock_plt, mock_kmeans, mock_imread):
        pass

    def test_ensure_default_classes(self):
        # Should not create duplicates
        utils.ensure_default_classes()
        self.assertEqual(LandUseClass.objects.count(), 4)

class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = AnalysisProject.objects.create(name='Test Project')

    def test_index_view(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context)

    def test_project_list_view(self):
        url = reverse('project_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context)

    def test_project_detail_view(self):
        url = reverse('project_detail', kwargs={'pk': self.project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('project', response.context)
