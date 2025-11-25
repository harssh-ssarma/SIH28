# Create Migration for Timetable Configuration

Run these commands:

```bash
cd d:\GitHub\SIH28\backend\django

# Create migration
python manage.py makemigrations academics

# Apply migration
python manage.py migrate academics

# Register in admin (add to academics/admin.py):
from .timetable_config_models import TimetableConfiguration
admin.site.register(TimetableConfiguration)

# Add to academics/__init__.py:
from .timetable_config_models import TimetableConfiguration

# Add URL to academics/urls.py:
from .timetable_config_views import TimetableConfigurationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'timetable-configs', TimetableConfigurationViewSet, basename='timetable-config')

urlpatterns += router.urls
```

## API Endpoints Created:

- `GET /api/academics/timetable-configs/` - List all configs
- `GET /api/academics/timetable-configs/last-used/` - Get last used config
- `POST /api/academics/timetable-configs/` - Create new config
- `PUT /api/academics/timetable-configs/{id}/` - Update config
- `POST /api/academics/timetable-configs/save-and-generate/` - Save & generate
