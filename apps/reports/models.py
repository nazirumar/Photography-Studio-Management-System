from django.db import models


# Reports are computed from other models, no separate models needed for V1.
# Add placeholder only.
class ReportConfig(models.Model):
    """Store custom report configurations if needed in the future."""
    pass
