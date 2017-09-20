# from greeking.lorem


def calaccess_website(request):
    """
    Custom context variables for the CAL-ACCESS downloads website.
    """
    domain = 'calaccess.californiacivicdata.org'

    return {
        'CALACCESS_WEBSITE_TITLE': 'California Civic Data Coalition',
        'CALACCESS_WEBSITE_DESCRIPTION': "An open-source network of journalists and computer programmers from news \
organizations across America.",
        'CALACCESS_WEBSITE_DOMAIN': domain,
        'CALACCESS_WEBSITE_SHARE_IMG': '//{}/static/calaccess_website/images/brown-bear-share.png'.format(domain),
        'FULL_URL': '//{}{}'.format(domain, request.path)
    }
