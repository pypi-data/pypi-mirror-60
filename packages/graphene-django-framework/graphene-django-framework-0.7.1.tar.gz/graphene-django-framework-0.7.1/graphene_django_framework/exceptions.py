
from django.core.exceptions import PermissionDenied


class GraphenePermissionDenied(PermissionDenied):
    """ The user didn't have the right permission. Keeps track of what that permission was. """

    def __init__(self, message, perm=None, *args, **kwargs):
        super(GraphenePermissionDenied, self).__init__(message, *args, **kwargs)

        self.perm = perm
