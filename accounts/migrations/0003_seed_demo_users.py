from django.db import migrations


DEMO_USERS = [
    {
        "email": "admin@farmhub.test",
        "username": "farmhub_admin",
        "full_name": "FarmHub Admin",
        "role": "admin",
        "is_staff": True,
        "is_superuser": True,
        "password": "pbkdf2_sha256$1000000$Ovjt74pB5O0wCJe6YD4fm3$OecnMVQETUH0xK3lLRFVtbG9IxT1x09Xgb0UqREsNpg=",
    },
    {
        "email": "farmer@farmhub.test",
        "username": "farmhub_farmer",
        "full_name": "FarmHub Farmer",
        "role": "farmer",
        "is_staff": False,
        "is_superuser": False,
        "password": "pbkdf2_sha256$1000000$4E4lu37OuOn9109cKt4wLH$Qp0JHVQ6VfHaj3KU9ExvXw8thSg/i6VrXlbOdcC3sGU=",
    },
]


def seed_demo_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    EmailVerification = apps.get_model("accounts", "EmailVerification")
    FarmerProfile = apps.get_model("accounts", "FarmerProfile")

    for data in DEMO_USERS:
        user = (
            User.objects.filter(email=data["email"]).first()
            or User.objects.filter(username=data["username"]).first()
        )
        if user is None:
            user = User(email=data["email"], username=data["username"])

        user.email = data["email"]
        user.username = data["username"]
        user.full_name = data["full_name"]
        user.role = data["role"]
        user.is_staff = data["is_staff"]
        user.is_superuser = data["is_superuser"]
        user.is_active = True
        user.is_verified = True
        user.password = data["password"]
        user.save()

        EmailVerification.objects.update_or_create(
            user=user,
            defaults={
                "is_verified": True,
                "otp": None,
                "otp_expires_at": None,
                "otp_attempts": 0,
            },
        )

        if data["role"] == "farmer":
            FarmerProfile.objects.get_or_create(user=user)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_emailverification_otp_fields"),
    ]

    operations = [
        migrations.RunPython(seed_demo_users, migrations.RunPython.noop),
    ]
