# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from crickly.core import models as coremodels

class PlayCricketLinker(models.Model):
    pc_id = models.CharField(max_length=20)

    class Meta:
        abstract = True

    @classmethod
    def cricket_model(self):
        return self.model_link


class Match(PlayCricketLinker):
    model_link = coremodels.Match
    link = models.ForeignKey(coremodels.Match, on_delete=models.CASCADE,
                              related_name='pc_match_link')



class Team(PlayCricketLinker):
    model_link = coremodels.Team
    link = models.ForeignKey(coremodels.Team, on_delete=models.CASCADE, related_name='pc_team_link')


class Club(PlayCricketLinker):
    model_link = coremodels.Club
    link = models.ForeignKey(coremodels.Club, on_delete=models.CASCADE, related_name='pc_club_link')


class Umpire(PlayCricketLinker):
    model_link = coremodels.Umpire
    link = models.ForeignKey(coremodels.Umpire, on_delete=models.CASCADE,
                               related_name='pc_umpire_link')


class Scorer(PlayCricketLinker):
    model_link = coremodels.Scorer
    link = models.ForeignKey(coremodels.Scorer, on_delete=models.CASCADE,
                               related_name='pc_scorer_link')


class Competition(PlayCricketLinker):
    model_link = coremodels.Competition
    link = models.ForeignKey(coremodels.Competition, on_delete=models.CASCADE,
                                    related_name='pc_competition_link')


class League(PlayCricketLinker):
    model_link = coremodels.League
    link = models.ForeignKey(coremodels.League, on_delete=models.CASCADE,
                               related_name='pc_league_link')


class Ground(PlayCricketLinker):
    model_link = coremodels.Ground
    link = models.ForeignKey(coremodels.Ground, on_delete=models.CASCADE,
                               related_name='pc_ground_link')


class Player(PlayCricketLinker):
    model_link = coremodels.Player
    link = models.ForeignKey(coremodels.Player, on_delete=models.CASCADE,
                               related_name='pc_player_link')


