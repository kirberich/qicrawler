import random
import time

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache
from django.utils import simplejson as json
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

import _qi as qi
from core.models import Speaker, Episode, Quote

def main(request):
    return _quote(request, None)

@cache_page(60*60*24)
def quote(request, quote_id):
    return _quote(request, quote_id)

def _quote(request, quote_id):
    to_search = request.GET.get('search') or request.POST.get('search')
    response = request.GET.get('response', 'html')

    if quote_id:
        try:
            quote = Quote.objects.get(pk=quote_id)
        except:
            quote = None
    elif to_search:
        search_list = to_search.split(" ")
        quotes = Quote.objects.all()
        for term in search_list:
            if term.startswith("-who:"):
                quotes = quotes.exclude(speaker__full_name__icontains=term[5:])
            elif term.startswith("who:"):
                quotes = quotes.filter(speaker__full_name__icontains=term[4:])
            elif term.startswith("-"):
                quotes = quotes.exclude(text__icontains=term[1:])
            else:
                quotes = quotes.filter(text__icontains=term)
        quote = quotes[random.randint(0, len(quotes)-1)] if len(quotes) else None
    else:
        num_quotes = cache.get('num_quotes')
        if not num_quotes:
            num_quotes = Quote.objects.all().count()
            cache.set('num_quotes', num_quotes, 60*60*24*7)
        quote = Quote.objects.all()[random.randint(0, num_quotes-1)]

    subs = {
        'quote': quote,
        'to_search': to_search if to_search else '',
        'context_before': quote.get_previous(3) if quote else [],
        'context_after': quote.get_next(3) if quote else [],
        'forfeit': quote.speaker.name.startswith("Forfeit") if quote else False
    }

    if response == 'raw':
        subs['raw'] = True
        return render_to_response('quote.html', subs, context_instance=RequestContext(request))
    elif response == 'json':
        data = json.dumps({
            'quote_text': quote.text.strip(),
            'speaker': quote.speaker.name,
            'speaker_full': quote.speaker.full_name,
            'next': 'http://qiquotes.com/%s' % quote.next.pk,
            'previous': 'http://qiquotes.com/%s' % quote.previous.pk,
            'link': 'http://qiquotes.com/%s' % quote.pk
        })
        return HttpResponse(data, mimetype='application/json')
    else:
        return render_to_response('main.html', subs, context_instance=RequestContext(request))


def init(request):
    reset = request.GET.get("reset") == "true"
    episodes = qi.load(debug=True)
    added = []
    for episode_name, episode_dict in episodes.items():
        episode, created = Episode.objects.get_or_create(name=episode_name)
        # If reset is true, delete existing quotes for existing episode, otherwise ignore existing episodes.
        if created:
            episode.description = episode_dict['description']
            episode.save()
        elif reset:
            episode.quote_set.all().delete()
        else:
            print "ignoring episode %s" % episode
            continue

        print episode
        if not 'transcript' in episode_dict:
            continue

        speaker_names = episode.speaker_names()
        number_lines = len(episode_dict['transcript'])
        previous_quote = None
        for line in range(0, number_lines):
            print line
            speaker_name, text = episode_dict['transcript'][line].split(":", 1)
            speaker = Speaker.objects.get_or_create(name=speaker_name, full_name=episode.full_speaker_name(speaker_name, speaker_names) or "")[0]

            quote = Quote(episode=episode, speaker=speaker, text=text)
            if previous_quote:
                quote.previous = previous_quote
                quote.save()
                previous_quote.next = quote
                previous_quote.save()
            else:
                quote.save()
            previous_quote = quote
        added.append(episode)
    return HttpResponse("ok, added episodes: %s" % added)


def stats(request):
    subs = {
        'episodes': Episode.objects.all(),
        'speaker': Speaker.objects.all(),
        'quote_count': Quote.objects.all().count(),
        'request': request,
    }
    if 'episode' in request.GET:
        subs['episode'] = Episode.objects.get(pk=request.GET.get('episode'))
    return render_to_response('stats.html', subs, context_instance=RequestContext(request))


@login_required
@require_POST
def quote_delete(request, quote_id):
    q = Quote.objects.get(pk=quote_id)
    if q.next:
        next = q.next
        next.previous = q.previous
        next.save()
    if q.previous:
        previous = q.previous 
        previous.next = q.next
        previous.save()
    q.delete()
    return HttpResponse("deleted")


@login_required
@require_POST
def quote_edit(request, quote_id):
    text = request.POST['text']
    q = Quote.objects.get(pk=quote_id)
    q.text = text 
    q.save()
    return HttpResponse("updated")


def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render_to_response('login.html', {'error': "Balls."}, context_instance = RequestContext(request))
    else:
        return render_to_response('login.html', {"user": request.user}, context_instance = RequestContext(request))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
