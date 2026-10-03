"""
Website Processing Module
Bevat de website-configuratie en helper-logica.
"""


class WebsiteProcessor:
    """Website processor met configuratie-ondersteuning"""

    def __init__(self, config=None):
        self.config = config

    def get_options(self):
        """Geef alle website-opties terug uit config"""
        if self.config:
            return self.config.get_website_options()
        # Fallback als geen config beschikbaar
        return [
            ("Website 1", "website1"),
            ("Website 2", "website2"),
            ("Test Website", "test_website"),
        ]

    def get_label(self, value):
        """Geef het label voor een website-waarde terug"""
        if self.config:
            return self.config.get_website_name(value)
        # Fallback labels
        labels = {
            "website1": "Website 1",
            "website2": "Website 2",
            "test_website": "Test Website",
        }
        return labels.get(value, value)

    def get_url(self, website_id):
        """Geef de URL van een website terug"""
        if self.config:
            return self.config.get_website_url(website_id)
        return ""

    def is_test_website(self, value):
        """Controleer of de gegeven waarde een test-website is"""
        if self.config:
            return self.config.is_test_website(value)
        return value == "test_website"
