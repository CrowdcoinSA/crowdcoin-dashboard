from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, loader
from django.conf import settings
from merchant_portal.models import *
from crowdcoin_backends.auth import api_session  
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.template.defaultfilters import urlencode
from payfast.forms import PayFastForm
import requests
import logging
import json
logger = logging.getLogger(__name__)



def custom_404(request):
    context_variables={}
    template = loader.get_template('404.html')
    next = request.META.get('HTTP_REFERER', None) or '/'
    context_variables['next']=next
    context= RequestContext(request,context_variables)
    return HttpResponse(template.render(context))

def custom_500(request):
    context_variables={}
    template = loader.get_template('500.html')
    next = request.META.get('HTTP_REFERER', None) or '/'
    context_variables['next']=next
    context= RequestContext(request,context_variables)
    return HttpResponse(template.render(context))

class OverviewView(LoginRequiredMixin,View):
    template_name = "overview.html"
    
    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        logger.info(profile)
        context['profile'] = profile
        context['transactions'] = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'transactions/?order_by=-datetime&pocket={pocket}'.format(pocket=profile['default_pocket']['id'])).json()['objects']
        request.session['active_side_pane'] = 'Overview'
        return render(request, self.template_name, context)


class MoneyTransferView(LoginRequiredMixin,View):
    template_name = "money-transfer/landing.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)


class BillsView(LoginRequiredMixin,View):
    template_name = "bills/landing.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Payments'
        return render(request, self.template_name, context)


class TicketsView(LoginRequiredMixin,View):
    template_name = "tickets/landing.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Events Tickets'
        return render(request, self.template_name, context)


class AccountView(LoginRequiredMixin,View):
    template_name = "account/landing.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Account'
        return render(request, self.template_name, context)


class BuyTicketView(LoginRequiredMixin,View):
    template_name = "tickets/buy-ticket.html"

    def get(self, request, *args, **kwargs):
        context ={}
        request.session['active_side_pane'] = 'Buy Ticket'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context ={}
        request.session['active_side_pane'] = 'Buy Ticket'
        return render(request, self.template_name, context)


class VerifyTicketView(LoginRequiredMixin,View):
    template_name = "tickets/verify-ticket.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Verify Ticket'
        return render(request, self.template_name, context)


class BuyVoucherView(LoginRequiredMixin,View):
    template_name = "money-transfer/buy-voucher.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        data = {}
        data['pocket_from'] = request.POST.get('pocket_from')
        data['amount'] = request.POST.get('amount')
        # data['recipient_name'] = request.POST.get('recipient_name')
        # data['sender_name'] = request.POST.get('sender_name')
        data['recipient_msisdn'] = request.POST.get('recipient_msisdn','0')
        # data['sender_msisdn'] = request.POST.get('sender_msisdn','0')
        data['status'] = "Awaiting Collection"

        api_response = crowdcoin_api.post(
            settings.CROWDCOIN_API_URL+'voucher_payments/',
            data=data
            )

        try:
            api_response = api_response.json()
            if api_response.get('status'):
                voucher = api_response
                response = "R{amount} Voucher sucessfully sent to {recipient_msisdn}".format(amount=voucher.get('amount'),recipient_msisdn=voucher.get('recipient_msisdn'))
            elif api_response.get('error'):
                response = api_response.get('error')['message']
            else:
                response = "An unknown error occured. Our engineering team has been notified about this."

        except Exception as e:
            response = e.message
            logger.warning(e.message)

        messages.add_message(request, messages.INFO,response)
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)


class RedeemVoucherView(LoginRequiredMixin,View):
    template_name = "money-transfer/redeem-voucher.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile

        api_response = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'voucher_payments/?voucher_code={voucher_code}'.format(voucher_code=request.POST.get('voucher_code'))).json()
        logger.info(api_response)
        if api_response['meta']['total_count'] == 1:
            voucher = api_response['objects'][0]
            if voucher['status'] == 'Awaiting Collection':
                #Update voucher details
                data = {'status':'Collected','pocket_to':request.POST.get('pocket_to')}
                api_response = crowdcoin_api.put(settings.CROWDCOIN_API_URL+'voucher_payments/{voucher_id}/'.format(voucher_id=voucher['id']), data=data)
                response = "Thank you. R{amount} has been credited to your account. Kindly give the customer their goods/cash".format(amount=voucher['amount'])
            else:
                response = "The supplied voucher code has already been redeemed. Do not give goods/cash."
        else:
            response = "The supplied voucher code does not exist. Do not give goods/cash."
        #context['voucher'] = voucher
        messages.add_message(request, messages.INFO,response)
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)


class VerifyVoucherView(LoginRequiredMixin,View):
    template_name = "money-transfer/verify-voucher.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)

