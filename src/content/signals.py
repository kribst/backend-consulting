from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Actualite, Service, SiteContent
from .serializers import ActualiteSerializer, ServiceSerializer


def update_site_content_actualites():
	actualites = ActualiteSerializer(Actualite.objects.all(), many=True).data
	SiteContent.objects.update(actualites=list(actualites))


def update_site_content_services():
	services = ServiceSerializer(Service.objects.all(), many=True).data
	SiteContent.objects.update(services=list(services))


@receiver(post_save, sender=Actualite)
@receiver(post_delete, sender=Actualite)
def sync_site_content_actualites(sender, **kwargs):
	update_site_content_actualites()


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def sync_site_content_services(sender, **kwargs):
	update_site_content_services()
