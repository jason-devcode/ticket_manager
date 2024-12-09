from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from . import models
from typing import TypeVar, Type

T = TypeVar('T')

def add_permission(group: Group, model: Type[T], perm_type: str) -> None:
    """
    Adds a specific permission (view, add, change, delete) for the specified model to the given group.

    Args:
        group (Group): The group to which the permission will be added.
        model (Type[T]): The model class for which the permission is added.
        perm_type (str): The type of permission ('view', 'add', 'change', 'delete').
    """
    # Get the content type of the model
    content_type = ContentType.objects.get_for_model(model)

    # Construct the codename for the permission
    codename = f'{perm_type}_{model._meta.model_name}'

    # Ensure that the permission exists for the model
    permission = Permission.objects.get(codename=codename, content_type=content_type)

    # Assign the permission to the group if it doesn't already have it
    if not group.permissions.filter(id=permission.id).exists():
        group.permissions.add(permission)

def add_view_model_permission(group: Group, model: Type[T]) -> None:
    add_permission(group, model, 'view')

def add_write_model_permission(group: Group, model: Type[T]) -> None:
    add_permission(group, model, 'change')

def add_add_model_permission(group: Group, model: Type[T]) -> None:
    add_permission(group, model, 'add')

def add_delete_model_permission(group: Group, model: Type[T]) -> None:
    add_permission(group, model, 'delete')

def add_model_general_permissions(group: Group, model: Type[T]) -> None:
    add_view_model_permission(group, model)
    add_write_model_permission(group, model)
    add_add_model_permission(group, model)
    add_delete_model_permission(group, model)

def create_seller_group_with_permissions(**kwargs) -> Group:
    
    # Get or create the group
    seller_group, created = Group.objects.get_or_create(name='Vendedores')
    
    # Clear all permissions
    seller_group.permissions.clear()
    
    # Add specific permissions to the group
    add_model_general_permissions(seller_group,models.ClientInfo)
    add_model_general_permissions(seller_group,models.Payment)
    add_model_general_permissions(seller_group,models.TicketReserved)
    add_model_general_permissions(seller_group,models.TicketPendingPurchase)
    add_model_general_permissions(seller_group,models.TicketWithPayment)
    add_model_general_permissions(seller_group,models.TicketPurchased)

    return seller_group
