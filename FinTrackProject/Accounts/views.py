from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from datetime import datetime
from .forms import *
from .models import Profile
from Main.models import *
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money
import plotly.graph_objects as go
from plotly.offline import plot

# Create your views here.


def signup(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, "Profile successfully created")
            return redirect('home')
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        return render(request, 'registration/signup.html', {'form': form})



def profile(request):
    if request.method == 'POST':
        form1 = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        form2 = EditUserForm(data=request.POST, instance=request.user)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
            return redirect('profile')
    else:
        form1 = EditProfileForm(instance=request.user.profile)
        form2 = EditUserForm(instance=request.user)

   
    labels1 = []
    values1 = []
    for category in request.user.profile.spending_categories.all():
        if category.month_total_dollars() > Money(0, 'USD'):
            labels1.append(category.name)
            values1.append(category.month_total_dollars().amount)
        
    # Use `hole` to create a donut-like pie chart
    fig1 = go.Figure(data=[go.Pie(labels=labels1, values=values1, hole=.6, title="This Month's Spending (USD)")],)      
    fig1.update_layout(
        barmode='stack',
        margin=go.layout.Margin(
                l=60, #left margin
                r=20, #right margin
                b=20, #bottom margin
                t=20  #top margin
            )
        )
    
    plt_div1 = plot(fig1, output_type='div', include_plotlyjs=False)
    
    labels2 = []
    values2 = []
    for merchant in request.user.profile.merchants.all():
        if merchant.month_total_dollars() > Money(0, 'USD'):
            labels2.append(merchant.name)
            values2.append(merchant.month_total_dollars().amount)
        
    # Use `hole` to create a donut-like pie chart
    fig2 = go.Figure(data=[go.Pie(labels=labels2, values=values2, hole=.6, title="This Month's Spending (USD)")])      
    plt_div2 = plot(fig2, output_type='div', include_plotlyjs=False)
      
    content = {
        'form1': form1, 
        'form2': form2, 
        'plt_div1': plt_div1,
        'plt_div2': plt_div2
        
        }
    return render(request, 'profile.html', content)




def addBankAccount(request):
    if request.method == 'POST':
        form1 = AddBankAccountForm(request.POST)
        form2 = AddNewBankBalanceForm(request.POST)
        if form1.is_valid():
            new_bank = form1.save(commit=False)
            new_bank.profile = request.user.profile
            new_bank.save()
            messages.success(request, "Bank Account Added")

        if form2.is_valid():
            new_inc_payment = form2.save(commit=False)
            new_inc_payment.profile = request.user.profile
            new_inc_payment.description = "Starting bank account balance"
            new_inc_payment.date_time = datetime.now() 
            new_inc_payment.income_source = IncomeSource.objects.get_or_create(name='Starting Balance', profile=request.user.profile)[0]
            new_inc_payment.income_category = IncomeCategory.objects.get_or_create(name='Miscellaneous', profile=request.user.profile)[0]
            new_inc_payment.bank_account = new_bank
            new_inc_payment.save()
            
            return redirect('profile')

    else:
        form1 = AddBankAccountForm()
        form2 = AddNewBankBalanceForm()
        return render(request, 'add_2_forms.html', {'form1': form1, 'form2': form2, 'title':'Bank Account'})



def EditBank(request):
    form = AddBankAccountForm(data=request.POST, instance=request.user)
    if request.method =='POST':
        form = AddBankAccountForm()



def addCreditCard(request):
    form1 = AddCreditCardForm()
    form2 = AddNewCreditBalanceForm()
    if request.method == 'POST':
        form1 = AddCreditCardForm(request.POST)
        form2 = AddNewCreditBalanceForm(request.POST)
        if form1.is_valid():
            new_card = form1.save(commit=False)
            new_card.profile = request.user.profile
            new_card.save()
            messages.success(request, "Credit Card Added")

        if form2.is_valid():
            new_out_payment = form2.save(commit=False)
            new_out_payment.profile = request.user.profile
            new_out_payment.description = "starting credit card balance due"
            new_out_payment.date_time = datetime.now() 
            new_out_payment.credit_card = new_card
            new_out_payment.save()    
            
            return redirect('profile')

    else:
        
        return render(request, 'add_2_forms.html', {'form1': form1, 'form2': form2, 'title':'Credit Card'})


def addIncomeCategory(request):
    form = AddIncomeCategoryForm()
    if request.method == 'POST':
        form = AddIncomeCategoryForm(request.POST)
        if form.is_valid():
            new_income_category = form.save(commit=False)
            new_income_category.profile = request.user.profile
            new_income_category.save()
            messages.success(request, "Income Category Added")
            return redirect('profile')
        
    else:
        
        return render(request, 'add_form.html', {'form': form, 'title': 'Income Category'})

