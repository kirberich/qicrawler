from django.db import models

class Speaker(models.Model):
	name = models.CharField(max_length=255)
	full_name = models.CharField(max_length=255, default="")

	def __repr__(self):
		return self.full_name or self.name
	__unicode__ = __repr__


class Episode(models.Model):
	name = models.CharField(max_length=10)
	description = models.CharField(max_length=255)


class Quote(models.Model):
	episode = models.ForeignKey(Episode)
	speaker = models.ForeignKey(Speaker)
	text = models.TextField()

	previous = models.ForeignKey('self', blank=True, null=True, related_name="next_set")
	next = models.ForeignKey('self', blank=True, null=True, related_name="previous_set")

	def __repr__(self):
		return "%s: %s" % (self.speaker, self.text)
	__unicode__ = __repr__
