from django.db.models import Q
from typing import List, Any

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet, Sum
from django.db import transaction
from django import forms

from django.urls import reverse, path
from django.utils.html import format_html
from django.template.response import TemplateResponse

from djangopwa import constants
from djangopwa import models

from djangopwa.forms.admin import ClientInfoAdminForm, PaymentForm, TicketReservedForm
from djangopwa.forms.ticket_forms import TicketAssignmentForm
from djangopwa.forms.lottery_forms import LotteryCreateForm
from djangopwa.forms.user import PaymentContactForm
from djangopwa.utils.complex_filter import build_complex_filter

from datetime import datetime, timedelta


class LotteryMultimediaInline(admin.TabularInline):
    model = models.LotteryMultimedia
    extra = 1
    fields = ("multimedia",)


class BillImageInline(admin.TabularInline):
    model = models.BillImage
    extra = 1
    fields = ("image", "image_type")


@admin.register(models.Lottery)
class LotteryAdminModel(admin.ModelAdmin):
    form = LotteryCreateForm
    inlines = [LotteryMultimediaInline, BillImageInline]

    list_display = (
        "name",
        "lottery_date_1",
        "lottery_date_2",
        "lottery_date_3",
        "lottery_date_4",
        "price_per_ticket",
    )
    search_fields = ("name",)
    list_filter = (
        "lottery_date_1",
        "lottery_date_2",
        "lottery_date_3",
        "lottery_date_4",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "price_per_ticket",
                    "lottery_date_1",
                    "lottery_date_2",
                    "lottery_date_3",
                    "lottery_date_4",
                    "lower_series_range",
                    "upper_series_range",
                ),
            },
        ),
    )

    def create_tickets_in_range(self, lottery, start_number, end_number):
        """
        Create tickets in the specified range for the given lottery.

        Args:
            lottery (Lottery): The lottery for which tickets are to be created.
            start_number (int): The starting number of the range.
            end_number (int): The ending number of the range.
        """
        tickets = [
            models.Ticket(lottery=lottery, number=number)
            for number in range(start_number, end_number + 1)
        ]
        models.Ticket.objects.bulk_create(tickets)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        """
        Save the model and create the tickets in the specified range.

        Args:
            request (Any): The current request object.
            obj (Any): The object being saved.
            form (Any): The form instance.
            change (Any): A boolean value; True if this is a change and False if it is a new object.
        """
        super().save_model(request, obj, form, change)
        # Create tickets only if this is a new lottery (not on change)
        if not change:
            start_number = form.cleaned_data.get("lower_series_range")
            end_number = form.cleaned_data.get("upper_series_range")
            self.create_tickets_in_range(obj, start_number, end_number)


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment model.

    Attributes:
        list_display (tuple): Fields displayed in the admin list view.
        list_filter (tuple): Fields available for filtering in the admin.
        search_fields (tuple): Fields available for searching in the admin.
    """

    list_display = ("client", "payment_method",
                    "amount", "date", "payment_type")
    list_filter = ("payment_type",)
    search_fields = ("client__name", "payment_method__name")

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a customized form based on the user's permissions.

        Args:
            request (HttpRequest): The request object.
            obj (Payment, optional): The object being edited, if any.
            **kwargs: Additional keyword arguments.

        Returns:
            django.forms.ModelForm: Customized form object.
        """
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            form.base_fields["seller"].widget = forms.HiddenInput()

        return form

    def get_queryset(self, request):
        """
        Filters the queryset based on the authenticated user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            QuerySet: Filtered queryset based on user permissions.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all records
        else:
            return qs.filter(seller=request.user)


class PaymentInline(admin.StackedInline):
    """
    Inline admin configuration for Payment model.

    Attributes:
        model (Payment): The Payment model class.
        extra (int): Number of extra inline forms to display.
        form (PaymentForm): Custom form class to use for inline editing.
    """

    model = models.Payment
    extra = 1
    form = PaymentForm

    def get_formset(self, request, obj=None, **kwargs):
        """
        Returns a formset for inline editing based on the request and object.

        Args:
            request (HttpRequest): The request object.
            obj (Model, optional): The parent object being edited, if any.
            **kwargs: Additional keyword arguments.

        Returns:
            django.forms.BaseInlineFormSet: Customized inline formset object.
        """
        formset = super().get_formset(request, obj, **kwargs)
        self.parent_instance = obj
        return formset

    def get_queryset(self, request):
        """
        Returns the queryset for inline editing based on the request.

        Args:
            request (HttpRequest): The request object.

        Returns:
            django.db.models.query.QuerySet: Filtered queryset.
        """
        if self.parent_instance:
            return super().get_queryset(request).filter(client=self.parent_instance)
        return super().get_queryset(request).none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Returns a formfield for a foreign key field based on the request.

        Args:
            db_field (django.db.models.ForeignKey): The foreign key field.
            request (HttpRequest): The request object.
            **kwargs: Additional keyword arguments.

        Returns:
            django.forms.models.ModelChoiceField: Customized form field.
        """
        if db_field.name == "seller":
            kwargs["initial"] = request.user
            if not request.user.is_superuser:
                kwargs["widget"] = forms.HiddenInput()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_formset(self, request, form, formset, change):
        """
        Saves the formset data, ensuring at least two fields are filled.

        Args:
            request (HttpRequest): The request object.
            form (django.forms.ModelForm): The form object.
            formset (django.forms.BaseInlineFormSet): The formset object.
            change (bool): Flag indicating if the object is being changed.

        Returns:
            None
        """
        instances = formset.save(commit=False)
        for instance in instances:
            # Check that at least two fields are filled
            if not instance.pk:
                instance.seller = request.user
            filled_fields = [
                field
                for field in instance._meta.fields
                if getattr(instance, field.name)
            ]
            if len(filled_fields) < 2:
                continue  # Do not save this instance
            instance.save()
        formset.save_m2m()

    class Media:
        js = ("js/custom_inline_client_payment.js",)


