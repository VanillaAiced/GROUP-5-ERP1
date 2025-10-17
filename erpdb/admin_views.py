from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.apps import apps
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

def is_staff(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_staff)
def custom_admin_home(request):
    """Custom admin dashboard home"""
    # Get all registered apps and models
    app_list = []

    # Define apps to include in admin
    admin_apps = ['erpdb', 'Email', 'authentication', 'auth']

    for app_config in apps.get_app_configs():
        if app_config.label in admin_apps:
            app_dict = {
                'name': app_config.verbose_name,
                'app_label': app_config.label,
                'models': []
            }

            for model in app_config.get_models():
                model_dict = {
                    'name': model._meta.verbose_name_plural.title(),
                    'object_name': model._meta.object_name,
                    'model_name': model._meta.model_name,
                    'count': model.objects.count(),
                }
                app_dict['models'].append(model_dict)

            if app_dict['models']:
                app_list.append(app_dict)

    context = {
        'app_list': app_list,
        'title': 'Lite WORK Admin',
    }
    return render(request, 'admin/custom_admin_home.html', context)

@login_required
@user_passes_test(is_staff)
def custom_admin_model_list(request, app_label, model_name):
    """List all objects of a model"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, f"Model {app_label}.{model_name} not found")
        return redirect('erp:custom_admin_home')

    # Get all objects
    queryset = model.objects.all()

    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        # Try to search in common fields
        search_fields = []
        for field in model._meta.fields:
            if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']:
                search_fields.append(f"{field.name}__icontains")

        if search_fields:
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{field: search_query})
            queryset = queryset.filter(q_objects)

    # Pagination
    paginator = Paginator(queryset, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get field names for table headers
    fields = [f for f in model._meta.fields if not f.name == 'password']

    context = {
        'model': model,
        'model_name': model._meta.model_name,
        'app_label': app_label,
        'verbose_name': model._meta.verbose_name,
        'verbose_name_plural': model._meta.verbose_name_plural,
        'objects': page_obj,
        'fields': fields,
        'search_query': search_query,
        'title': f'{model._meta.verbose_name_plural.title()} - Admin',
    }
    return render(request, 'admin/custom_admin_model_list.html', context)

@login_required
@user_passes_test(is_staff)
def custom_admin_model_add(request, app_label, model_name):
    """Add new object"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, f"Model {app_label}.{model_name} not found")
        return redirect('erp:custom_admin_home')

    if request.method == 'POST':
        try:
            # Create new instance
            instance = model()

            # Set field values from POST data
            for field in model._meta.fields:
                if field.name in request.POST and not field.auto_created:
                    field_value = request.POST.get(field.name)
                    if field_value:
                        setattr(instance, field.name, field_value)

            instance.save()
            messages.success(request, f'{model._meta.verbose_name} created successfully!')
            return redirect('erp:custom_admin_model_list', app_label=app_label, model_name=model_name)
        except Exception as e:
            messages.error(request, f'Error creating object: {str(e)}')

    fields = [f for f in model._meta.fields if not f.auto_created and f.name != 'password']

    context = {
        'model': model,
        'model_name': model._meta.model_name,
        'app_label': app_label,
        'verbose_name': model._meta.verbose_name,
        'fields': fields,
        'title': f'Add {model._meta.verbose_name} - Admin',
    }
    return render(request, 'admin/custom_admin_model_form.html', context)

@login_required
@user_passes_test(is_staff)
def custom_admin_model_edit(request, app_label, model_name, object_id):
    """Edit existing object"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, f"Model {app_label}.{model_name} not found")
        return redirect('erp:custom_admin_home')

    instance = get_object_or_404(model, pk=object_id)

    if request.method == 'POST':
        try:
            # Update field values from POST data
            for field in model._meta.fields:
                if field.name in request.POST and not field.auto_created and field.name != 'id':
                    field_value = request.POST.get(field.name)
                    if field_value or field.null:
                        setattr(instance, field.name, field_value)

            instance.save()
            messages.success(request, f'{model._meta.verbose_name} updated successfully!')
            return redirect('erp:custom_admin_model_list', app_label=app_label, model_name=model_name)
        except Exception as e:
            messages.error(request, f'Error updating object: {str(e)}')

    fields = [f for f in model._meta.fields if not f.auto_created and f.name != 'password']

    context = {
        'model': model,
        'model_name': model._meta.model_name,
        'app_label': app_label,
        'verbose_name': model._meta.verbose_name,
        'instance': instance,
        'fields': fields,
        'title': f'Edit {model._meta.verbose_name} - Admin',
    }
    return render(request, 'admin/custom_admin_model_form.html', context)

@login_required
@user_passes_test(is_staff)
def custom_admin_model_delete(request, app_label, model_name, object_id):
    """Delete object"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        messages.error(request, f"Model {app_label}.{model_name} not found")
        return redirect('erp:custom_admin_home')

    instance = get_object_or_404(model, pk=object_id)

    if request.method == 'POST':
        try:
            instance.delete()
            messages.success(request, f'{model._meta.verbose_name} deleted successfully!')
            return redirect('erp:custom_admin_model_list', app_label=app_label, model_name=model_name)
        except Exception as e:
            messages.error(request, f'Error deleting object: {str(e)}')
            return redirect('erp:custom_admin_model_list', app_label=app_label, model_name=model_name)

    context = {
        'model': model,
        'instance': instance,
        'app_label': app_label,
        'model_name': model_name,
        'verbose_name': model._meta.verbose_name,
        'title': f'Delete {model._meta.verbose_name} - Admin',
    }
    return render(request, 'admin/custom_admin_delete.html', context)

