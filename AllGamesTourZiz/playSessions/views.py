from django.http import HttpResponseRedirect
from django.shortcuts import render
import re
import math
from .models import PlaySession, SessionParticipants
from shareScripts.decorators import need_authorization, need_stuff
from users.models import GameStats, User
from django.utils.dateparse import parse_duration
from django.db.models import F
from enum import Enum

MAX_ON_PAGE = 10


def all_sessions_view(request):
    search = request.GET.get('search', '')
    if not bool(re.match(r"^[a-zA-Z0-9 ]+$", search)) or len(search) > 20:
        search = ''

    new_link = f"/sessions/?search={search}" if search else "/sessions/"

    filtered_sessions = PlaySession.objects.filter(game__name__icontains=search).order_by("created_at")
    try:
        page = int(request.GET.get("page", 1))
        lastpage = math.floor(((filtered_sessions.count() - 1) / MAX_ON_PAGE) + 1)
        if page < 1 or page > lastpage:
            raise
    except:
        return HttpResponseRedirect(new_link)

    context = {"user": request.user, 'page': page}
    if page > 1:
        context['prevpage'] = new_link + (f'&page={page - 1}' if search else f"?page={page - 1}")
    if page < lastpage:
        context['nextpage'] = new_link + (f'&page={page + 1}' if search else f"?page={page + 1}")
    if search != '':
        context['search'] = search

    filtredsessions = filtered_sessions[(page - 1) * MAX_ON_PAGE:page * MAX_ON_PAGE]

    context['allsessions'] = filtredsessions.values("uniqueCode", "status", "game__name", "game__image")

    for i in range(len(context['allsessions'])):
        this_session_participants = SessionParticipants.objects.filter(session=filtredsessions[i])

        player1 = this_session_participants.filter(numberInSession=0).first()
        if player1 is None:
            continue

        context['allsessions'][i]['player1name'] = player1.user.username
        context['allsessions'][i]['player1avatar'] = player1.user.avatar
        player2 = this_session_participants.filter(numberInSession=1).first()

        if player2 is None:
            continue

        context['allsessions'][i]['player2name'] = player2.user.username
        context['allsessions'][i]['player2avatar'] = player2.user.avatar

        context['allsessions'][i]['player3exists'] = this_session_participants.filter(numberInSession=2).exists()

    return render(request, "allsessions.html", context)


def session_view(request, sessionid):
    sessions = PlaySession.objects.filter(uniqueCode=sessionid)
    if not sessions.exists():
        return render(request, "errors/session_not_found.html", {"user": request.user})

    session = sessions.first()
    context = {"user": request.user,
               'gamename': session.game.name, 'gameimage': session.game.image,
               'status': session.status, 'uniqueCode': session.uniqueCode}

    participants = SessionParticipants.objects.filter(session=session).order_by("-numberInSession")

    teams = []
    team = {}
    adminteams = []
    lastTeam = -1
    for participant in participants:
        if participant.numberInSession != lastTeam:
            if lastTeam != -1:
                teams.append(team)
            team = {'players': [],
                    'number': {'text': f'номер {participant.numberInSession + 1}',
                               'value': participant.numberInSession}}
            if participant.points:
                team['results'] = {'text': f' - {participant.points} очков',
                                   'value': participant.points,
                                   'isPoints': True}
            elif participant.time:
                team['results'] = {'text': f' - время: {participant.time}',
                                   'value': participant.time,
                                   'isPoints': False}
            else:
                team['results'] = {'text': '',
                                   'value': None,
                                   'isPoints': True}
            if session.status - 4 == participant.numberInSession:
                context['winner'] = participant.user.username
            if session.status <= 2:
                adminteams.append(
                    {"value": participant.numberInSession + 4, "team": f'Команда {participant.user.username}'})

        lastTeam = participant.numberInSession
        player = {'name': participant.user.username, 'image': participant.user.avatar, 'mmrChange': participant.mmrChange}
        playerForMMR = session.game.gamestats_set.filter(user=participant.user).first()
        if playerForMMR:
            player['MMR'] = playerForMMR.MMR
        team['players'].append(player)

    teams.append(team)
    teams.reverse()
    context['teams'] = teams

    if request.user.is_authenticated and request.user.is_staff:
        context['adminteams'] = adminteams

    return render(request, "session.html", context)


@need_stuff
def new_team_value(request, sessionid, teamnumber):
    sessions = PlaySession.objects.filter(uniqueCode=sessionid)
    if not sessions.exists():
        return render(request, "errors/session_not_found.html", {"user": request.user})

    if request.method == 'POST':
        session = sessions.first()
        points = request.POST.get('points', None)
        if points == '':
            points = None
        if points is not None:
            points = int(points)
        time = request.POST.get('time', None)
        print(time)
        if time == '00:00:00':
            time = None
        if time is not None:
            time = parse_duration(time)
        SessionParticipants.objects.filter(session=session, numberInSession=teamnumber).update(points=points, time=time)

    return HttpResponseRedirect(f'/sessions/{sessionid}')


