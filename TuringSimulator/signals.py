from django.db.models.signals import post_delete, pre_save, post_save, post_init
from django.dispatch import receiver
from django.db import models
from .models import TuringMachineDB, ExampleDB


# ****************** MANAGING UNUSED FILES ********************
def delete_file_if_unused(model, instance, field, instance_file_field):
    if 'default' not in instance_file_field.name:
        dynamic_field = {}
        dynamic_field[field.name] = instance_file_field.name
        other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
        if not other_refs_exist:
            instance_file_field.delete(False)


@receiver(pre_save)
def delete_files_when_file_changed(sender, instance, **kwargs):
    # Don't run on initial save
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field,models.FileField):
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # We are probably in a transaction and the PK is just temporary
                # Don't worry about deleting attachments if they aren't actually saved yet.
                return
            instance_in_db_file_field = getattr(instance_in_db,field.name)
            instance_file_field = getattr(instance,field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(sender,instance,field,instance_in_db_file_field)


@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)

# ****************** END MANAGING UNUSED FILES ********************


@receiver(post_init, sender=TuringMachineDB)
def machine_preparations(sender, instance, created, **kwargs):
    print("machine_preparations")
    if created:
        print("new machine")
        instance.initial_alphabet = instance.alphabet
        instance.initial_number_of_states = instance.number_of_states
        alph = str(instance.alphabet).split(',')

        instance.prepare_excel()
    else:
        print("updated machine")
        # checking if during update user changed alphabet or nr of states
        # if yes, then we need to prepare brand new blank excel of instructions
        if instance.initial_alphabet != instance.alphabet or instance.initial_number_of_states != instance.number_of_states:
            instance.prepare_excel()
            instance.initial_number_of_states = instance.number_of_states
            instance.initial_alphabet = instance.alphabet


@receiver(post_init, sender=ExampleDB)
def example_preparations(sender, instance, **kwargs):
    print("example_preparations")
    instance.prepare_instruction_steps_file()