@admin.register(models.ClientInfo)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin configuration for ClientInfo model.

    Attributes:
        form (Form): Form class used for this admin.
        list_display (tuple): Fields displayed in the admin list view.
        inlines (list): Inline models displayed in the admin.
    """

    form = ClientInfoAdminForm

    search_fields = ['ticket_number__number', "name",
                     "lastname", "document_number"]

    list_display = (
        "ticket_number",
        "name_and_lastname",
        "document_number",
        "city",
        "telephone_field",
        "lottery_to_buy",
        "id_seller",
        "modify_payments_button",
        # "modify_total_payment_button",
        "bills_button",
        "whatsapp_button",
        "delete_button",
        "edit_button",
    )

    inlines = [PaymentInline]

    def bills_button(self, obj):

        dropdownBillsSelectorHTML = f"""
        <div class="client-bills-dropdown" style="position: relative; display: inline-block;">
            <div class="client-bills-dropdown-button" style="background-color: #4CAF50; color: white; padding: 10px; font-size: 16px; border: none; cursor: pointer; border-radius: 5px;" onclick="toggleDropdown('dropdown-{obj.id}')">
                Facturas
            </div>
            <div id="dropdown-{obj.id}" class="client-bills-dropdown-content" style="display: none; position: absolute; background-color: #f9f9f9; min-width: 160px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); z-index: 1; border-radius: 5px;">
                <div onclick="getClientBill({obj.id}, 1)" class="client-bills-dropdown-item">Factura Bono 1</div>
                <div onclick="getClientBill({obj.id}, 2)" class="client-bills-dropdown-item">Factura Bono 2</div>
                <div onclick="getClientBill({obj.id}, 3)" class="client-bills-dropdown-item">Factura Bono 3</div>
                <div onclick="getClientBill({obj.id}, 4)" class="client-bills-dropdown-item">Factura Pago Total</div>
            </div>
        </div>
        """

        return format_html(dropdownBillsSelectorHTML)

    bills_button.short_description = "Facturas"
    bills_button.allow_tags = True

    def modify_payments_button(self, obj: models.Payment):
        """
        Generates a button to modify payments for a ClientInfo object.

        Args:
            obj (Payment): The Payment object related to the ClientInfo.

        Returns:
            str: HTML formatted button to modify payments.
        """
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/{obj.id}/change/#pagos-tab" class="btn btn-secondary">Modificar</a>'
        )

    modify_payments_button.short_description = "Abonos(1,2,3)"
    modify_payments_button.allow_tags = True

    def modify_total_payment_button(self, obj: models.Payment):
        """
        Generates a button to modify total payments for a ClientInfo object.

        Args:
            obj (Payment): The Payment object related to the ClientInfo.

        Returns:
            str: HTML formatted button to modify total payment.
        """
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/{obj.id}/change/#pagos-tab" class="btn btn-secondary">Modificar</a>'
        )

    modify_total_payment_button.short_description = "Pago total"
    modify_total_payment_button.allow_tags = True

    def id_seller(self, obj: models.ClientInfo):
        """
        Retrieves the ID of the seller associated with a ClientInfo object.

        Args:
            obj (ClientInfo): The ClientInfo object.

        Returns:
            int: ID of the seller.
        """
        seller = obj.seller
        return seller.id

    id_seller.short_description = "ID Vendedor"

    def name_and_lastname(self, obj):
        return format_html(
            f"<p>{obj.name} {obj.lastname}</p>",
        )

    name_and_lastname.short_description = "Nombre y apellidos"
    name_and_lastname.allow_tags = True

    def telephone_field(self, obj):
        return format_html(
            f"<p>{obj.whatsapp}</p>",
        )

    telephone_field.short_description = "Teléfono"
    telephone_field.allow_tags = True

    def whatsapp_button(self, obj):
        return format_html(
            f'<a href="https://wa.me/{obj.whatsapp}" class="logos--whatsapp-icon"></a>',
        )

    whatsapp_button.short_description = "Whatsapp"
    whatsapp_button.allow_tags = True

    def delete_button(self, obj):
        """
        Returns a button to initiate balance payment for the seller.

        Args:
            obj (User): The User object.

        Returns:
            django.utils.safestring.SafeString: HTML representation of the button.
        """
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/{obj.id}/delete/" class="material-symbols--delete-outline"></a>',
        )

    delete_button.short_description = "Eliminar"
    delete_button.allow_tags = True

    def edit_button(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/{obj.id}/change/" class="dashicons--edit"></a>',
        )

    edit_button.short_description = "Editar"
    edit_button.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a customized form based on the user's permissions.

        Args:
            request (HttpRequest): The request object.
            obj (ClientInfo, optional): The object being edited, if any.
            **kwargs: Additional keyword arguments.

        Returns:
            django.forms.ModelForm: Customized form object.
        """
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user

        if not request.user.is_superuser:
            form.base_fields["seller"].widget = forms.HiddenInput()

        form.base_fields["seller"].initial = request.user

        lottery_to_buy = (
            request.GET.get("lottery_to_buy")
            or request.POST.get("lottery_to_buy")
            or (obj and obj.lottery_to_buy.id)
        )

        self.filter_ticket_numbers_by_assignment(
            form, lottery_to_buy, request.user, obj and obj.ticket_number
        )

        return form

    def get_seller_ticket_assignments(self, current_user, initial_lottery_to_buy):
        return models.TicketAssignment.objects.filter(
            assigned_to=current_user, lottery=initial_lottery_to_buy
        )

    def get_ticket_number_ranges(self, seller_ticket_assignments):
        ticket_number_ranges = []
        for assignment in seller_ticket_assignments:
            if assignment.start_number is not None and assignment.end_number is not None:
                ticket_number_ranges.extend(range(
                    assignment.start_number,
                    assignment.end_number + 1,
                ))
        return ticket_number_ranges

    def get_individual_ticket_numbers(self, seller_ticket_assignments):
        individual_ticket_numbers = []
        for assignment in seller_ticket_assignments:
            individual_ticket_numbers.extend(
                list(assignment.individual_tickets.values_list('number', flat=True)))
        return individual_ticket_numbers

    def combine_ticket_numbers(self, ticket_number_ranges, individual_ticket_numbers):
        return set(ticket_number_ranges) | set(individual_ticket_numbers)

    def filter_ticket_numbers_by_assignment(
        self,
        form,
        lottery_to_buy,
        current_user,
        change_ticket_number: models.Ticket = None,
    ):
        """
        Filters ticket numbers based on seller's assignments and lottery.

        Args:
            form (Form): The form object.
            lottery_to_buy (int): ID of the lottery to buy.
            current_user (User): The current user (seller).
            change_ticket_number (Ticket, optional): The ticket being changed.

        Returns:
            None
        """
        ticket_numbers = models.Ticket.objects.none()

        if lottery_to_buy and current_user:
            seller_ticket_assignments = self.get_seller_ticket_assignments(
                current_user=current_user, initial_lottery_to_buy=lottery_to_buy
            )

            if not current_user.is_superuser and (
                not seller_ticket_assignments or len(
                    seller_ticket_assignments) <= 0
            ):
                form.base_fields["ticket"].queryset = ticket_numbers
                return

            extra_ticket_conditions_info = {}
            extra_ticket_conditions_info_purchased = {}

            if change_ticket_number:
                extra_ticket_conditions_info["number"] = change_ticket_number.number
                extra_ticket_conditions_info["state"] = constants.TicketState.RESERVED

                extra_ticket_conditions_info_purchased["number"] = (
                    change_ticket_number.number
                )
                extra_ticket_conditions_info_purchased["state"] = (
                    constants.TicketState.PURCHASED
                )

            ticket_numbers_conditions = [
                {
                    "lottery": lottery_to_buy,
                    "state": constants.TicketState.AVAILABLE,
                },
                extra_ticket_conditions_info,
                extra_ticket_conditions_info_purchased,
            ]

            # add filter by ticket ranges if user is a seller
            if not current_user.is_superuser:
                ticket_number_ranges = self.get_ticket_number_ranges(
                    seller_ticket_assignments)
                individual_ticket_numbers = self.get_individual_ticket_numbers(
                    seller_ticket_assignments)
                all_ticket_numbers = self.combine_ticket_numbers(
                    ticket_number_ranges, individual_ticket_numbers)

                ticket_numbers_conditions[0]["number__in"] = all_ticket_numbers

            ticket_numbers_complex_filter = build_complex_filter(
                ticket_numbers_conditions
            )

            ticket_numbers = models.Ticket.objects.filter(
                ticket_numbers_complex_filter)

        form.base_fields["ticket_number"].queryset = ticket_numbers

        return ticket_numbers

    def save_related(self, request, form, formsets, change):
        """
        Overrides save_related to ensure that inline objects are saved before the main object.

        Args:
            request (HttpRequest): The request object.
            form (django.forms.ModelForm): The form object.
            formsets (list): List of formsets related to the main form.
            change (bool): Flag indicating if the object is being changed.

        Returns:
            None
        """
        with transaction.atomic():
            super().save_related(request, form, formsets, change)

    def save_model(self, request, obj, form, change):
        """
        Override the save_model method to set the seller as the current user.

        Args:
            request (HttpRequest): The request object.
            obj (ClientInfo): The ClientInfo object being saved.
            form (Form): The form object.
            change (bool): Whether the object is being changed or created.

        Returns:
            None
        """
        if not obj.seller_id:
            obj.seller = request.user  # Set the seller as the current logged-in user
        super().save_model(request, obj, form, change)

    def before_delete_logic(self, request, obj):
        """
        Additional logic to execute before the object is deleted.

        Args:
            request (HttpRequest): The request object.
            obj (ClientInfo): The ClientInfo object being deleted.

        Returns:
            None
        """
        if obj.ticket_number:
            obj.ticket_number.state = constants.TicketState.AVAILABLE
            obj.ticket_number.save()

    def delete_model(self, request, obj):
        """
        Override the delete_model method to add additional logic before deleting a ClientInfo object.

        Args:
            request (HttpRequest): The request object.
            obj (ClientInfo): The ClientInfo object being deleted.

        Returns:
            None
        """
        # Execute any additional logic before deleting the object
        self.before_delete_logic(request, obj)

        # Call the superclass method to proceed with the deletion
        super().delete_model(request, obj)

    def get_queryset(self, request):
        """
        Method to filter the queryset based on the authenticated user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            QuerySet: Filtered queryset based on user permissions.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all records
        else:
            return qs.filter(seller=request.user)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def is_numeric_search(self, search_term):
        """Check if the search term consists only of digits."""
        return search_term.isdigit()

    def search_by_number(self, queryset, search_number):
        """Search by ticket number or document number."""
        return queryset.filter(
            Q(ticket_number__number=search_number) |
            Q(document_number=search_number)
        )

    def search_by_name(self, queryset, search_terms):
        """Search by name and lastname."""
        if len(search_terms) > 1:
            # If there are multiple search terms, search across name and lastname
            query = Q()
            for term in search_terms:
                query &= Q(name__icontains=term) | Q(
                    lastname__icontains=term)
            return queryset.filter(query)
        else:
            # Standard search if there is only one term
            search_term = search_terms[0]
            return queryset.filter(
                Q(name__icontains=search_term) |
                Q(lastname__icontains=search_term) |
                Q(ticket_number__number__icontains=search_term) |
                Q(document_number__icontains=search_term) |
                Q(purchase_reference__icontains=search_term)
            )

    def get_search_results(self, request, queryset, search_term):
        """Customize search behavior in the admin."""
        # Check if the search term is empty
        if not search_term.strip():
            # Return the unfiltered queryset if the search term is empty
            return queryset, False

        if self.is_numeric_search(search_term):
            # Parse the search term to an integer for numeric search
            search_number = int(search_term)
            queryset = self.search_by_number(queryset, search_number)
        else:
            # Split the search term into words for name-based search
            search_terms = search_term.split()
            queryset = self.search_by_name(queryset, search_terms)

        # Return the search results along with a boolean indicating if there were more results
        return queryset, False

    def get_list_display_links(self, request, list_display):
        """
        Override to prevent the first column from being a link.
        """
        # Prevent the first column ('ticket') from being a link
        return None

    def has_add_permission(self, request):
        return False

    class Media:
        js = ("js/custom_client_bills.js",)  # path to custom javascript


class ClientInfoInline(admin.TabularInline):
    """
    Inline admin configuration for ClientInfo model.

    Attributes:
        model (Model): The ClientInfo model to inline.
        extra (int): Number of extra forms displayed.
        can_delete (bool): Whether inline forms can be deleted.
        readonly_fields (list): Fields that are read-only in the admin interface.
    """

    model = models.ClientInfo
    extra = 0
    can_delete = False

    readonly_fields = [
        "name",
        "lastname",
        "lottery_to_buy",
        "ticket_number",
        "city",
        "whatsapp",
        "document_number",
        "telephone",
    ]

    def has_add_permission(self, request, obj=None):
        """
        Disables the ability to add new ClientInfo instances inline.

        Args:
            request (HttpRequest): The request object.
            obj (Model, optional): The object being edited in the admin.

        Returns:
            bool: False, indicating add permission is disabled.
        """
        return False

    def get_queryset(self, request):
        """
        Filters the queryset based on the authenticated user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            QuerySet: Filtered queryset based on user permissions.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(seller=request.user)


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for User model.

    Attributes:
        fieldsets (tuple): Sets of fields to display in the admin interface.
        add_fieldsets (tuple): Sets of fields to display when adding a new user.
        list_display (tuple): Fields displayed in the admin list view.
        search_fields (tuple): Fields available for searching in the admin.
        list_filter (tuple): Fields available for filtering in the admin.
        inlines (list): Inline classes to include in the admin interface.
        Media (class): Class defining additional media (JavaScript) files for the admin interface.
    """

    fieldsets = (
        (
            "Informacion Personal",
            {
                "fields": (
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                    "email",
                    "document_number",
                    "city_residence",
                    "whatsapp",
                )
            },
        ),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Roles", {"fields": ("role",)}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "role",
                    "first_name",
                    "last_name",
                    "city_residence",
                    "email",
                    "document_number",
                    "whatsapp",
                ),
            },
        ),
    )

    list_display = (
        "id_sellers",
        "username_link",
        "first_name",
        "last_name",
        "document_number",
        "city_residence",
        "whatsapp",
        "look_client_list_button",
        "balance_payments_button",
        "total_clients",
        "email",
        "delete_button",
    )
    search_fields = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "document_number",
    )
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    inlines = [ClientInfoInline]

    def get_urls(self):
        """
        Returns additional URL patterns for the admin interface.

        Returns:
            list: Additional URL patterns.
        """
        urls = super().get_urls()
        custom_urls = [
            path("custom_tab/", self.custom_view, name="custom_tab"),
        ]
        return custom_urls + urls

    def custom_view(self, request):
        """
        Custom admin view for displaying balance payment information.

        Args:
            request (HttpRequest): The request object.

        Returns:
            TemplateResponse: Template response object.
        """
        context = self.admin_site.each_context(request)
        return TemplateResponse(request, "admin/balance_payment.html", context)

    def id_sellers(self, obj: models.User):
        """
        Returns the ID of the seller user.

        Args:
            obj (User): The User object.

        Returns:
            int: ID of the seller user.
        """
        return obj.id

    def total_clients(self, obj: models.User):
        """
        Returns the total number of clients associated with the user.

        Args:
            obj (User): The User object.

        Returns:
            int: Total number of clients.
        """
        return obj.clientinfo_set.count()

    def username_link(self, obj: models.User):
        """
        Returns a clickable link to the user's change page in the admin.

        Args:
            obj (User): The User object.

        Returns:
            django.utils.safestring.SafeString: HTML representation of the link.
        """
        url = reverse("admin:djangopwa_user_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.username)

    username_link.admin_order_field = "username"
    username_link.short_description = "Nombre de usuario"

    total_clients.short_description = "Total Clientes"

    id_sellers.short_description = "ID Vendedores"

    def look_client_list_button(self, obj: models.User):
        """
        Returns a button to view the client list associated with the user.

        Args:
            obj (User): The User object.

        Returns:
            django.utils.safestring.SafeString: HTML representation of the button.
        """
        return format_html(
            f'<a href="/admin/djangopwa/user/{obj.id}/change/#clientes-tab" class="btn btn-secondary" style="white-space: nowrap;">Ver lista</a>'
        )

    look_client_list_button.short_description = "Clientes"
    look_client_list_button.allow_tags = True

    def balance_payments_button(self, obj):
        """
        Returns a button to initiate balance payment for the seller.

        Args:
            obj (User): The User object.

        Returns:
            django.utils.safestring.SafeString: HTML representation of the button.
        """
        return format_html(
            f'<div class="btn btn-secondary" onclick="balance_seller_payment({obj.id})" >Cobrar</div>',
        )

    balance_payments_button.short_description = "Cuadre"
    balance_payments_button.allow_tags = True

    def delete_button(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/user/{obj.id}/delete/" class="btn btn-danger">Eliminar</a>',
        )

    delete_button.short_description = ""
    delete_button.allow_tags = True

    def get_inline_instances(self, request, obj=None):
        """
        Returns inline instances based on the request and object.

        Args:
            request (HttpRequest): The request object.
            obj (User, optional): The User object being edited.

        Returns:
            list: Inline instances for the admin interface.
        """
        if not obj:
            return []
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        """
        Overrides the save_model method to customize user saving behavior in the admin.

        Args:
            request (HttpRequest): The request object.
            obj (User): The User object being saved.
            form (django.forms.ModelForm): The form object.
            change (bool): Flag indicating if the object is being changed.

        Returns:
            User: The saved User object.
        """
        user = form.save(commit=False)
        if not change:
            user.set_password(form.cleaned_data["password1"])
        user.save()

        if not user.is_superuser:
            group = Group.objects.get(name="Vendedores")
            user.groups.add(group)

        return user

    class Media:
        js = (
            "js/seller_admin_payment_popup.js",
            "js/custom_user_admin.js",
        )


@admin.register(models.TicketAssignment)
class TicketAssignmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for TicketAssignment model.

    Attributes:
        form (Form): Form class used for this admin.
        list_display (list): Fields displayed in the admin list view.
        list_filter (list): Fields available for filtering in the admin.
        search_fields (list): Fields available for searching in the admin.
    """

    form = TicketAssignmentForm
    list_display = [
        "assigned_to",
        "lottery",
        "start_number",
        "end_number",
        "total_tickets",
        "display_individual_tickets",
    ]
    list_filter = ["lottery", "assigned_to"]
    search_fields = ["assigned_to__username"]

    def total_tickets(self, obj):
        """
        Calculates the total number of tickets based on the difference between end_number and start_number.

        Args:
            obj (TicketAssignment): The TicketAssignment object.

        Returns:
            int: Total number of tickets.
        """
        return ((obj.end_number - obj.start_number + 1) if obj.end_number and obj.start_number else 0) + obj.individual_tickets.count()  # +1 to include both endpoints

    total_tickets.short_description = "Total Boletas Asignadas"

    def display_individual_tickets(self, obj):
        """
        Displays the individual tickets associated with the TicketAssignment.

        Args:
            obj (TicketAssignment): The TicketAssignment object.

        Returns:
            str: A comma-separated string of ticket numbers.
        """
        return ", ".join([f"{ticket.number:04}" for ticket in obj.individual_tickets.all()])

    display_individual_tickets.short_description = "Boletas individuales"

    def get_queryset(self, request):
        """
        Filters the queryset based on the authenticated user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            QuerySet: Filtered queryset based on user permissions.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all records
        else:
            return qs.filter(assigned_to=request.user)

    class Media:
        js = ("js/custom_ticket_assignment.js",)


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    # list_filter = ["lottery__name"]

    # list_display = ["lottery", "number", "state", "delete_button"]
    list_display = ["number", "state", "delete_button", "sell_button"]
    search_fields = ("number",)

    def delete_button(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/ticket/{obj.id}/delete/" class="btn btn-danger">Eliminar</a>',
        )

    delete_button.short_description = ""
    delete_button.allow_tags = True

    def sell_button(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/add/?lottery_to_buy={obj.lottery.id}&ticket_number={obj.id}" class="btn btn-secondary">Vender</a>',
        )

    sell_button.short_description = ""
    sell_button.allow_tags = True


@admin.register(models.SellerBill)
class SellerBillAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True


@admin.register(models.ClientTicketPaymentBalance)
class ClientTicketPaymentBalanceAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True


@admin.register(models.PaymentContact)
class PaymentContactAdmin(admin.ModelAdmin):
    form = PaymentContactForm


class BaseAdminTable(admin.ModelAdmin):
    search_fields = ['ticket__number', "client__name",
                     "client__lastname", "client__document_number"]

    list_display = ("ticket_number", "client_name_lastname", "client_document_number",
                    "client_telephone", "client_city", "client_seller", "client_payments", "payment_balance", "amount_to_pay", "bills_button", "verify_purchase", "client_whatsapp", "ticket_png", "edit_button")

    def ticket_number(self, obj):
        return f"{obj.client.ticket_number.number:04}" if obj.client.ticket_number else ""

    ticket_number.short_description = "Boleta"
    ticket_number.allow_tags = True

    def client_name_lastname(self, obj):
        return f"{obj.client.name} {obj.client.lastname}"

    client_name_lastname.short_description = "Nombre y apellidos"
    client_name_lastname.allow_tags = True

    def client_document_number(self, obj):
        return obj.client.document_number

    client_document_number.short_description = "N⁰ Documento"
    client_document_number.allow_tags = True

    def client_telephone(self, obj):
        return obj.client.telephone

    client_telephone.short_description = "Telefono"
    client_telephone.allow_tags = True

    def client_city(self, obj):
        return obj.client.city

    client_city.short_description = "Ciudad"
    client_city.allow_tags = True

    def client_seller(self, obj):
        return obj.client.seller.id

    client_seller.short_description = "Vendedor"
    client_seller.allow_tags = True

    def client_payments(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/{obj.client.id}/change/#pagos-tab" class="raphael--edit"/>'
        )

    client_payments.short_description = "Abonos"
    client_payments.allow_tags = True

    def calculate_client_balance(self, obj):
        payments = models.Payment.objects.filter(client=obj.client)

        payment_balance = 0

        for payment in payments:
            payment_balance += payment.amount
        return payment_balance

    def payment_balance(self, obj):
        payment_balance = self.calculate_client_balance(obj)
        return f"${payment_balance:,.0f}".replace(",", ".")

    payment_balance.short_description = "Abonado"
    payment_balance.allow_tags = True

    def amount_to_pay(self, obj: models.TicketPendingPurchase):
        payment_balance = self.calculate_client_balance(obj)
        price_ticket = obj.ticket.lottery.price_per_ticket
        total_to_pay = price_ticket - payment_balance
        return f"${total_to_pay:,.0f}".replace(",", ".")

    amount_to_pay.short_description = "Saldo"
    amount_to_pay.allow_tags = True

    def bills_button(self, obj):

        dropdownBillsSelectorHTML = f"""
        <div class="client-bills-dropdown" style="position: relative; display: inline-block;">
            <div class="client-bills-dropdown-button solar--bill-list-linear" style="padding: 1rem;" onclick="toggleDropdown('dropdown-{obj.id}')">
            </div>
            <div id="dropdown-{obj.id}" class="client-bills-dropdown-content" style="display: none; position: fixed; background-color: #f9f9f9; min-width: 160px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); z-index: 1; border-radius: 5px;">
                <div onclick="getClientBill({obj.client.id}, 1)" class="client-bills-dropdown-item">Factura Bono 1</div>
                <div onclick="getClientBill({obj.client.id}, 2)" class="client-bills-dropdown-item">Factura Bono 2</div>
                <div onclick="getClientBill({obj.client.id}, 3)" class="client-bills-dropdown-item">Factura Bono 3</div>
                <div onclick="getClientBill({obj.client.id}, 4)" class="client-bills-dropdown-item">Factura Pago Total</div>
            </div>
        </div>
        """

        return format_html(dropdownBillsSelectorHTML)

    bills_button.short_description = "Facturas"
    bills_button.allow_tags = True

    def verify_purchase(self, obj):
        return format_html(
            f"""
            <div style="display: flex; width: 100%; justify-content: center; gap: 4px;">
                <div class="admin-table-button material-symbols--check" onclick="verifyPurchase({obj.client.id})"></div>
                <div class="admin-table-button material-symbols--close" onclick="declineTicket({obj.client.id})" ></div>
            </div>
            """
        )

    verify_purchase.short_description = "Aprobar / Declinar"
    verify_purchase.allow_tags = True

    def client_whatsapp(self, obj):
        return format_html(
            f"""
            <a href="https://wa.me/{obj.client.whatsapp}" target="_blank" class="logos--whatsapp-icon"></a>
            """
        )

    client_whatsapp.short_description = "Whatsapp"
    client_whatsapp.allow_tags = True

    def ticket_png(self, obj):
        return format_html(
            f"""
            <div onclick="getTicketPng({obj.client.id})" style="border: 0px;" class="admin-table-button bxs--file-png"></div>
            """
        )

    ticket_png.short_description = "PNG Boleta"
    ticket_png.allow_tags = True

    def edit_button(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/clientinfo/{obj.client.id}/change" class="wpf--edit"/>'
        )

    edit_button.short_description = "Editar"
    edit_button.allow_tags = True

    def is_numeric_search(self, search_term):
        """Check if the search term consists only of digits."""
        return search_term.isdigit()

    def search_by_number(self, queryset, search_number):
        """Search by ticket number or document number."""
        return queryset.filter(
            Q(ticket__number=search_number) |
            Q(client__document_number=search_number)
        )

    def search_by_name(self, queryset, search_terms):
        """Search by name and lastname."""
        if len(search_terms) > 1:
            # If there are multiple search terms, search across name and lastname
            query = Q()
            for term in search_terms:
                query &= Q(client__name__icontains=term) | Q(
                    client__lastname__icontains=term)
            return queryset.filter(query)
        else:
            # Standard search if there is only one term
            search_term = search_terms[0]
            return queryset.filter(
                Q(client__name__icontains=search_term) |
                Q(client__lastname__icontains=search_term) |
                Q(ticket__number__icontains=search_term) |
                Q(client__document_number__icontains=search_term) |
                Q(purchase_reference__icontains=search_term)
            )

    def get_search_results(self, request, queryset, search_term):
        """Customize search behavior in the admin."""
        # Check if the search term is empty
        if not search_term.strip():
            # Return the unfiltered queryset if the search term is empty
            return queryset, False

        if self.is_numeric_search(search_term):
            # Parse the search term to an integer for numeric search
            search_number = int(search_term)
            queryset = self.search_by_number(queryset, search_number)
        else:
            # Split the search term into words for name-based search
            search_terms = search_term.split()
            queryset = self.search_by_name(queryset, search_terms)

        # Return the search results along with a boolean indicating if there were more results
        return queryset, False

    def get_list_display_links(self, request, list_display):
        """
        Override to prevent the first column from being a link.
        """
        # Prevent the first column ('ticket') from being a link
        return None

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        """
        Method to filter the queryset based on the authenticated user.

        Args:
            request (HttpRequest): The request object.

        Returns:
            QuerySet: Filtered queryset based on user permissions.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all records
        else:
            # Filter by seller corresponding to the client
            return qs.filter(client__seller=request.user)

    class Media:
        js = ("js/pending_purchase.js", "js/custom_client_bills.js",
              "js/custom_ticket_png.js", "js/custom_decline_ticket.js", "js/custom_delete_buttons.js")


