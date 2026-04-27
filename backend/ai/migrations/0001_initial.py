import django.db.models.deletion
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('offers', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(
                    default=0.0,
                    validators=[
                        django.core.validators.MinValueValidator(0.0),
                        django.core.validators.MaxValueValidator(1.0),
                    ],
                    verbose_name='Score de similarite',
                )),
                ('computed_at', models.DateTimeField(auto_now=True, verbose_name='Calcule le')),
                ('offer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recommendations',
                    to='offers.internshipoffer',
                    verbose_name='Offre',
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='recommendations',
                    to='users.studentprofile',
                    verbose_name='Etudiant',
                )),
            ],
            options={
                'verbose_name': 'Recommandation',
                'verbose_name_plural': 'Recommandations',
                'ordering': ['-score'],
                'unique_together': {('student', 'offer')},
            },
        ),
    ]
