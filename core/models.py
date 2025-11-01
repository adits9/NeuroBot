from django.db import models


class EEGRecord(models.Model):
    """Stores processed EEG features and metadata."""
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw_data_s3 = models.URLField(blank=True, null=True)
    features = models.JSONField(null=True, blank=True)
    mood_inference = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f'EEGRecord {self.id} at {self.uploaded_at.isoformat()}'
