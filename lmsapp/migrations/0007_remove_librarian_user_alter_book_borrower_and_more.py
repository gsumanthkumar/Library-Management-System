# Generated by Django 4.1 on 2022-09-14 11:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lmsapp', '0006_alter_library_librarian'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='librarian',
            name='user',
        ),
        migrations.AlterField(
            model_name='book',
            name='borrower',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='library',
            name='librarian',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='borrower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_borrower', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='lender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_lender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Borrower',
        ),
        migrations.DeleteModel(
            name='Librarian',
        ),
    ]