def addIncomeSource(request):
    form = AddIncomeSourceForm()
    if request.method == 'POST':
        form = AddIncomeSourceForm(request.POST)
        if form.is_valid():
            new_income_source = form.save(commit=False)
            new_income_source.profile = request.user.profile
            new_income_source.save()
            messages.success(request, "Income Source Added")
            return redirect('profile')
        
    else:
        
        return render(request, 'add_form.html', {'form': form, 'title': 'Income Source'})



def addSpendingCategory(request):
    form = AddSpendCategoryForm()
    if request.method == 'POST':
        form = AddSpendCategoryForm(request.POST)
        if form.is_valid():
            new_spending_category = form.save(commit=False)
            new_spending_category.profile = request.user.profile
            new_spending_category.save()
            messages.success(request, "Spending category added")
            return redirect('profile')
       
    else:
        return render(request, 'add_form.html', {'form': form, 'title': 'Spending Category'})




def addMerchant(request):
    form = AddMerchantForm()
    if request.method == 'POST':
        form = AddMerchantForm(request.POST)
        if form.is_valid():
            new_merchant = form.save(commit=False)
            new_merchant.profile = request.user.profile
            new_merchant.save()
            messages.success(request, "Merchant Added")
            return redirect('profile')
       
    else:
        return render(request, 'add_form.html', {'form': form, 'title': 'Merchant'})


def addIncomingPayment(request):
    form = AddIncomingPaymentForm()
    form.fields['bank_account'].queryset = BankAccount.objects.filter(profile=request.user.profile)
    if request.method == 'POST':
        form = AddIncomingPaymentForm(request.POST)
        if form.is_valid():
            new_inc_pmnt = form.save(commit=False)
            new_inc_pmnt.profile = request.user.profile
            new_inc_pmnt.save()
            messages.success(request, "Incoming Payment Added")
            return redirect('profile')
       
    else:
        return render(request, 'add_form.html', {'form': form, 'title': 'Incoming Payment'})


def addOutgoingPayment(request):
    form = AddOutgoingPaymentForm()
    form.fields['spend_category'].queryset = request.user.profile.spending_categories.all()
    form.fields['bank_account'].queryset = request.user.profile.bank_accounts.all()
    form.fields['credit_card'].queryset = request.user.profile.credit_cards.all()
    
    if request.method == 'POST':
        form = AddOutgoingPaymentForm(request.POST)
        if form.is_valid():
            new_out_pmnt = form.save(commit=False)
            new_out_pmnt.profile = request.user.profile
            new_out_pmnt.save()
            messages.success(request, "Outgoing Payment Added")
            return redirect('profile')
       
    else:
        return render(request, 'add_form.html', {'form': form, 'title': 'Outgoing Payment'})



        






def addTransfer(request):
    form = AddTransferForm()
    form.fields['bank_account_from'].queryset = BankAccount.objects.filter(profile=request.user.profile)
    form.fields['bank_account_to'].queryset = BankAccount.objects.filter(profile=request.user.profile)
    if request.method == 'POST':
        form = AddTransferForm(request.POST)
        if form.is_valid():
            new_transfer = form.save(commit=False)
            new_transfer.profile = request.user.profile
            new_transfer.save()
            messages.success(request, "Transfer Added")
            return redirect('profile')
       
    else:
        return render(request, 'add_form.html', {'form': form, 'title': 'Transfer'})


def addCreditPayment(request):
    form = AddCreditCardPaymentForm()
    form.fields['bank_account_from'].queryset = BankAccount.objects.filter(profile=request.user.profile)
    form.fields['credit_card_to'].queryset = CreditCard.objects.filter(profile=request.user.profile)
    if request.method == 'POST':
        form = AddCreditCardPaymentForm(request.POST)
        if form.is_valid():
            new_crd_pymnt = form.save(commit=False)
            new_crd_pymnt .profile = request.user.profile
            new_crd_pymnt .save()
            messages.success(request, "Credit card payment saved")
            return redirect('profile')
       
    else:
        return render(request, 'add_form.html', {'form': form, 'title': 'Credit Card Payment'})


class MerchantAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Merchant.objects.filter(profile=self.request.user.profile)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
    
    def create_object(self, text):
        return self.get_queryset().get_or_create(**{self.create_field:text, 'profile': self.request.user.profile})[0]


# class SpendingCatAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         qs = SpendCategory.objects.filter(profile=self.request.user.profile)
#         if self.q:
#             qs = qs.filter(name__icontains=self.q)
#         return qs
    
#     def create_object(self, text):
#         return self.get_queryset().get_or_create(**{self.create_field:text, 'profile': self.request.user.profile})[0]
    

class IncomeCatAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = IncomeCategory.objects.filter(profile=self.request.user.profile)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
    
    def create_object(self, text):
        return self.get_queryset().get_or_create(**{self.create_field:text, 'profile': self.request.user.profile})[0]

class IncomeSrcAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = IncomeSource.objects.filter(profile=self.request.user.profile)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
    
    def create_object(self, text):
        return self.get_queryset().get_or_create(**{self.create_field:text, 'profile': self.request.user.profile})[0]

    
def dashboard(request):
    



    return render(request, 'dashboard.html')
    