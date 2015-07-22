from django.http import Http404

from rest_framework import generics, permissions, authentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import *  # noqa
from .serializers import *  # noqa


class NotificationList(generics.ListAPIView):
    """
    Retrieve a list of notifications of the current user.

    **Available variations through querystring parameters:**

     * `action=unread`: default behaviour, retrieve unread notifications and mark them as read
     * `action=unread&read=false`: retrieve unread notifications without marking them as read
     * `action=count`: retrieve count of unread notifications without marking them as read
     * `action=all`: retrieve all notifications with pagination
        * `limit=<n>`: specify number of items per page (defaults to 30)
        * `limit=0`: turns off pagination
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    paginate_by = 30
    paginate_by_param = 'limit'
    serializer_class = NotificationSerializer
    pagination_class = PageNumberPagination
    queryset = Notification.objects.select_related('from_user')

    def get_queryset(self):
        """ filter only notifications of current user """
        return self.queryset.filter(to_user=self.request.user)

    def get(self, request, format=None):
        """ get HTTP method """
        action = request.query_params.get('action', 'unread')
        # action can be only "unread" (default), "count" and "all"
        action = action if action == 'count' or action == 'all' else 'unread'
        # mark as read parameter, defaults to true
        mark_as_read = request.query_params.get('read', 'true') == 'true'
        # queryset
        notifications = self.get_queryset().filter(to_user=request.user)
        # pass to specific action
        return getattr(self, 'get_%s' % action)(request, notifications, mark_as_read)

    def get_unread(self, request, notifications, mark_as_read):
        """
        return unread notifications and mark as read
        (unless read=false param is passed)
        """
        notifications = notifications.filter(is_read=False)
        serializer = UnreadNotificationSerializer(list(notifications),  # evaluate queryset
                                                  many=True,
                                                  context=self.get_serializer_context())
        # retrieve unread notifications as read (default behaviour)
        if mark_as_read:
            notifications.update(is_read=True)
        return Response(serializer.data)

    def get_count(self, request, notifications, mark_as_read=False):
        """ return count of unread notification """
        return Response({'count': notifications.filter(is_read=False).count()})

    def get_all(self, request, notifications, mark_as_read=False):
        """ return all notifications with pagination """
        return self.list(request, notifications)

notification_list = NotificationList.as_view()


class NotificationDetail(generics.RetrieveAPIView):
    """
    Retrieve specific notification of current user.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationSerializer
    queryset = Notification.objects.select_related('from_user')

    def get_queryset(self):
        """ filter only notifications of current user """
        return self.queryset.filter(to_user=self.request.user)

notification_detail = NotificationDetail.as_view()


# ------ User Notification Settings ------ #


class EmailNotificationSettings(generics.RetrieveUpdateAPIView):
    """
    Retrieve Email Notification settings.

    ### PUT & PATCH

    Edit Email Notification settings.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmailNotificationSettingsSerializer
    model = UserEmailNotificationSettings

    def get_queryset(self):
        return self.model.objects.get(user_id=self.request.user.id)

    def get_object(self, queryset=None):
        """ get privacy settings of current user """
        try:
            obj = self.get_queryset()
        except self.model.DoesNotExist:
            raise Http404()
        self.check_object_permissions(self.request, obj)
        return obj

notification_email_settings = EmailNotificationSettings.as_view()


class WebNotificationSettings(EmailNotificationSettings):
    """
    Retrieve Web Notification settings.

    ### PUT & PATCH

    Edit Web Notification settings.
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WebNotificationSettingsSerializer
    model = UserWebNotificationSettings

notification_web_settings = WebNotificationSettings.as_view()
