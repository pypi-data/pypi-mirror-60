# Generated by Django 2.2.6 on 2019-11-07 01:27

from django.db import migrations
from edc_reportable import MILLIMOLES_PER_LITER


def update_fasting_glucose(apps, schema_editor):
    SubjectScreening = apps.get_model("meta_screening", "SubjectScreening")
    for obj in SubjectScreening._default_manager.all():
        eligible = obj.eligible
        obj.converted_fasting_glucose = obj.fasting_glucose
        obj.fasting_glucose_units = MILLIMOLES_PER_LITER
        obj.save()
        obj.refresh_from_db()
        if obj.eligible != eligible:
            print(f"Eligibility has changed! See {obj.screening_identifier}")


class Migration(migrations.Migration):

    dependencies = [("meta_screening", "0011_auto_20191107_0342")]

    operations = [migrations.RunPython(update_fasting_glucose)]
