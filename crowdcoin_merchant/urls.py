"""crowdcoin_merchant URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from merchant_portal.views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views import static
from django.conf import settings

handler404='merchant_portal.views.custom_404'
handler500='merchant_portal.views.custom_500'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hijack/', include('hijack.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html','active_side_pane':'Sign in'}),
    url(r'^logout/$', auth_views.logout),
    url(r'^signup/$', SignupView.as_view(), name='signup'),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^money-transfer/buy-voucher/$', BuyVoucherView.as_view(), name='money-transfer-buy-voucher'),
    url(r'^money-transfer/redeem-voucher/$', RedeemVoucherView.as_view(), name='money-transfer-redeem-voucher'),
    url(r'^money-transfer/verify-voucher/$', VerifyVoucherView.as_view(), name='money-transfer-verify-voucher'),
    url(r'^money-transfer/voucher-history/$', VoucherHistoryView.as_view(), name='money-transfer-voucher-history'),
    url(r'^money-transfer/$', MoneyTransferView.as_view(), name='money-transfer'),
    url(r'^bills/public-account/$', PublicAccountView.as_view(), name='bills-public-account'),
    url(r'^bills/bank-transfer/$', BankTransferView.as_view(), name='bills-bank-transfer'),
    url(r'^bills/$', BillsView.as_view(), name='bills'),
    url(r'^tickets/buy-ticket/$', BuyTicketView.as_view(), name='tickets-buy-ticket'),
    url(r'^tickets/verify-ticket/$', VerifyTicketView.as_view(), name='tickets-verify-ticket'),
    url(r'^tickets/$', TicketsView.as_view(), name='tickets'),
    url(r'^account/add-funds/$', AddFundsView.as_view(), name='account-add-funds'),
    url(r'^account/statement/$', StatementView.as_view(), name='account-statement'),
    url(r'^account/transfer/$', TransferView.as_view(), name='account-transfer'),
    url(r'^account/profile/$', ProfileView.as_view(), name='account-profile'),
    url(r'^account/integration/$', IntegrationView.as_view(), name='account-integration'),
    url(r'^account/security/$', SecurityView.as_view(), name='account-security'),
    url(r'^account/notification/$', NotificationView.as_view(), name='account-notification'),
     url(r'^account/subscription/$', SubscriptionView.as_view(), name='account-subscription'),
    url(r'^account/$', AccountView.as_view(), name='account'),
    url(r'^promotions/$', PromotionsView.as_view(), name='promotions'),
    url(r'^payfast/', include('payfast.urls')),
    url(r'^pay/redirect', pay_with_payfast, name='pay_with_payfast'),    
    url(r'^$', OverviewView.as_view(), name='overview'),
]+ staticfiles_urlpatterns()