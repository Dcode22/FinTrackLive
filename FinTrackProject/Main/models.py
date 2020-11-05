from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import *; from dateutil.relativedelta import *
from Accounts.models import Profile, budget_spent_plot
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money



# Create your models here.
class Currency(models.Model):
    name = models.CharField(max_length=3)
    long_name = models.CharField(max_length=50)
    # value??
    profile_favorites = models.ManyToManyField(Profile)
    # profile_primary = models.ManyToOneRel(Profile)
    def __str__(self):
        return f"{self.name} - ({self.long_name})"


class BankAccount(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=100)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    # balance = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency='USD')
    def __str__(self):
        return f"{self.name}"

    @property
    def balance(self):
        if self.currency.name == 'USD':
            balance = Money(0, 'USD')
            for incpayment in self.incoming_payments.all():
                balance += incpayment.amount_dollars
            for outpayment in self.outgoing_payments.all():
                balance -= outpayment.amount_dollars
            for outgoing_transfer in self.outgoing_transfers.all():
                balance -= outgoing_transfer.amount_dollars
                balance -= outgoing_transfer.extra_fee_dollars
            for incoming_transfer in self.incoming_transfers.all():
                balance += incoming_transfer.amount_dollars
            for credpay in self.credit_card_payments.all():
                balance -= credpay.amount_dollars
                balance -= credpay.extra_fee_dollars
            
        elif self.currency.name == 'ILS':
            balance = Money(0, 'ILS')
            for incpayment in self.incoming_payments.all():
                balance += incpayment.amount_shekels
            for outpayment in self.outgoing_payments.all():
                balance -= outpayment.amount_shekels 
            for outgoing_transfer in self.outgoing_transfers.all():
                balance -= outgoing_transfer.amount_shekels
                balance -= outgoing_transfer.extra_fee_shekels
            for incoming_transfer in self.incoming_transfers.all():
                balance += incoming_transfer.amount_shekels
            for credpay in self.credit_card_payments.all():
                balance -= credpay.amount_shekels
                balance -= credpay.extra_fee_shekels
                    
        return balance
        


class CreditCard(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='credit_cards')
    name = models.CharField(max_length=50)
    # balance_due = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency='USD')
    spending_limit = MoneyField(max_digits=10, decimal_places=2, null=True, default_currency='USD')
    due_day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(28)])
    def __str__(self):
        return f"{self.name}"

    @property
    def month_charges(self, date=datetime.now().date()):
        due_date = date
        if date.day >= self.due_day:
            due_date = date + relativedelta(months=+1)
            
        due_date = due_date.replace(day=self.due_day)
        last_due_date = due_date + relativedelta(months=-1)
        results = self.outgoing_payments.filter(date_time__lt=due_date, date_time__gt=last_due_date)
        return results
   
    @property
    def balance_due(self, date=datetime.now().date()):
        due_date = date
        if date.day >= self.due_day:
            due_date = date + relativedelta(months=+1)
            
        due_date = due_date.replace(day=self.due_day)
        last_due_date = due_date + relativedelta(months=-1)
        if self.spending_limit_currency == 'USD':
            balance_due = Money(0, 'USD')
            for outgoing_payment in self.month_charges:
                balance_due += outgoing_payment.amount_dollars
            for creditpayment in self.credit_card_payments.filter(date_time__lt=due_date, date_time__gt=last_due_date):
                balance_due -= creditpayment.amount_dollars
                balance_due -= creditpayment.rewards_discounts_dollars
            return balance_due

        elif self.spending_limit_currency == 'ILS':
            balance_due = Money(0,'ILS')
            for outgoing_payment in self.month_charges:
                balance_due += outgoing_payment.amount_shekels
            for creditpayment in self.credit_card_payments.filter(date_time__lt=due_date, date_time__gt=last_due_date):
                balance_due -= creditpayment.amount_shekels
                balance_due -= creditpayment.rewards_discounts_shekels
            return balance_due 
        
    @property
    def credit_utilization(self):
        if self.spending_limit in [Money(0, 'USD'), Money(0, 'ILS')] :
            percentage = 0
        else:
            percentage = self.balance_due/self.spending_limit*100

        return round(percentage, 2)
            
    

class IncomeCategory(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, related_name='income_categories', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f"{self.name}"


class IncomeSource(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='income_sources')
    name = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"



class Payment(models.Model):
    
    description =  models.CharField(max_length=200, null=True)
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    amount_dollars = MoneyField(max_digits=10, decimal_places=2, default_currency='USD', blank=True, null=True)
    amount_shekels = MoneyField(max_digits=10, decimal_places=2, default_currency='ILS', blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=False, default=datetime.now())
    class Meta:
        abstract = True 


class IncomingPayment(Payment):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='incoming_payments')
    income_source = models.ForeignKey(IncomeSource, on_delete=models.PROTECT, related_name='incoming_payments', null=True, blank=True)
   
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='incoming_payments')
    income_category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, related_name='incoming_payments')
    def save(self, *args, **kwargs):
        self.amount_dollars = convert_money(self.amount, 'USD')
        self.amount_shekels = convert_money(self.amount, 'ILS')
        super(IncomingPayment,self).save(*args, **kwargs)
