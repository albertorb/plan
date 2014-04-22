#!/Library/Frameworks/Python.framework/Versions/3.3/bin/python3-32
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ispp8.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
