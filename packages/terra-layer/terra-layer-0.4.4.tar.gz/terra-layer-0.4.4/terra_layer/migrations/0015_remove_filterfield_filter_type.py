# Generated by Django 2.0.13 on 2019-06-25 09:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("terra_layer", "0014_filterfield_label")]

    operations = [migrations.RemoveField(model_name="filterfield", name="filter_type")]
