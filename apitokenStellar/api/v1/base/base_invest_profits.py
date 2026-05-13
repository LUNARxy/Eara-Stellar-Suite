import calendar
from collections import defaultdict

from sqlalchemy import asc, literal_column, func, or_, desc
from sqlalchemy.orm import Session
from datetime import datetime

from api.v1 import const
from api.v1.base.base import Object
from api.v1.models import models_user


def _get_value_profit_percentage(
        invest_value: float,
        profit_percentage: float,
        investment_date: datetime,
        profit_day: int
):
    # se calcula el beneficio obtenido de cada inversion en la fecha del profit_day desde que se hizo la inversion

    # Get the current month and year from the system
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    profit_day = profit_day - 1

    # Calculate the full monthly profit
    monthly_profit = invest_value * (profit_percentage / 100)

    # Get the number of days in the current month
    days_in_current_month = calendar.monthrange(current_year, current_month)[1]

    # Case 1: Investment made in the same month and year as current_day
    if investment_date.year == current_year and investment_date.month == current_month:
        if investment_date.day > profit_day:
            # No profit because the investment was made after the profit_day
            return 0
        else:
            # Proportional days invested from investment date to profit_day
            days_invested = profit_day - investment_date.day + 1
            proportional_profit = (monthly_profit / days_in_current_month) * days_invested

    # Case 2: Investment made in previous month or earlier
    else:
        # Calculate the number of months passed from investment_date to the current date
        months_passed = (current_year - investment_date.year) * 12 + (current_month - investment_date.month)

        # Full month profit multiplied by the number of full months that have passed
        full_month_profit = monthly_profit * months_passed

        # Proportional profit for extra days in the current month
        extra_days_profit = (monthly_profit / days_in_current_month) * (profit_day - investment_date.day)

        # Total profit: full month + extra days
        proportional_profit = full_month_profit + extra_days_profit

    if proportional_profit > monthly_profit:
        return monthly_profit
    else:
        return proportional_profit


def _get_list_user_profit_percentage(
        db: Session,
        invest_id: int,
        profit_percentage: float,
        profit_day: int
):
    # devuelve la lista de usuarios con el beneficio de porcentaje que le toca y el dinero que tiene invertido

    # se recuperan las inversiones
    q = db.query(models_user.UsersInvest.user_id, models_user.UsersInvest.value, models_user.UsersInvest.date_created)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_BUY))
    list_users_invest = q.distinct().all()

    # se le va restando las inversiones devueltas
    q = db.query(models_user.UsersInvest.user_id, models_user.UsersInvest.value, models_user.UsersInvest.date_created)
    q = q.filter(models_user.UsersInvest.invest_id == invest_id)
    q = q.filter(or_(models_user.UsersInvest.type == const.USERS_INVEST_TYPE_SOLD,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND,
                     models_user.UsersInvest.type == const.USERS_INVEST_TYPE_REFUND_PARTIAL))
    list_users_invest_sold_refund = q.all()

    # Diccionario para almacenar el saldo de cada usuario a lo largo del tiempo
    user_transactions = defaultdict(list)

    # Registrar compras en orden
    for invest in list_users_invest:
        user_transactions[invest.user_id].append({"date": invest.date_created, "value": invest.value})

    # Aplicar las ventas en orden cronológico
    for sold_refund in list_users_invest_sold_refund:
        user_id = sold_refund.user_id
        refund_value = sold_refund.value

        if user_id in user_transactions:
            # Restar ventas de las compras previas
            for transaction in user_transactions[user_id]:
                if refund_value > 0:
                    if transaction["value"] >= refund_value:
                        transaction["value"] -= refund_value
                        refund_value = 0
                    else:
                        refund_value -= transaction["value"]
                        transaction["value"] = 0
                else:
                    break  # Terminamos cuando ya hemos restado todo

    # Construimos el resultado final con los valores ajustados
    adjusted_users_invest = [
        {
            "user_id": user_id,
            "date_created": transaction["date"],
            "value": transaction["value"]
        }
        for user_id, transactions in user_transactions.items()
        for transaction in transactions
        if transaction["value"] > 0  # Filtramos compras que quedaron en 0
    ]

    user_profits = {}

    for user_invest in adjusted_users_invest:
        total_profits = _get_value_profit_percentage(invest_value=user_invest['value'], profit_percentage=profit_percentage, investment_date=user_invest['date_created'], profit_day=profit_day)
        total_invest = user_invest['value']

        # Si el 'user_id' no está en el diccionario, lo inicializamos con valores de 0
        if user_invest['user_id'] not in user_profits:
            user_profits[user_invest['user_id']] = {'total_invest': 0, 'profit_value': 0}

        user_profits[user_invest['user_id']]['total_invest'] += total_invest
        user_profits[user_invest['user_id']]['profit_value'] += total_profits

    # Convert the accumulated user profits into a list of dictionaries
    list_users_tokens = [{'user_id': user_id, 'total_invest': values['total_invest'], 'profit_value': values['profit_value']} for user_id, values in user_profits.items()]

    # para cada inversion, si tiene tokens mayor que cero se guardan en el listado
    list_users_out = []
    for item in list_users_tokens:
        # se recuperan sus datos
        q = db.query(models_user.User.id, models_user.User.email, models_user.UserDataPhysicalPerson)
        q = q.filter(models_user.User.id == item['user_id'])
        q = q.outerjoin(models_user.UserDataPhysicalPerson, models_user.User.id == models_user.UserDataPhysicalPerson.user_id)
        for users in q.all():
            aux_user = Object()
            aux_user.user_id = users.id
            aux_user.email = users.email
            if users.UserDataPhysicalPerson:
                aux_user.name = users.UserDataPhysicalPerson.name
                aux_user.surname = users.UserDataPhysicalPerson.surname
            aux_user.value = item['profit_value']
            aux_user.total_invest = item['total_invest']
            list_users_out.append(aux_user)

            # revisamos el porcentaje que el usuario no quiere sacar y el que si quiere
            q = db.query(models_user.UsersInvestProfitPercentage)
            q = q.filter(models_user.UsersInvestProfitPercentage.invest_id == invest_id)
            q = q.filter(models_user.UsersInvestProfitPercentage.user_id == aux_user.user_id)
            profit_percentage = q.first()
            # print(f'valor total para el usuario {item.user_id} {item.value}')
            value_to_refund = 0
            profit_percentage_to_refund = 0
            if profit_percentage:
                profit_percentage_to_refund = profit_percentage.profit_percentage
                # print(f'valor porcentage a devolver {profit_percentage_to_refund}')
                value_to_refund = aux_user.value * profit_percentage_to_refund / 100
            aux_user.profit_to_refund = value_to_refund
            aux_user.profit_percentage_to_refund = profit_percentage_to_refund

    return list_users_out