@need_stuff
def new_status(request, sessionid):
    sessions = PlaySession.objects.filter(uniqueCode=sessionid)
    if not sessions.exists():
        return render(request, "errors/session_not_found.html", {"user": request.user})

    if request.method == 'POST':
        session = sessions.first()
        session.status = int(request.POST.get('newstatus'))
        if session.status >= 3:
            changeMMR(session)
        session.save(update_fields=['status'])

    return HttpResponseRedirect(f'/sessions/{sessionid}')


def changeMMR(session):
    participants = SessionParticipants.objects.filter(session=session)
    if session.status == 3:
        print('hello')
        participants.update(mmrChange=0)
        return
        # TODO: normal draw

    class WinnerBy(Enum): # TODO: add this to game model
        MOST_POINTS = 1
        LEAST_POINTS = 2
        MOST_TIME = 3
        LEAST_TIME = 4
        ONE_WINNER = 5



    winnerPoints = participants.filter(numberInSession=session.status-4).first() # TODO: change this shit
    if winnerPoints is not None:
        winnerPoints = winnerPoints.points
    winnerTime = participants.filter(numberInSession=session.status-4).first() # TODO: this too
    if winnerTime is not None:
        winnerTime = winnerTime.time
    if winnerPoints is not None:
        loserPoints = participants.exclude(numberInSession=session.status - 4).first().points
        if loserPoints is None:
            loserPoints = 0

        if winnerPoints >= loserPoints:
            winBy = WinnerBy(1)
            # sorted_participants = participants.order_by("-points", "")
        else:
            winBy = WinnerBy(2)
            # sorted_participants = participants.order_by("points")
    elif winnerTime is not None:
        loserTime = participants.exclude(numberInSession=session.status - 4).first().time
        if loserTime is None:
            loserTime = 0
        else:
            loserTime = loserTime.total_seconds()

        winnerTime = winnerTime.total_seconds()

        if winnerTime >= loserTime:
            winBy = WinnerBy(3)
            # sorted_participants = participants.order_by("-time")
        else:
            winBy = WinnerBy(4)
            # sorted_participants = participants.order_by("time")
    else:
        winBy = WinnerBy(5)
        # sorted_participants = participants.order_by("points", "time")

    values_participants = participants.values("points", "time", "numberInSession", "user__username")

    teams = {}
    for participant in values_participants:
        if participant['numberInSession'] not in teams.keys():
            teams[participant['numberInSession']] = {'points': participant['points'] or 0,
                                                     'time': participant['time'].total_seconds()
                                                        if participant['time'] is not None else 0,
                                                  'mmrSum': 0, 'users': []}
        teams[participant['numberInSession']]['users'].append(participant['user__username'])
        gamestat, created = GameStats.objects.get_or_create(
            user=User.objects.get(username=participant['user__username']),
            game=session.game)
        teams[participant['numberInSession']]['mmrSum'] += gamestat.MMR

    for team in teams.values():
        team['mmr_avarage'] = team['mmrSum'] / len(team['users'])

    for team in teams.values():
        sumMMRchanges = 0
        for enemyteam in teams.values():
            if team['users'] == enemyteam['users']:
                continue

            Sa = 0.5

            if team['points'] > enemyteam['points']:
                if winBy == WinnerBy.MOST_POINTS: Sa = 1
                if winBy == WinnerBy.LEAST_POINTS: Sa = 0
            if team['points'] < enemyteam['points']:
                if winBy == WinnerBy.MOST_POINTS: Sa = 0
                if winBy == WinnerBy.LEAST_POINTS: Sa = 1
            if team['points'] == enemyteam['points'] and (winBy == WinnerBy.MOST_POINTS or winBy == WinnerBy.LEAST_POINTS):
                Sa = 0.5

            if team['time'] > enemyteam['time']:
                if winBy == WinnerBy.MOST_TIME: Sa = 1
                if winBy == WinnerBy.LEAST_TIME: Sa = 0
            if team['time'] < enemyteam['time']:
                if winBy == WinnerBy.MOST_TIME: Sa = 0
                if winBy == WinnerBy.LEAST_TIME: Sa = 1
            if team['time'] == enemyteam['time'] and (winBy == WinnerBy.MOST_TIME or winBy == WinnerBy.LEAST_TIME):
                Sa = 0.5

            print(f"===== {winBy} - {team['mmr_avarage']} enemy {enemyteam['mmr_avarage']} | Sa: {Sa} =====")
            sumMMRchanges += ELOrating(team['mmr_avarage'], enemyteam['mmr_avarage'], Sa)

        team['mmr_change'] = round(sumMMRchanges / (len(teams) - 1))
        for username in team['users']:
            changeuser = User.objects.get(username=username)

            participants.filter(user=changeuser).update(mmrChange=team['mmr_change'])
            changeuser.MMR += team['mmr_change']
            changeuser.save()
            nowgame = session.game
            while nowgame is not None:
                stat, created = GameStats.objects.get_or_create(
                    user=changeuser,
                    game=nowgame)
                stat.MMR += team['mmr_change']
                stat.save()
                nowgame = nowgame.relateOnId


    print(teams)


def ELOrating(Ra, Rb, Sa, K = 60):
    E = 1/(1+10**((Rb-Ra)/400))
    return K * (Sa - E)