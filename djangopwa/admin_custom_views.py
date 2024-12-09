# mi_app/views.py (o admin.py)
from django.db.models import Sum
from . import models
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.shortcuts import render
from django.contrib import admin

from djangopwa.constants import TicketState
from djangopwa.models import Lottery


def calculate_tickets_with_payment(lottery):
    clients = models.ClientInfo.objects.filter(lottery_to_buy=lottery)
    tickets_with_payment = sum(
        1 for client in clients
        if models.Payment.objects.filter(client=client).exists()
        and client.ticket_number.state == TicketState.RESERVED
    )
    return tickets_with_payment


def calculate_total_money_raised():
    total_money_raised = models.Payment.objects.aggregate(Sum('amount'))[
        'amount__sum'] or 0
    return total_money_raised


def calculate_current_percentage(lottery):
    lottery_total_tickets = lottery.upper_series_range - lottery.lower_series_range + 1
    available_tickets = lottery.ticket_set.filter(state=TicketState.AVAILABLE)
    available_tickets_percentage = len(
        available_tickets) / lottery_total_tickets
    current_percentage = (1.0 - available_tickets_percentage) * 100
    return current_percentage


def get_lottery_statistics(lottery):
    purchased_tickets = lottery.ticket_set.filter(state=TicketState.PURCHASED)
    pending_tickets = models.TicketPendingPurchase.objects.count()
    tickets_with_payments = calculate_tickets_with_payment(lottery)
    total_money_raised = calculate_total_money_raised()
    current_percentage = calculate_current_percentage(lottery)

    return {
        "total_money_raised": "{:,.0f}".format(total_money_raised).replace(",", "."),
        "percentage": current_percentage,
        "pending_tickets": pending_tickets,
        "complete_tickets_payment": len(purchased_tickets),
        "tickets_with_payments": tickets_with_payments,
    }


@staff_member_required
def custom_admin_tickets_view(request):
    context = admin.site.each_context(request)

    lottery = Lottery.objects.order_by("id").first()
    ticket_number = request.GET.get('ticket_number')

    context["hasAvailableTickets"] = False
    context["lottery_id"] = lottery.id if lottery else ""

    if lottery:
        if request.user.is_superuser:
            # If the user is a super admin, show all available tickets
            tickets = lottery.ticket_set.filter(state=TicketState.AVAILABLE)
        else:
            # Get assignments for the current user
            assigned_tickets = models.TicketAssignment.objects.filter(assigned_to=request.user)
            ticket_ids = set()

            if assigned_tickets.exists():
                # Add individual tickets to the set
                for assignment in assigned_tickets:
                    ticket_ids.update(assignment.individual_tickets.values_list('id', flat=True))
                    
                    # Add tickets in the range
                    if assignment.start_number is not None and assignment.end_number is not None:
                        range_tickets = lottery.ticket_set.filter(
                            number__gte=assignment.start_number,
                            number__lte=assignment.end_number
                        ).values_list('id', flat=True)
                        ticket_ids.update(range_tickets)

                tickets = lottery.ticket_set.filter(state=TicketState.AVAILABLE, id__in=ticket_ids)
            else:
                # No assignments, return an empty queryset
                tickets = models.Ticket.objects.none()

        if ticket_number:
            tickets = tickets.filter(number=ticket_number)

        context["tickets"] = tickets
        context["hasAvailableTickets"] = tickets.exists()
    else:
        context["tickets"] = models.Ticket.objects.none()

    return render(request, 'admin/available_tickets_view.html', context)


@staff_member_required
def admin_reports_view(request):
    context = admin.site.each_context(request)

    try:
        lottery = models.Lottery.objects.latest("id")
        lottery_stats = get_lottery_statistics(lottery)
    except models.Lottery.DoesNotExist:
        lottery_stats = {
            "total_money_raised": "0",
            "percentage": 0,
            "pending_tickets": 0,
            "complete_tickets_payment": 0,
            "tickets_with_payments": 0,
        }

    context["lottery_stats"] = lottery_stats
    return render(request, 'admin/reports_view.html', context)
