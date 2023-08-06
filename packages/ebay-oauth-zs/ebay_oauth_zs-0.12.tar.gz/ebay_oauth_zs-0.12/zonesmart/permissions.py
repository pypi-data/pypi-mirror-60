from rest_framework import permissions


class SupportGroupPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="support").exists()


class AnnouncementGroupPermission(permissions.IsAuthenticated):
    """
    Announcement group permissions.
    """

    GROUP_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    def has_permission(self, request, view):
        if (
            request.method in self.GROUP_METHODS
            and request.user.groups.filter(name="announcement").exists()
        ):
            return True
        elif request.method not in self.GROUP_METHODS:
            return True
        else:
            return False
