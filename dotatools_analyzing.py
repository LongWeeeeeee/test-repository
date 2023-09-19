import requests, json

url = "https://api.stratz.com/graphql"
api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiMWM5MDkyYTgtMGY0OS00OTExLTliMjQtNjM2OWZlNDQ2NzFhIiwiU3RlYW1JZCI6IjQ1MDgzMDI2MCIsIm5iZiI6MTY5MzI5MzMwMCwiZXhwIjoxNzI0ODI5MzAwLCJpYXQiOjE2OTMyOTMzMDAsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.NMbS1F2UuagU8o4RghSgyYgNebPgR1xng46KDC-kaz8'
headers = {"Authorization": f"Bearer {api_token}"}

match_id = 7223329449

query = """query GetLiveMatches {
  live {
    matches(request: {take: 100, orderBy: GAME_TIME, isParsing: true}) {
      matchId
      spectators
      ...LiveMatchMatchLiveTypeFragment
      ...LivePageModifiersMatchLiveType
      __typename
    }
    __typename
  }
}

fragment LiveMatchMatchLiveTypeFragment on MatchLiveType {
  gameTime
  averageRank
  league {
    id
    displayName
    __typename
  }
  players {
    ...LiveMatchFactionMatchLivePlayerTypeFragment
    __typename
  }
  ...GetGameStateMatchLiveTypeFragment
  ...LiveMinimapMatchLiveTypeFragment
  ...LiveMatchKashaMatchLiveTypeFragment
  __typename
}

fragment GetGameStateMatchLiveTypeFragment on MatchLiveType {
  playbackData {
    buildingEvents {
      npcId
      isAlive
      __typename
    }
    __typename
  }
  isParsing
  players {
    heroId
    __typename
  }
  gameTime
  __typename
}

fragment LiveMatchFactionMatchLivePlayerTypeFragment on MatchLivePlayerType {
  heroId
  numKills
  numDeaths
  numAssists
  steamAccount {
    id
    name
    proSteamAccount {
      name
      team {
        id
        tag
        name
        __typename
      }
      __typename
    }
    ...SteamAccountHoverCardSteamAccountTypeFragment
    __typename
  }
  __typename
}

fragment SteamAccountHoverCardSteamAccountTypeFragment on SteamAccountType {
  id
  name
  avatar
  isAnonymous
  isStratzPublic
  smurfFlag
  proSteamAccount {
    name
    team {
      id
      tag
      __typename
    }
    __typename
  }
  __typename
}

fragment LiveMinimapMatchLiveTypeFragment on MatchLiveType {
  players {
    heroId
    isRadiant
    playbackData {
      positionEvents {
        x
        y
        time
        __typename
      }
      __typename
    }
    ...LiveMinimapHeroHoverCardMatchLivePlayerTypeFragment
    __typename
  }
  playbackData {
    buildingEvents {
      npcId
      isAlive
      time
      positionX
      __typename
    }
    __typename
  }
  gameTime
  ...LiveScoreAndTimeMatchLiveTypeFragment
  __typename
}

fragment LiveMinimapHeroHoverCardMatchLivePlayerTypeFragment on MatchLivePlayerType {
  heroId
  level
  steamAccount {
    ...SteamAccountHoverCardSteamAccountTypeFragment
    __typename
  }
  __typename
}

fragment LiveScoreAndTimeMatchLiveTypeFragment on MatchLiveType {
  gameTime
  radiantScore
  direScore
  radiantTeam {
    ...LiveScoreAndTimeTeamTypeFragment
    __typename
  }
  direTeam {
    ...LiveScoreAndTimeTeamTypeFragment
    __typename
  }
  playbackData {
    radiantScore {
      ...LiveScoreAndTimeMatchLiveTeamScoreDetailTypeFragment
      __typename
    }
    direScore {
      ...LiveScoreAndTimeMatchLiveTeamScoreDetailTypeFragment
      __typename
    }
    __typename
  }
  __typename
}

fragment LiveScoreAndTimeTeamTypeFragment on TeamType {
  id
  name
  __typename
}

fragment LiveScoreAndTimeMatchLiveTeamScoreDetailTypeFragment on MatchLiveTeamScoreDetailType {
  time
  score
  __typename
}

fragment LiveMatchKashaMatchLiveTypeFragment on MatchLiveType {
  matchId
  serverSteamId
  radiantScore
  direScore
  winRateValues
  durationValues
  liveWinRateValues {
    winRate
    __typename
  }
  players {
    networth
    __typename
  }
  radiantTeam {
    ...LiveMatchKashaTeamTypeFragment
    __typename
  }
  direTeam {
    ...LiveMatchKashaTeamTypeFragment
    __typename
  }
  ...GetDidRadiantWinMatchLiveTypeFragment
  __typename
}

fragment LiveMatchKashaTeamTypeFragment on TeamType {
  id
  name
  __typename
}

fragment GetDidRadiantWinMatchLiveTypeFragment on MatchLiveType {
  playbackData {
    buildingEvents {
      npcId
      isAlive
      __typename
    }
    __typename
  }
  __typename
}

fragment LivePageModifiersMatchLiveType on MatchLiveType {
  players {
    steamAccount {
      ...SteamAccountPageModifierSteamAccountTypeFragment
      __typename
    }
    heroId
    __typename
  }
  radiantTeam {
    ...LivePageModifiersTeamTypeFragment
    __typename
  }
  direTeam {
    ...LivePageModifiersTeamTypeFragment
    __typename
  }
  league {
    id
    displayName
    __typename
  }
  ...GetGameStateMatchLiveTypeFragment
  __typename
}

fragment LivePageModifiersTeamTypeFragment on TeamType {
  id
  name
  __typename
}

fragment SteamAccountPageModifierSteamAccountTypeFragment on SteamAccountType {
  id
  name
  avatar
  proSteamAccount {
    name
    team {
      id
      tag
      name
      __typename
    }
    __typename
  }
  __typename
}
"""

player_name = 'Qojqva'
match1 = requests.post(url, json={"query":query}, headers=headers)
match = json.loads(match1.text)
print(match1.status_code)
for match in match['data']['live']['matches']:
    for player in match['players']:
        # if player['steamAccount']['name'] == player_name:
        print(player['steamAccount']['name'])