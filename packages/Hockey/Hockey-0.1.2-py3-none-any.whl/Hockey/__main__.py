
import requests
import time
import paho.mqtt.publish as publish
import datetime
import dateutil.parser

from Hockey import video
from Hockey import config

URL="https://statsapi.web.nhl.com/"

endpoint={
	"schedule": 		"/api/v1/schedule",
	"teamsID": 		"/api/v1/teams/{}",
	"scheduleteam": 	"/api/v1/schedule/?teamId={}&date={}",
	"gamefeed":		"/api/v1/game/{}/live/feed",
	"gamecontent":		"/api/v1/game/{}/content",
	"nextev":		"/api/v1/schedule/?endDate={}&startDate={}&teamId={}"
}



def sendMessage(txt):
	publish.single('hockey/message',txt,hostname=MYHOST)
	return 0

def nextDate(team):
	start=datetime.datetime.now()
	end=datetime.datetime.now()+datetime.timedelta(days=5)
	url=URL+endpoint['nextev'].format(end.date(),start.date(),team)
	m=sess.get(url)
	txt=""
	for a in m.json()['dates']:
		d=dateutil.parser.parse(a['games'][0]['gameDate']).timestamp()
		d=datetime.datetime.fromtimestamp(d).strftime("%c")

		h=a['games'][0]['teams']['home']['team']['name']
		v=a['games'][0]['teams']['away']['team']['name']
		if (a['games'][0]['teams']['home']['team']['id']== MYteam):
			hc="[3;32m{}[0m".format(h)
			vc=v
		else:
			vc="[3;32m{}[0m".format(v)
			hc=h
		print("[[1;32m{}[0m ] {}-{}".format(d,hc,vc))
		txt=txt+"[{}] {} vs. {}\n".format(d,h,v)
	sendMessage(txt)
	return m.json()



config=config.config("hockey")

if (config.status==False):
	data={}
	print("Config:")
	data['myteam']=input("Read Team")
	data['host']  =input("Read mqtt Host")
	config.write(data)
	MYteam=data['myteam']
	MYHOST=data['host']

else:
	data=config.readConf()
	MYteam=data['myteam']
	MYHOST=data['host']


#MYteam=17
#MYteam=8
#MYHOST='meraki'




sess=requests.session()
m=sess.get(URL+endpoint['scheduleteam'].format(MYteam,datetime.datetime.now().strftime("%Y-%m-%d")))

url=URL+endpoint['teamsID'].format(MYteam)
team=sess.get(url).json()['teams']


if (len(m.json()['dates'])<1):
	print ("[Next Games [3;32m{}[0m]".format(team[0]['name']))
	m=nextDate(MYteam)
	exit(1)
	
endpoint['live']= m.json()['dates'][0]['games'][0]['link']

e={
'away' : {'goal': 0},
'home' : {'goal': 0},
'lastgoal': 0
}

game=m.json()['dates'][0]['games'][0]['gamePk']

print(URL+endpoint['live'])
oldstatus=0
oldperiod=0
oldgoal=0

while 1:
	sess= requests.session()
	m=sess.get(URL+endpoint['live'])
	e['away']['name'] = m.json()['gameData']['teams']['away']['name']
	e['home']['name'] = m.json()['gameData']['teams']['home']['name']
	e['status']=m.json()['gameData']['status']['detailedState']
	e['wait']=m.json()['metaData']['wait']

	status=int(m.json()['gameData']['status']['statusCode'])
	e['statusCode']=status


	if (status != oldstatus):
		print("Change Status")
		sendMessage("Status {}".format(e['status']))
		oldstatus=status

	if (status==1):
		now=int(datetime.datetime.now().timestamp())
		match=int(dateutil.parser.parse(m.json()['gameData']['datetime']['dateTime']).timestamp())
		time2match=(match-now)
		dateMatch=datetime.datetime.fromtimestamp(match).strftime("%c")
		print("Waiting for match {}".format(dateMatch))
		sendMessage("Waiting {} sec before {} {}:{}".format(time2match,dateMatch,e['home']['name'],e['away']['name']))
		time.sleep(time2match/2)



	if (int(m.json()['gameData']['status']['statusCode'])>2):


		g1 = m.json()['liveData']['plays']['currentPlay']['about']['goals']['away']
		g2 = m.json()['liveData']['plays']['currentPlay']['about']['goals']['home']
	
	#	print(g1+g2)
	#	print(e['away']['goal']+e['home']['goal'])
	
		if ( (g1+g2) > (e['away']['goal']+e['home']['goal'])):
			print("Goal")
			print("Score : {} - {} {} - {}".format(e['home']['name'],g2,g1,e['away']['name']))
			txt="Score : {} - {} {} - {}".format(e['home']['name'],g2,g1,e['away']['name'])
	
			last=m.json()['liveData']['plays']['scoringPlays'][-1:][0]
			team=m.json()['liveData']['plays']['allPlays'][last]['team']['name']
			name=m.json()['liveData']['plays']['allPlays'][last]['players'][0]['player']['fullName']
			id=m.json()['liveData']['plays']['allPlays'][last]['players'][0]['player']['id']
			evtid=m.json()['liveData']['plays']['allPlays'][last]['about']['eventId']
			print("{} de {}".format(name,team))
			e['lastgoal']=evtid
	
			img="https://nhl.bamcontent.com/images/headshots/current/60x60/{}@3x.jpg".format(id)
	
			txt="Score : {} {}-{} {}\nBut {} de {} {} id: {}".format(e['home']['name'],g2,g1,e['away']['name'],name,team,img,evtid)
			sendMessage(txt)


		if (oldgoal != e['lastgoal']):

			print("check video")
			sess=requests.session()
			url=URL+endpoint['gamecontent'].format(game)
			print(url)
			m2=sess.get(url)

			goals=[]
			try:
				goals=video.findaction(m2.json(),e['lastgoal'])
				sendMessage("Review Goal : {} ".format(goals['video']))
				oldgoal=e['lastgoal']
			except:
				pass

	
		
		if (e['away']['goal'] != g1):
		    e['away']['goal'] = g1
		
		if (e['home']['goal'] != g2):
		    e['home']['goal'] = g2
		
		period = m.json()['liveData']['plays']['currentPlay']['about']['ordinalNum']
		e['time']    = m.json()['liveData']['plays']['currentPlay']['about']['periodTimeRemaining']
		e['period']  = period

		if ( oldperiod != period):
			oldperiod=period
			txt="Changement > {} ({})".format(period,e['time'])
			sendMessage(txt)
		
		

	
	print(e)

	if (status>5):
		txt="{} {} {}-{} {}".format(
			e['status'],
			e['away']['name'],
			e['away']['goal'],
			e['home']['goal'],
			e['home']['name'])
		sendMessage(txt)
		exit(0)

	time.sleep(e['wait'])

