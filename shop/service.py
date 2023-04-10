from django.conf import settings


class SiteSettings:

    def __init__(self, request):
        """Инициализация Настроек администратора"""
        self.sessions = request.session
        site_settings = self.sessions.get(settings.ADMIN_SETTINGS_ID)
        if not site_settings:
            site_settings = self.sessions[settings.ADMIN_SETTINGS_ID] = {}
        self.site_settings = site_settings

    def add(self, name, value):
        self.site_settings[name] = value
        self.save()

    def __iter__(self):
        for item in self.site_settings.items():

            yield item

    def save(self):
        self.sessions[settings.ADMIN_SETTINGS_ID] = self.site_settings
        self.sessions.modified = True
