from django import template
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money

register = template.Library()


@register.simple_tag 
def convertMoney(moneyobject, currency): 
    return convert_money(moneyobject, currency)