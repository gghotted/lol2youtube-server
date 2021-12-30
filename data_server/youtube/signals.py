from django.db.models.signals import post_save
from django.dispatch import receiver

from youtube.models import UploadInfo


@receiver(post_save, sender=UploadInfo)
def upload_info_post_save(sender, instance, created, **kwargs):
    if not created:
        return
    
    instance.post_backup_data()
