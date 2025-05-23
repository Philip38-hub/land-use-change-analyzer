# LandAnalyzer

LandAnalyzer is a Django web application for analyzing land use changes between two aerial or satellite images. It helps users detect, visualize, and quantify changes in land cover over time, supporting environmental monitoring and planning efforts.

## Features
- Upload and compare two georeferenced images
- Automated detection of land use changes
- Visualization of detected changes
- Change analysis report generation

## Prerequisites
- Python 3.8+
- Django (see requirements.txt)

## Setup Instructions
1. Clone this repository:
   ```bash
   git clone https://github.com/Philip38-hub/landanalyzer.git
   cd landanalyzer
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply Django migrations:
   ```bash
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
1. Open your browser and go to `http://127.0.0.1:8000/`.
2. Upload two georeferenced aerial images (before and after).
3. Start the analysis to view detected land use changes.
4. Download the results if needed.

## Project Structure
- `analyzer/` - Django app with models, views, forms, and utilities
- `manage.py` - Django project management script
- `requirements.txt` - Python dependencies

## Roadmap
- Integrate GDAL for advanced geospatial image processing and raster analysis
- Add Leaflet.js for interactive map visualization of land use changes
- Support for more geospatial data formats
- User authentication and project management
- Automated report generation and export
- API endpoints for programmatic access

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](LICENSE)