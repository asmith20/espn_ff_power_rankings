from django.db import models

# Create your models here.
class Team(models.Model):
    team_id = models.IntegerField()
    logo = models.CharField(max_length=200)
    record = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    box_score = models.CharField(max_length=100)
    rank = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))))
    prev_rank = models.IntegerField(choices=list(zip(range(1, 11), range(1, 11))), null=True)
    comments = models.CharField(max_length=500)

class CurrentRankWeek(models.Model):
    curr_week = models.IntegerField()