from django.conf import settings
from django.contrib.auth.hashers import check_password,make_password
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend,RemoteUserBackend
import logging
import requests
from merchant_portal.models import UserProfile
logger = logging.getLogger(__name__)

logger.info("Debugging")

class RemoteBackend(ModelBackend):
	logger.info("Remote")
	request = requests.Session()
	#headers = {'Authorization':settings.CROWDCOIN_API_KEY}
	#request.headers = headers
	def authenticate(self, username=None, password=None, **kwargs):
		logger.info("Called authentication")
		try:
			# 
			response = self.request.get(settings.CROWDCOIN_API_URL+'users/', auth=(username,password))
			response_user = response.json()['objects'][0]
			logger.info(response_user)
			try:
				user = User.objects.get(username=response_user['username'])
			except User.DoesNotExist:
				# Create a new user. There's no need to set a password
				# because only the password from settings.py is checked.
				user = User(username=response_user['username'])
			user.first_name = response_user['first_name']
			user.last_name = response_user['last_name']
			user.email = response_user['email']
			user.is_staff = response_user['is_staff']
			user.is_superuser = response_user['is_superuser']
			user.save()

			profile = UserProfile.objects.get(user=user)
			profile.api_key=response_user.get('key')
			profile.save()
			return user
		except Exception as e:
			logger.error(e.message)
		return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None

def api_session(request):
	try:
		api_session = requests.Session()
		api_session.headers = {'Authorization':'ApiKey {username}:{api_key}'.format(username=request.user.username,api_key=UserProfile.objects.get(user=request.user).api_key)}
		logger.debug(api_session.headers)
		return api_session
	except Exception as e:
		return None