@admin.register(models.TicketPendingPurchase)
class TicketPendingPurchase(BaseAdminTable):
    ...


@admin.register(models.TicketReserved)
class TicketReservedAdmin(BaseAdminTable):
    form = TicketReservedForm

    def has_add_permission(self, request):
        return True

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a customized form based on the user's permissions.

        Args:
            request (HttpRequest): The request object.
            obj (ClientInfo, optional): The object being edited, if any.
            **kwargs: Additional keyword arguments.

        Returns:
            django.forms.ModelForm: Customized form object.
        """

        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user

        if not request.user.is_superuser:
            form.base_fields["seller"].widget = forms.HiddenInput()

        form.base_fields["seller"].initial = request.user

        lottery_to_buy = (
            request.GET.get("lottery_to_buy")
            or request.POST.get("lottery_to_buy")
            or (obj and obj.client.lottery_to_buy.id)
        )

        form.base_fields['lottery_to_buy'].initial = lottery_to_buy

        ticket = (obj and obj.client.ticket_number.id)

        self.filter_ticket_numbers_by_assignment(
            form, lottery_to_buy, request.user, obj and obj.client.ticket_number
        )

        if ticket:
            form.base_fields["ticket"].initial = ticket

        return form

    def get_seller_ticket_assignments(self, current_user, initial_lottery_to_buy):
        return models.TicketAssignment.objects.filter(
            assigned_to=current_user, lottery=initial_lottery_to_buy
        )

    def get_ticket_number_ranges(self, seller_ticket_assignments):
        ticket_number_ranges = []
        for assignment in seller_ticket_assignments:
            if assignment.start_number is not None and assignment.end_number is not None:
                ticket_number_ranges.extend(range(
                    assignment.start_number,
                    assignment.end_number + 1,
                ))
        return ticket_number_ranges

    def get_individual_ticket_numbers(self, seller_ticket_assignments):
        individual_ticket_numbers = []
        for assignment in seller_ticket_assignments:
            individual_ticket_numbers.extend(
                list(assignment.individual_tickets.values_list('number', flat=True)))
        return individual_ticket_numbers

    def combine_ticket_numbers(self, ticket_number_ranges, individual_ticket_numbers):
        return set(ticket_number_ranges) | set(individual_ticket_numbers)

    def filter_ticket_numbers_by_assignment(
        self,
        form,
        lottery_to_buy,
        current_user,
        change_ticket_number: models.Ticket = None,
    ):
        """
        Filters ticket numbers based on seller's assignments and lottery.

        Args:
            form (Form): The form object.
            lottery_to_buy (int): ID of the lottery to buy.
            current_user (User): The current user (seller).
            change_ticket_number (Ticket, optional): The ticket being changed.

        Returns:
            None
        """
        ticket_numbers = models.Ticket.objects.none()

        if lottery_to_buy and current_user:
            seller_ticket_assignments = self.get_seller_ticket_assignments(
                current_user=current_user, initial_lottery_to_buy=lottery_to_buy
            )

            if not current_user.is_superuser and (
                not seller_ticket_assignments or len(
                    seller_ticket_assignments) <= 0
            ):
                form.base_fields["ticket"].queryset = ticket_numbers
                return

            extra_ticket_conditions_info = {}
            extra_ticket_conditions_info_purchased = {}

            if change_ticket_number:
                extra_ticket_conditions_info["number"] = change_ticket_number.number
                extra_ticket_conditions_info["state"] = constants.TicketState.RESERVED

                extra_ticket_conditions_info_purchased["number"] = (
                    change_ticket_number.number
                )
                extra_ticket_conditions_info_purchased["state"] = (
                    constants.TicketState.PURCHASED
                )

            ticket_numbers_conditions = [
                {
                    "lottery": lottery_to_buy,
                    "state": constants.TicketState.AVAILABLE,
                },
                extra_ticket_conditions_info,
                extra_ticket_conditions_info_purchased,
            ]

            # add filter by ticket ranges if user is a seller
            if not current_user.is_superuser:
                ticket_number_ranges = self.get_ticket_number_ranges(
                    seller_ticket_assignments)
                individual_ticket_numbers = self.get_individual_ticket_numbers(
                    seller_ticket_assignments)
                all_ticket_numbers = self.combine_ticket_numbers(
                    ticket_number_ranges, individual_ticket_numbers)

                ticket_numbers_conditions[0]["number__in"] = all_ticket_numbers

            ticket_numbers_complex_filter = build_complex_filter(
                ticket_numbers_conditions
            )

            ticket_numbers = models.Ticket.objects.filter(
                ticket_numbers_complex_filter)

        form.base_fields["ticket"].queryset = ticket_numbers

        return ticket_numbers


@admin.register(models.TicketPurchased)
class TicketPurchasedAdmin(BaseAdminTable):
    def get_list_display(self, request):
        # Get the default list display from the base class
        list_display = super().get_list_display(request)
        # Remove 'verify_purchase' from the list if it exists
        return [item for item in list_display if item != 'verify_purchase']


@admin.register(models.TicketWithPayment)
class TicketWithPaymentAdmin(BaseAdminTable):
    """Admin view filtered by clients with existing payments."""
    
    def verify_purchase(self, obj):
        return format_html(
            f"""
            <div style="display: flex; width: 100%; justify-content: center; gap: 4px;">
                <div class="admin-table-button material-symbols--close" onclick="declineTicket({obj.client.id})" ></div>
            </div>
            """
        )
    
    verify_purchase.short_description = "Declinar"
    verify_purchase.allow_tags = True

    def get_queryset(self, request):
        """Override to filter TicketReserved by clients who have existing payments."""
        # Fetch the TicketReserved model queryset
        queryset = models.TicketReserved.objects.all()
        # Get client IDs with existing payments
        client_ids_with_payments = models.Payment.objects.values_list(
            'client_id', flat=True).distinct()
        # Filter TicketReserved where the client is in the list of client IDs with payments
        return queryset.filter(client_id__in=client_ids_with_payments)


@admin.register(models.Whatsapp)
class WhatsappAdmin(admin.ModelAdmin):
    """Admin view for managing Whatsapp, allowing only one instance."""

    list_display = ("whatsapp", "edit_button")

    def edit_button(self, obj):
        return format_html(
            f'<a href="/admin/djangopwa/whatsapp/{obj.id}/change" class="wpf--edit"/>'
        )

    edit_button.short_description = "Editar"
    edit_button.allow_tags = True

    def get_queryset(self, request):
        """Override to ensure only one instance is shown."""
        queryset = super().get_queryset(request)
        # Return only the single instance if it exists
        if queryset.count() > 1:
            raise forms.ValidationError(
                "There should be only one instance of Whatsapp.")
        return queryset

    def has_add_permission(self, request):
        """Prevent adding more than one instance."""
        # Allow adding only if no instances exist
        if models.Whatsapp.objects.exists():
            return False
        return super().has_add_permission(request)

    def save_model(self, request, obj, form, change):
        """Prevent saving more than one instance."""
        if obj.pk is None and models.Whatsapp.objects.exists():
            raise forms.ValidationError(
                "Only one instance of Whatsapp can be created.")
        super().save_model(request, obj, form, change)


admin.site.register(models.BankAccount)
admin.site.register(models.PaymentMethod)
