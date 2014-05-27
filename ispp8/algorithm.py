__author__ = 'Mike'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ispp8.settings")
from plan.models import OurUser

def show_tastes(user):
    for taste in user.tastes.all():
        print(taste.attribute_name, taste.attribute_value, taste.degree)


show_tastes(OurUser.objects.get(pk=2))