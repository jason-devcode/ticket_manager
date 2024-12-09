from django.urls import path

from . import views
from .wompi_webhook import wompi_webhook

from .crud_views import crud_lottery, crud_tickets


urlpatterns = [
    path(
        "api/balance_payment_list/<int:seller_id>",
        views.get_seller_balance_payment_list,
        name="get_seller_balance_payment_list",
    ),
    path(
        "api/generate_seller_bill/<int:seller_id>",
        views.generate_seller_bill_endpoint,
        name="generate_seller_bill_endpoint",
    ),
    path(
        "api/verify_purchase/<int:client_id>",
        views.verify_ticket_purchase,
        name="verify_ticket_purchase",
    ),
    path(
        "api/get_client_side_whatsapp",
        views.get_client_side_whatsapp,
        name="get_client_side_whatsapp",
    ),
    path(
        "api/get_ticket_state",
        views.get_ticket_state,
        name="get_ticket_state",
    ),
    path(
        "api/get_client_bill_data/<int:clientId>/<int:billType>",
        views.get_client_bill_data,
        name="get_client_bill_data",
    ),

    path(
        "api/get_ticket_png_data/<int:client_id>",
        views.get_ticket_png_data,
        name="get_ticket_png_data"
    ),
    path(
        "api/decline_ticket/<int:client_id>",
        views.decline_ticket,
        name="decline_ticket"
    ),
    path(
        "api/get_tickets_to_assign",
        views.get_tickets_to_assign,
        name="get_tickets_to_assign"
    ),
    path(
        "api/get_ticket_info/<int:lottery_id>/<int:ticket_number>",
        views.get_ticket_info,
        name="get_ticket_info"
    ),
    path("api/wompi_webhook", wompi_webhook, name="wompi_webhook"),
]


urlpatterns.extend(crud_lottery.urlpatterns)
urlpatterns.extend(crud_tickets.urlpatterns)