class PublicAccountView(LoginRequiredMixin,View):
    template_name = "bills/public-account.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        api_response = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'merchants/')
        logger.info(api_response.json())
        context['merchants'] = api_response.json()['objects']
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Payments'
        return render(request, self.template_name, context)

        
    def post(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        api_response = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'merchants/')
        logger.info(api_response.json())
        context['merchants'] = api_response.json()['objects']
        data=request.POST.copy()
        data['reference'] = "Acc: {account} - Ref: {reference} - Sender: {sender_name} {sender_msisdn}".format(reference=data.get('reference'),
            account=data.get('account_no'),
            sender_name=data.get('sender_name'),
            sender_msisdn=data.get('sender_msisdn')
            )
        api_response = crowdcoin_api.post(settings.CROWDCOIN_API_URL+'crowdcoin_payments/', data=data).json()
        logger.info(api_response)
        if not api_response.get('error') or not api_response.get('error_message'):
            response = "Your payment was successful. Please allow upto 48 hours for the transaction to reflect in the recivieng institution's account."
        else:
            response = api_response.get('error',api_response.get('error_message'))
        messages.add_message(request, messages.INFO,response)
        request.session['active_side_pane'] = 'Payments'
        return render(request, self.template_name, context)



class BankTransferView(LoginRequiredMixin,View):
    template_name = "bills/bank-transfer.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Bank Transfer'
        return render(request, self.template_name, context)


class TransferView(LoginRequiredMixin,View):
    template_name = "account/transfer-funds.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Transfer funds'
        return render(request, self.template_name, context)

class AddFundsView(LoginRequiredMixin,View):
    template_name = "account/add-funds.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        request.session['active_side_pane'] = 'Add funds'
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin,View):
    template_name = "account/profile.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        merchant = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'merchants/?profile={id}'.format(id=profile['id'])).json()
        context['merchant'] = merchant['objects'][0]
        request.session['active_side_pane'] = 'Profile'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #Post form to api
        post_data = request.POST.dict()
        logger.info(post_data)
        crowdcoin_api = api_session(request)
        response = crowdcoin_api.put(settings.CROWDCOIN_API_URL+'merchants/{id}'.format(id=post_data.get('merchant_id')), data=json.dumps(post_data), headers={'Content-type':'application/json'})
        if response.status_code in [200]:
            logger.exception(response.content)
            messages.success(request,"Profile successfully updated.")
        else:
            logger.warning(response.content)
            messages.error(request,"Profile update was not successfull.")
        return redirect('account-profile')


class NotificationView(LoginRequiredMixin,View):
    template_name = "account/notification.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile

        merchant = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'merchants/?profile={id}'.format(id=profile['id'])).json()['objects'][0]
        context['merchant'] = merchant
        logger.info(merchant)        
        request.session['active_side_pane'] = 'Notification'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #Post form to api
        crowdcoin_api = api_session(request)
        post_data = request.POST.dict()
        logger.info(post_data)
        response = crowdcoin_api.put(settings.CROWDCOIN_API_URL+'merchants/{id}'.format(id=post_data.get('merchant_id')), data=json.dumps(post_data), headers={'Content-type':'application/json'})
        if response.status_code in [200]:
            logger.exception(response.content)
            messages.success(request,"Profile successfully updated.")
        else:
            logger.warning(response.content)
            messages.error(request,"Profile update was not successfull.")
        request.session['active_side_pane'] = 'Notification'
        return redirect('account-notification')


class SubscriptionView(LoginRequiredMixin,View):
    template_name = "account/subscription.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile

        merchant = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'merchants/?profile={id}'.format(id=profile['id'])).json()['objects'][0]
        context['merchant'] = merchant
        logger.info(merchant)        
        request.session['active_side_pane'] = 'Subscription'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #Post form to api
        crowdcoin_api = api_session(request)
        post_data = request.POST.dict()
        logger.info(post_data)
        response = crowdcoin_api.put(settings.CROWDCOIN_API_URL+'merchants/{id}'.format(id=post_data.get('merchant_id')), data=json.dumps(post_data), headers={'Content-type':'application/json'})
        if response.status_code in [200]:
            logger.exception(response.content)
            messages.success(request,"Profile successfully updated.")
        else:
            logger.warning(response.content)
            messages.error(request,"Profile update was not successfull.")
        request.session['active_side_pane'] = 'Subscription'
        return redirect('account-notification')


