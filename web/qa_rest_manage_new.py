#!/usr/bin/env python
import os
import sys
cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
#print '>>>cur_dir in manage.py:', cur_dir
#sys.path.append(cur_dir)
sys.path.append(cur_dir+'/../')

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qa_demo.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
