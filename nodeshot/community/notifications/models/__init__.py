from nodeshot.core.base.utils import check_dependencies

check_dependencies(
    dependencies='nodeshot.community.profiles',
    module='nodeshot.community.notifications'
)


from .notification import Notification
from .user_settings import UserEmailNotificationSettings, UserWebNotificationSettings


__all__ = ['Notification',
           'UserWebNotificationSettings',
           'UserEmailNotificationSettings']