class IntegrationView(LoginRequiredMixin,View):
    template_name = "account/integration.html"

    def get(self, request, *args, **kwargs):
        context ={}
        #context['form'] = ProfileForm
        context['profile'] = UserProfile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Integration'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # generate payment url 
        posted_data = request.POST.copy()
        logger.info(posted_data)
        gen_pay_link = "{crowdcoin_web}process/?pocket_to={pocket_to}&amount={amount}&reference={reference}".format(crowdcoin_web=settings.CROWDCOIN_WEB_URL, pocket_to=posted_data.get('pocket_to'), amount = posted_data.get('amount'), reference =posted_data.get('reference'))
        gen_pay_link = urlencode(gen_pay_link,":/?=&")
        logger.info(gen_pay_link)
        request.session['gen_pay_link'] = gen_pay_link
        return redirect('account-integration')

class SecurityView(LoginRequiredMixin,View):
    template_name = "account/security.html"

    def get(self, request, *args, **kwargs):
        context ={}
        context['form']  = PasswordChangeForm(request.user)
        request.session['active_side_pane'] = 'Security'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context ={}
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
        request.session['active_side_pane'] = 'Security'
        context['form']  = PasswordChangeForm(request.user)
        return render(request, self.template_name, context)


class StatementView(LoginRequiredMixin,View):
    template_name = "account/statement.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        merchant = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'merchants/?profile={id}'.format(id=profile['id'])).json()['objects'][0]
        context['merchant'] = merchant
        transactions = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'transactions/?order_by=-datetime&pocket={pocket}'.format(pocket=merchant['default_pocket']['id'])).json()['objects']

        transaction_list = transactions
        paginator = Paginator(transaction_list, 10) # Show 25 contacts per page
        page = request.GET.get('page')
        try:
            transactions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            transactions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            transactions = paginator.page(paginator.num_pages)
        context['transactions'] = transactions
        request.session['active_side_pane'] = 'Statement'
        return render(request, self.template_name, context)


class VoucherHistoryView(LoginRequiredMixin,View):
    template_name = "money-transfer/history.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        context['vouchers'] = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'voucher_payments/?pocket_from={pocket}&order_by=-created'.format(pocket=profile['default_pocket']['id'])).json()['objects']
        request.session['active_side_pane'] = 'Money Transfer'
        return render(request, self.template_name, context)



class PromotionsView(LoginRequiredMixin,View):
    template_name = "promotions.html"

    def get(self, request, *args, **kwargs):
        context ={}
        crowdcoin_api = api_session(request)
        profile = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'profile/').json()
        context['profile'] = profile
        context['promotion'] = crowdcoin_api.get(settings.CROWDCOIN_API_URL+'promotions/?referrer_id={pocket}'.format(pocket=profile['default_pocket']['id'])).json()['objects'][0]
        request.session['active_side_pane'] = 'Promotions'
        return render(request, self.template_name, context)



class SignupView(View):
    template_name = "registration/signup.html"

    def get(self, request, *args, **kwargs):
        context = {}
        context['active_side_pane']='Sign up'
        if request.user.is_authenticated:
            return redirect('/')
        #context['form'] = ProfileForm
        #context['profile'] = Profile.objects.get(user=request.user)
        request.session['active_side_pane'] = 'Sign up'
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context ={}
        if request.user.is_authenticated:
            return redirect('/')
        data = request.POST
        if data.get('password') == data.get('password_again'):
            crowdcoin_api = api_session(request)
            api_response = requests.post(settings.CROWDCOIN_API_URL+'register_merchant/',data=data).json()
            response = api_response['response']
            request.session['active_side_pane'] = 'Sign up'
            messages.add_message(request, messages.INFO,response)
            if api_response['status'] == 'SUCCESS':
                return redirect('/login')
        else:
            response = 'The passwords you provided do not match, please try again.'
            messages.add_message(request, messages.INFO,response)
        return render(request, self.template_name, context)

class PayFastCancelView(View):
    template_name = "payfast/cancel.html"


    def get(self, request, *args, **kwargs):
        context ={}
        return render(request, self.template_name, context)



class PayFastReturnView(View):
    template_name = "payfast/return.html"


    def get(self, request, *args, **kwargs):
        context ={}
        return render(request, self.template_name, context)


def pay_with_payfast(request,*args, **kwargs):

    # Order model have to be defined by user, it is not a part
    # of django-payfast
    amount = request.POST.get('amount')
    item_name = request.POST.get('product')

    form = PayFastForm(initial={
        # required params:
        'amount':amount,
        'item_name': item_name,
        'return_url' : request.scheme +"://"+ request.get_host()+'/payfast/return/',
        'cancel_url' : request.scheme +"://"+ request.get_host()+'/payfast/cancel/',
        'notify_url' : request.scheme +"://"+ request.get_host()+'/payfast/notify/'
    })

    return render(request, 'payfast/pay.html', {'form': form})    
