ps aux | grep qa_rest_manage_new.py | grep -v grep | awk '{print $2}'| xargs kill -9
