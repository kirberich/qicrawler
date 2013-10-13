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

    def speaker_names(self):
        names = ["Stephen Fry", "Alan Davies"]

        try: 
            names_string = self.description.split(" ",1)[1]
        except IndexError:
            return []

        names_raw = names_string.split(",")
        for name_raw in names_raw:
            names.append(name_raw.strip())
        return names

    def full_speaker_name(self, speaker_name, speaker_names_list=None):
        speaker_names_list = speaker_names_list or self.speaker_names()
        for name in speaker_names_list:
            if speaker_name in name:
                return name

    def __repr__(self):
        return "Episode %s" % self.description
    __unicode__ = __repr__


class Quote(models.Model):
    episode = models.ForeignKey(Episode)
    speaker = models.ForeignKey(Speaker)
    text = models.TextField()

    previous = models.ForeignKey('self', blank=True, null=True, related_name="next_set")
    next = models.ForeignKey('self', blank=True, null=True, related_name="previous_set")
    
    def get_previous(self, limit):
        results = []
        item = self.previous
        item_number = 0
        while item is not None and item_number < limit:
            results.append(item)
            item_number += 1
            item = item.previous
        results.reverse()
        return results

    def get_next(self, limit):
        results = []
        item = self.next
        item_number = 0
        while item is not None and item_number < limit:
            results.append(item)
            item_number += 1
            item = item.next
        return results
    
    def __repr__(self):
        return "%s: %s" % (self.speaker, self.text)
    __unicode__ = __repr__
