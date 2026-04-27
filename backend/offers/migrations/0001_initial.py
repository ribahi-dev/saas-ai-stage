import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternshipOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titre du poste')),
                ('description', models.TextField(verbose_name='Description detaillee')),
                ('required_skills', models.TextField(
                    help_text='Texte libre analyse par TF-IDF. Ex: Python Django REST API Git Docker',
                    verbose_name='Competences requises',
                )),
                ('location', models.CharField(blank=True, max_length=200, null=True, verbose_name='Lieu (ville / remote)')),
                ('duration_months', models.PositiveSmallIntegerField(
                    blank=True,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)],
                    verbose_name='Duree (mois)',
                )),
                ('is_paid', models.BooleanField(default=False, verbose_name='Stage remunere ?')),
                ('salary', models.DecimalField(
                    blank=True,
                    decimal_places=2,
                    max_digits=8,
                    null=True,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Remuneration mensuelle (MAD)',
                )),
                ('status', models.CharField(
                    choices=[('active', 'Active'), ('paused', 'En pause'), ('archived', 'Archivee')],
                    default='active',
                    max_length=10,
                    verbose_name='Statut',
                )),
                ('deadline', models.DateField(blank=True, null=True, verbose_name='Date limite de candidature')),
                ('offer_vector_json', models.TextField(blank=True, null=True, verbose_name='Vecteur TF-IDF (JSON)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='offers',
                    to='users.companyprofile',
                    verbose_name='Entreprise',
                )),
            ],
            options={
                'verbose_name': 'Offre de Stage',
                'verbose_name_plural': 'Offres de Stage',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_letter', models.TextField(blank=True, null=True, verbose_name='Lettre de motivation')),
                ('status', models.CharField(
                    choices=[('pending', 'En attente'), ('accepted', 'Acceptee'), ('rejected', 'Refusee'), ('withdrawn', 'Retiree')],
                    default='pending',
                    max_length=10,
                    verbose_name='Statut',
                )),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('offer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='applications',
                    to='offers.internshipoffer',
                    verbose_name='Offre',
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='applications',
                    to='users.studentprofile',
                    verbose_name='Etudiant',
                )),
            ],
            options={
                'verbose_name': 'Candidature',
                'verbose_name_plural': 'Candidatures',
                'ordering': ['-applied_at'],
                'unique_together': {('student', 'offer')},
            },
        ),
    ]
