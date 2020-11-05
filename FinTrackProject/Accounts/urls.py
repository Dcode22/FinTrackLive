from django.conf.urls import url
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('signup/', views.signup, name="signup"),
    path('profile/', views.profile, name='profile'),
    path('addbank/', views.addBankAccount, name='add_bank_account'),
    path('addmerchant/', views.addMerchant, name='add_merchant'),
    path('addcreditcard/', views.addCreditCard, name='add_credit_card'),
    path('addincomecat/', views.addIncomeCategory, name='add_income_category'),
    path('addincomesrc/', views.addIncomeSource, name='add_income_source'),
    path('addspendcat/', views.addSpendingCategory, name='add_spending_category'),
    path('addincomingpayment/', views.addIncomingPayment, name='add_incoming_payment'),
    path('addoutgoingpayment/', views.addOutgoingPayment, name='add_outgoing_payment'),
    path('addtrans/', views.addTransfer, name='add_transfer'),
    path('addcredpay/', views.addCreditPayment, name='add_credit_card_payment'),
    path('merchantautocomp/', views.MerchantAutocomplete.as_view(create_field='name'), name='merchant_autocomplete'),
    # path('spdcatautocomp/', views.SpendingCatAutocomplete.as_view(create_field='name'), name='spend_cat_autocomplete'),
    path('inccatautocomp/', views.IncomeCatAutocomplete.as_view(create_field='name'), name='inc_cat_autocomplete'),
    path('incsrcautocomp/', views.IncomeSrcAutocomplete.as_view(create_field='name'), name='inc_src_autocomplete'),
    path('dash/', views.dashboard, name='dashboard'),
]