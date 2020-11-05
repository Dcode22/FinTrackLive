from django import forms
from .models import Profile
from Main.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from dal import autocomplete


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name', 'last_name')


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

class AddBankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount 
        fields = ('name', 'currency',)
    
class AddCreditCardForm(forms.ModelForm):
    class Meta: 
        model = CreditCard
        fields = ('name', 'spending_limit', 'due_day')


class AddIncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory 
        fields = ('name',)


class AddIncomeSourceForm(forms.ModelForm):
    class Meta: 
        model = IncomeSource
        fields = ('name',)


class AddIncomingPaymentForm(forms.ModelForm):
    class Meta: 
        model = IncomingPayment
        fields = ('description', 'amount', 'income_source', 'income_category', 'bank_account')
        widgets = {
            'income_category': autocomplete.ModelSelect2(url='inc_cat_autocomplete'),
            'income_source': autocomplete.ModelSelect2(url='inc_src_autocomplete')
        }


class AddSpendCategoryForm(forms.ModelForm):
    class Meta: 
        model = SpendCategory
        fields = ('name', 'monthly_budget')


class AddMerchantForm(forms.ModelForm):
    class Meta: 
        model = Merchant 
        fields = ('name',)
    

class AddOutgoingPaymentForm(forms.ModelForm):
    class Meta: 
        model = OutgoingPayment
        fields = ('description', 'amount', 'spend_category', 'merchant', 'bank_account', 'credit_card')
        widgets = {
            # 'spend_category': autocomplete.ModelSelect2(url='spend_cat_autocomplete'),
            'merchant': autocomplete.ModelSelect2(url='merchant_autocomplete')
        }




class AddNewBankBalanceForm(forms.ModelForm):
    class Meta:
        model = IncomingPayment
        fields = ('amount',)
        labels = {
            'amount':'Current Balance',
        }

class AddNewCreditBalanceForm(forms.ModelForm):
    class Meta:
        model = OutgoingPayment
        fields = ('amount',)
        labels = {
            'amount':'Current Balance Due',
        }
    
class AddTransferForm(forms.ModelForm):
    class Meta:
        model = AccountTransfer
        fields = ('amount', 'bank_account_from', 'bank_account_to', 'extra_fee', 'description' )
        labels = {
            'amount':'Amount Deposited',
            'extra_fee':'Extra Fees charged from sending account'
        }
    
class AddCreditCardPaymentForm(forms.ModelForm):
    class Meta:
        model = CreditCardPayment
        fields = ('amount', 'bank_account_from', 'credit_card_to', 'extra_fee', 'rewards_discounts', 'description' )
        labels = {
            'amount':'Amount paid from bank',
            'extra_fee':'Extra Fees charged from sending account',
            'rewards_discounts': 'Extra credit paid off through rewards etc.'
        }
    