# class Recurrence(models.Model):
#     incoming_payment = models.OneToOneField(Payment, on_delete=models.PROTECT)
#     is_active = models.BooleanField(default=True)


class SpendCategory(models.Model):
    name = models.CharField(max_length=50)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='spending_categories')
    monthly_budget = MoneyField(max_digits=10, decimal_places=2, null=True, blank=True, default_currency='USD')
    monthly_budget_usd = MoneyField(max_digits=10, decimal_places=2, default_currency='USD', blank=True, null=True)
    monthly_budget_ils = MoneyField(max_digits=10, decimal_places=2, default_currency='ILS', blank=True, null=True)
    def __str__(self):
        return self.name
   
    def month_total_dollars(self, date=datetime.now()):
        total = Money(0, 'USD')
        for payment in self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year):
            total += payment.amount_dollars 

        return total    

    def month_total_shekels(self, date=datetime.now()):
        total = Money(0, 'ILS')
        for payment in self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year):
            total += payment.amount_shekels 

        return total    

    def save(self, *args, **kwargs):
        self.monthly_budget_usd = convert_money(self.monthly_budget, 'USD')
        self.monthly_budget_ils = convert_money(self.monthly_budget, 'ILS')
        super(SpendCategory,self).save(*args, **kwargs)

    def create_plot(self):
        if self.monthly_budget_currency == 'USD':
            month_total = self.month_total_dollars().amount
        elif self.monthly_budget_currency == 'ILS':
            month_total = self.month_total_shekels().amount

        return budget_spent_plot(month_total, self.monthly_budget.amount)
  

class Merchant(models.Model):
    name = models.CharField(max_length=100)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='merchants', null=True, blank=True)
    # spend_category = models.ForeignKey(SpendCategory, on_delete=models.PROTECT, related_name='merchants', null=True, blank=True)
    def __str__(self):
        return self.name

    def month_total_dollars(self, date=datetime.now()):
        total = Money(0, 'USD')
        for payment in self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year):
            total += payment.amount_dollars 

        return total    

    def month_total_shekels(self, date=datetime.now()):
        total = Money(0, 'ILS')
        for payment in self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year):
            total += payment.amount_shekels 

        return total    


class OutgoingPayment(Payment):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='outgoing_payments')
    credit_card = models.ForeignKey(CreditCard, on_delete=models.PROTECT, null=True, blank=True, related_name='outgoing_payments')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, null=True, blank=True, related_name='outgoing_payments')
    spend_category = models.ForeignKey(SpendCategory, on_delete=models.PROTECT, related_name='outgoing_payments', null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.PROTECT, null=True, blank=True, related_name='outgoing_payments')
    def save(self, *args, **kwargs):
        self.amount_dollars = convert_money(self.amount, 'USD')
        self.amount_shekels = convert_money(self.amount, 'ILS')
        super(OutgoingPayment,self).save(*args, **kwargs)


class Transfer(models.Model):
    date_time = models.DateTimeField(auto_now_add=False, default=datetime.now())
    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    amount_dollars = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    amount_shekels = MoneyField(max_digits=10, decimal_places=2, default_currency='ILS')
    extra_fee = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    extra_fee_dollars = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    extra_fee_shekels = MoneyField(max_digits=10, decimal_places=2, default_currency='ILS')
    description = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        self.amount_dollars = convert_money(self.amount, 'USD')
        self.amount_shekels = convert_money(self.amount, 'ILS')
        self.extra_fee_dollars = convert_money(self.extra_fee, 'USD')
        self.extra_fee_shekels = convert_money(self.extra_fee, 'ILS')
        super(Transfer,self).save(*args, **kwargs)

    class Meta:
        abstract = True 

class CreditCardPayment(Transfer):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='credit_card_payments')
    bank_account_from = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='credit_card_payments')
    credit_card_to = models.ForeignKey(CreditCard, on_delete=models.PROTECT, related_name='credit_card_payments')
    rewards_discounts = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    rewards_discounts_dollars = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    rewards_discounts_shekels = MoneyField(max_digits=10, decimal_places=2, default_currency='ILS')
    def save(self, *args, **kwargs):
        self.rewards_discounts_dollars = convert_money(self.rewards_discounts, 'USD')
        self.rewards_discounts_shekels = convert_money(self.rewards_discounts, 'ILS')
        super(CreditCardPayment,self).save(*args, **kwargs)

class AccountTransfer(Transfer):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='account_transfers')
    bank_account_from = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='outgoing_transfers')   
    bank_account_to = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='incoming_transfers')
    