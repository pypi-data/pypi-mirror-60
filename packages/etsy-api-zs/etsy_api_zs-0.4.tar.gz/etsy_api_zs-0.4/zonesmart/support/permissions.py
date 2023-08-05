from rest_framework import permissions


class SupportGroupPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return True if request.user.groups.filter(name="support").exists() else False
        # return request.user.groups.filter(name='support').exists()
