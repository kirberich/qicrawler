import random
import time

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.cache import cache

import qi
from core.models import Speaker, Episode, Quote

def main(request):
	num_quotes = cache.get('num_quotes')
	if not num_quotes:
		num_quotes = Quote.objects.all().count()
		cache.set('num_quotes', num_quotes, 60*10)

	quote = Quote.objects.all()[random.randint(0, num_quotes)]
	return render_to_response('main.html', {'quote':quote}, context_instance=RequestContext(request))


def init(request):
	episodes = qi.parse_episodes()
	for episode_name, episode_dict in episodes.items():
		episode, created = Episode.objects.get_or_create(name=episode_name)
		if created:
			episode.description = episode_dict['description']
			episode.save()
		else:
			episode.quote_set.all().delete()

		if not 'transcript' in episode_dict:
			continue
		number_lines = len(episode_dict['transcript'])
		previous_quote = None
		for line in range(0, number_lines):
			speaker_name, text = episode_dict['transcript'][line].split(":", 1)
			speaker = Speaker.objects.get_or_create(name=speaker_name)[0]

			quote = Quote(episode=episode, speaker=speaker, text=text)
			if previous_quote:
				quote.previous = previous_quote
				previous_quote.next = quote
				previous_quote.save()
			quote.save()
			previous_quote = quote
	return HttpResponse("ok")
