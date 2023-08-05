# Third party
from django.conf import settings


# define basic SEO settings
SEO_SETTINGS = {
    "content_words_number": [300, 600],
    "internal_links": 1,
    "external_links": 1,
    "meta_title_length": [30, 60],
    "meta_description_length": [50, 160],
    "keywords_in_first_words": 50,
    "max_link_depth": 3,
    "max_url_length": 70,
}

# update SEO settings with values from projectname/settings.py
SEO_SETTINGS.update(getattr(settings, "DJANGO_CHECK_SEO_SETTINGS", {}))


# define auth data (for .htaccess files)
DJANGO_CHECK_SEO_AUTH = {}

DJANGO_CHECK_SEO_AUTH.update(getattr(settings, "DJANGO_CHECK_SEO_AUTH", {}))
