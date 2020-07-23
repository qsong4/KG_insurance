import os, sys
import json
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

cur_dir = os.path.dirname( os.path.abspath(__file__)) or os.getcwd()
sys.path.append(cur_dir + '/../../QABot/DM/')
sessionID = "songqingyuantest"
history = ""
from bot_dm import dm
dm = dm()


    
## receive the post input data and process.
@csrf_exempt
def analyze(request):
    ctx ={}
    if 'user_say' in request.POST:
        ctx['input'] = in_text = request.POST['user_say'].strip()

        history = request.POST['answer'].strip()
        answer = json.dumps(dm.management(sessionID, in_text), ensure_ascii=False)
        history = history + "\n" + "sqy: " + in_text + "\n" + "PA_Bot: " + answer + "\n" + "*************************" + "\n"
        ctx['answer'] = history

    return render(request, "index.html", ctx)





