from zonesmart.news.models import Announcement
from zonesmart.news.serializers.announcement import AnnouncementSerializer
from zonesmart.permissions import AnnouncementGroupPermission
from zonesmart.views import GenericSerializerModelViewSet


class AnnouncementViewSet(GenericSerializerModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [AnnouncementGroupPermission]
    queryset = Announcement.objects.all()
