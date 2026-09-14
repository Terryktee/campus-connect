from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Category, Institution


INSTITUTIONS = (
    ("University of Zimbabwe", "UZ", "Harare"),
    ("National University of Science and Technology", "NUST", "Bulawayo"),
    ("Midlands State University", "MSU", "Gweru"),
    ("Catholic University of Zimbabwe", "CUZ", "Harare"),
    ("Chinhoyi University of Technology", "CUT", "Chinhoyi"),
    ("Harare Institute of Technology", "HIT", "Harare"),
    ("Africa University", "AU", "Mutare"),
)
CATEGORIES = (
    "University News",
    "Student Opportunities",
    "Internships",
    "Scholarships",
    "Tech Events",
    "Student Businesses",
    "Coding",
    "Careers",
    "Campus Life",
    "Orientation",
    "Entrepreneurship",
    "Technology",
)


class Command(BaseCommand):
    help = "Create the initial institutions and categories without duplicates."

    def handle(self, *args, **options):
        for name, short_code, city in INSTITUTIONS:
            Institution.objects.update_or_create(
                short_code=short_code,
                defaults={"name": name, "city": city},
            )
        for name in CATEGORIES:
            Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)},
            )
        self.stdout.write(self.style.SUCCESS("Seed data is up to date."))
