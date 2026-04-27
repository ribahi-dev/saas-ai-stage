import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('student', 'Etudiant'), ('company', 'Entreprise'), ('admin', 'Administrateur')], default='student', max_length=10, verbose_name='Role')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Utilisateur',
                'verbose_name_plural': 'Utilisateurs',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('linkedin_url', models.URLField(blank=True, null=True)),
                ('university', models.CharField(blank=True, max_length=200, null=True, verbose_name='Universite / Ecole')),
                ('field_of_study', models.CharField(blank=True, max_length=200, null=True, verbose_name='Filiere')),
                ('graduation_year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Annee de diplome')),
                ('cv_file', models.FileField(blank=True, null=True, upload_to='cvs/', verbose_name='CV (PDF)')),
                ('cv_text_extracted', models.TextField(blank=True, null=True, verbose_name='Texte extrait du CV')),
                ('cv_vector_json', models.TextField(blank=True, null=True, verbose_name='Vecteur TF-IDF (JSON)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil Etudiant',
                'verbose_name_plural': 'Profils Etudiants',
            },
        ),
        migrations.CreateModel(
            name='CompanyProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200, verbose_name="Nom de l'entreprise")),
                ('description', models.TextField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True, verbose_name="Secteur d'activite")),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ville')),
                ('country', models.CharField(default='Maroc', max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(limit_choices_to={'role': 'company'}, on_delete=django.db.models.deletion.CASCADE, related_name='company_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profil Entreprise',
                'verbose_name_plural': 'Profils Entreprises',
            },
        ),
    ]
