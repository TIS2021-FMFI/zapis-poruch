"""
Create permission groups
Create permissions to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError

# GROUPS = ['developers', 'devops', 'qa', 'operators', 'product']
# MODELS = ['video', 'article', 'license', 'list', 'page', 'client']
# PERMISSIONS = ['view', ]  # For now only view permission by default for all, others include add, delete, change

GROUPS = {
    'full access': {
        'add':              ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'change':           ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'delete':           ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'view':             ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'schvalenie chyby': True,
        'grafy': True,
    },
    'viewer': {
        'add':      [],
        'change':   [],
        'delete':   [],
        'view':     ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'approve':  False,
        'grafy': False,
    },
    'deleter': {
        'add':      [],
        'change':   [],
        'delete':   ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'view':     ['chyba', 'druh chyby', 'miesto na linke', 'sposobena kym', 'typ chyby', 'typ revizie'],
        'approve':  False,
        'grafy': False,
    },
}

def custom_permission(group, name, codename, model):
    print(f"Creating {name}")

    try:
        model_add_perm = Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        logging.warning(f"Permission not found with name '{name}', generating...")

        content_type = ContentType.objects.get(app_label='linka', model=model)
        model_add_perm = Permission.objects.create(codename=codename,
                                                   name=name,
                                                   content_type=content_type)

    group.permissions.add(model_add_perm)


class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'

    def handle(self, *args, **options):
        for group in GROUPS:
            print(f"Creating group: {group}")
            new_group, created = Group.objects.get_or_create(name=group)
            new_group.permissions.clear()

            for permission in GROUPS[group]:
                if permission == 'schvalenie chyby' and GROUPS[group][permission]:
                    custom_permission(new_group, 'Can approve chyba', 'can_approve_chyba', 'chyba')
                    continue

                elif permission == 'grafy' and GROUPS[group][permission]:
                    custom_permission(new_group, 'Can view grafy', 'can_view_grafy', 'typchyby')
                    continue

                if permission in ('add', 'change', 'delete', 'view'):
                    for model in GROUPS[group][permission]:
                        name = f'Can {permission} {model}'
                        print(f"Creating {name}")

                        try:
                            model_add_perm = Permission.objects.get(name=name)
                        except Permission.DoesNotExist:
                            logging.warning(f"Permission not found with name '{name}'.")
                            continue

                        new_group.permissions.add(model_add_perm)

        print("Created default group and permissions.")
