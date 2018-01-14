from django import template
from django.conf import settings
from crowdcoin_backends.auth import api_session  
import logging

logger = logging.getLogger(__name__)

def get_merchant(request):
	try:
		user = request.user
		merchant = api_session(request).get(settings.CROWDCOIN_API_URL+'merchants/?profile__user__username={username}'.format(username=user.username)).json()
		output = {"merchant":merchant['objects'][0]}
	except Exception as e:
		logger.exception(e)
		output = []
	return output
	
def global_config(request):
	output = {"settings":settings}
	return output
	