# from greeking.lorem


def calaccess_website(request):
    """
    Custom context variables for the CAL-ACCESS downloads website.
    """
    return {
        'CALACCESS_WEBSITE_TITLE': 'California Civic Data Coalition',
        'CALACCESS_WEBSITE_DESCRIPTION': "An open-source team of journalists \
and computer programmers from news organizations across America.",
        'CALACCESS_WEBSITE_DOMAIN': 'calaccess.californiacivicdata.org',
        'CALACCESS_WEBSITE_SHARE_IMG': '//calaccess.californiacivicdata.org/static/calaccess_website/images/brown-bear-share.png'
    }
