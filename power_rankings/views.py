from django.shortcuts import render
from django.http import HttpResponse
import requests
import pandas as pd
from django.conf import settings
import json
from .forms import power_ranks
from .models import Team, CurrentRankWeek
from django.views.generic.edit import UpdateView, CreateView
from django.forms import modelformset_factory
from datetime import datetime
import numpy as np
from datetime import datetime


# Create your views here.
def get_score(team_id, teams, scores, week):
    if week > 0:
        if team_id in scores['home.teamId'].to_list():
            row = scores[scores['home.teamId'] == team_id]
            opp = teams[teams['id'] == row.iloc[0,2]]
            opp = opp.iloc[0, 2]
            if row.iloc[0,1] > row.iloc[0,3]:
                return f"Beat {opp}, {row.iloc[0,1]}-{row.iloc[0,3]}"
            else:
                return f"Lost to {opp}, {row.iloc[0,1]}-{row.iloc[0,3]}"
        else:
            row = scores[scores['away.teamId'] == team_id]
            opp = teams[teams['id'] == row.iloc[0,0]]
            opp = opp.iloc[0,2]
            if row.iloc[0,1] > row.iloc[0,3]:
                return f"Lost to {opp}, {row.iloc[0,3]}-{row.iloc[0,1]}"
            else:
                return f"Beat {opp}, {row.iloc[0,3]}-{row.iloc[0,1]}"
    else:
        if team_id in scores['home.teamId'].to_list():
            row = scores[scores['home.teamId'] == team_id]
            opp = teams[teams['id'] == row.iloc[0,2]]
            opp = opp.iloc[0, 2]
            return f"Week 1 matchup against {opp}"
        else:
            row = scores[scores['away.teamId'] == team_id]
            opp = teams[teams['id'] == row.iloc[0,0]]
            opp = opp.iloc[0,2]
            return f"Week 1 matchup against {opp}"



def create_power_rankings(request):
    week0 = datetime(2021,9,7)
    week = int(np.floor((datetime.now() - week0).days/7))
    if week < 0:
        week = 0
    RankFormset = modelformset_factory(Team, extra=0, fields=('rank', 'comments'))
    curr_week = CurrentRankWeek.objects.get(id=1)
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = RankFormset(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            form.save()
            curr_week.curr_week = week
            curr_week.save()
            teams = Team.objects.order_by('rank')
            return render(request, 'power_rankings/power_rankings.html', {'teams':teams, 'week':week})
    else:
        #Team.objects.all().delete()
        yr = datetime.now().year
        url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{yr}/segments/0/leagues/86125"
        raw = requests.get(url, params={"view": "mBoxscore"},
                           cookies={"swid": settings.ESPN_SWID,
                                    "espn_s2": settings.ESPN_S2})
        data = raw.json()
        teams = pd.json_normalize(data["teams"])
        teams['team'] = teams['location'] + " " + teams['nickname']
        teams['record'] = teams.apply(
            lambda row: str(row['record.overall.wins']) + "-" + str(row['record.overall.losses']) + "-" + str(
                row['record.overall.ties']), axis=1)
        teams = teams[['id', 'logo', 'team', 'record']]

        df = pd.json_normalize(data["schedule"])
        if week > 0:
            df = df[df['matchupPeriodId'] == week]
        else:
            df = df[df['matchupPeriodId'] == 1]
        df = df[['home.teamId', 'home.totalPoints', 'away.teamId', 'away.totalPoints']]

        teams['this_week'] = teams.apply(lambda row: get_score(row['id'], teams, df, week), axis=1)

        for n, row in teams.iterrows():
            if Team.objects.filter(team_id=row['id']).count() > 0:
                model = Team.objects.get(team_id=row['id'])
                if week > curr_week.curr_week:
                    model.prev_rank = model.rank
                model.logo = row['logo']
                model.name = row['team']
                model.record = row['record']
                model.box_score = row['this_week']
                model.save()
            else:
                model = Team()
                model.team_id = row['id']
                model.logo = row['logo']
                model.name = row['team']
                model.record = row['record']
                model.box_score = row['this_week']
                model.rank = n+1
                model.prev_rank = n+1
                model.comments = 'none'
                model.save()

        rank_formset = RankFormset(queryset=Team.objects.all().order_by('rank'))
        return render(request, 'power_rankings/rank_form.html', {'forms':rank_formset})

