from django.db import models
from django.contrib.auth.models import User, Permission
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import *
from django.db.models import Sum
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money
import plotly.graph_objects as go
from plotly.offline import plot




def budget_spent_plot(month_total, monthly_budget):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=['Spent'],
        x=[month_total],
        name='Spent so far this month',
        orientation='h',
        marker=dict(
            color='rgba(157, 211, 49, 0.5)',
            line=dict(color='rgba(157, 211, 49, 1.0)', width=3)
        )
    ))
    fig.add_trace(go.Bar(
        y=['Budget'],
        x=[monthly_budget],
        name='Monthly Budget',
        orientation='h',
        marker=dict(
            color='rgba(58, 71, 80, 0.6)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
        )
    ))

        
    
    fig.update_layout(
        autosize=False,
        height=100,
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',

        font={
            'color':'rgb(157, 211, 49)'
        },
        margin=go.layout.Margin(
                l=60, #left margin
                r=20, #right margin
                b=20, #bottom margin
                t=20  #top margin
            )
        )


    return plot(fig, output_type='div', include_plotlyjs=False)

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="profile_pics/avatar.png", upload_to="profile_pics")
    def __str__(self):
        return f"{self.user.get_full_name()}"

    
    def month_outgoing_payments(self, date=datetime.now()):
        return self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year)
         
    
    def month_spending_usd(self, date=datetime.now()):
        month_out_payments = self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year)
        total_month_out_usd = Money(0, 'USD')
        for payment in month_out_payments:
            total_month_out_usd += payment.amount_dollars
        
        return total_month_out_usd
    
    def month_spending_ils(self, date=datetime.now()):
        month_out_payments = self.outgoing_payments.filter(date_time__month=date.month, date_time__year=date.year)
        total_month_out_ils = Money(0, 'ILS')
        for payment in month_out_payments:
            total_month_out_ils += payment.amount_shekels
        
        return total_month_out_ils

    def month_total_budget_usd(self):
        budget_usd = Money(0, 'USD')
        for category in self.spending_categories.all():
            
            budget_usd += category.monthly_budget_usd
        
        return budget_usd
    
    def month_total_budget_ils(self):
        budget_ils = Money(0, 'ILS')
        for category in self.spending_categories.all():
            budget_ils += category.monthly_budget_ils
        return budget_ils


    def budget_spent_as_plot(self):
        return budget_spent_plot(self.month_spending_usd().amount, self.month_total_budget_usd().amount)

    
    def total_bank_dollars(self):
        total = Money(0, 'USD')
        for account in self.bank_accounts.all():
            if account.currency.name != 'USD':
                converted = convert_money(account.balance, 'USD')
                total += converted
            
            else:
                total += account.balance
        
        return total 
        

    def total_bank_shekels(self): 
        total = Money(0, 'ILS')
        for account in self.bank_accounts.all():
            if account.currency.name != 'ILS':
                converted = convert_money(account.balance, 'ILS')
                total += converted
            
            else:
                total += account.balance
        
        return total

    @property
    def total_due_dollars(self):
        total = Money(0, 'USD')
    
        for card in self.credit_cards.all():
            if card.spending_limit_currency != 'USD':
                converted = convert_money(card.balance_due, 'USD')
                total += converted
            
            else:
                total += card.balance_due
        return total
    
    def total_due_shekels(self):
        total = Money(0, 'ILS')
        for card in self.credit_cards.all():
            if card.spending_limit_currency != 'ILS':
                converted = convert_money(card.balance_due, 'ILS')
                total += converted
            
            else:
                total += card.balance_due
            
        return total
    
    @property
    def total_limit_dollars(self):
        total = Money(0, 'USD')
    
        for card in self.credit_cards.all():
            if card.spending_limit_currency != 'USD':
                converted = convert_money(card.spending_limit, 'USD')
                total += converted
            
            else:
                total += card.spending_limit
        return total
    

    def total_limit_shekels(self):
        total = Money(0, 'ILS')
        for card in self.credit_cards.all():
            if card.spending_limit_currency != 'ILS':
                converted = convert_money(card.spending_limit, 'ILS')
                total += converted
            
            else:
                total += card.spending_limit
        return total
    
    def total_utilization(self):
        if self.total_limit_dollars > Money(0, 'USD'):
            return round(self.total_due_dollars/self.total_limit_dollars*100, 2)
        else:
            pass 

    def spend_cat_pie(self):
        labels1 = []
        values1 = []
        for category in self.spending_categories.all():
            if category.month_total_dollars() > Money(0, 'USD'):
                labels1.append(category.name)
                values1.append(category.month_total_dollars().amount)
            
        # Use `hole` to create a donut-like pie chart
        fig1 = go.Figure(data=[go.Pie(labels=labels1, values=values1, hole=.6, title="Month's Spending by Category(USD)")],)      
        fig1.update_layout(
          
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=go.layout.Margin(
                    l=0, #left margin
                    r=0, #right margin
                    b=50, #bottom margin
                    t=0  #top margin
                ),

            font={
            'color':'rgb(157, 211, 49)'
            },
            )
        
        return plot(fig1, output_type='div', include_plotlyjs=False)
    
    
    def spend_merchant_pie(self):

        labels2 = []
        values2 = []
        for merchant in self.merchants.all():
            if merchant.month_total_dollars() > Money(0, 'USD'):
                labels2.append(merchant.name)
                values2.append(merchant.month_total_dollars().amount)
            
        # Use `hole` to create a donut-like pie chart
        fig2 = go.Figure(data=[go.Pie(labels=labels2, values=values2, hole=.6, title="Month's Spending by Merchant (USD)")])      
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=go.layout.Margin(
                    l=0, #left margin
                    r=0, #right margin
                    b=0, #bottom margin
                    t=0  #top margin
                ),

            font={
            'color':'rgb(157, 211, 49)'
            },
            )
        
        return plot(fig2, output_type='div', include_plotlyjs=False)



    
@receiver(post_save, sender=User)
def createProfile(sender, created, instance, **kwargs):
    if created:
        Profile.objects.create(user=instance)

    permission1 = Permission.objects.get(codename='add_merchant')
    permission2 = Permission.objects.get(codename='add_incomecategory')
    permission3 = Permission.objects.get(codename='add_incomesource')
    instance.user_permissions.add(permission1, permission2, permission3)