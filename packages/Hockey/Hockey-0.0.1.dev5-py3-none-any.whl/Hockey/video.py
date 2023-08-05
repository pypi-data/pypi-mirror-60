

import requests
import json



vidz=[]

def find(js,element,value):
	v=[]
	try:
		for a in js:
			if (a[element]==value):
				v.append(a)
	except:
		return {}
	return v

def findaction(json, event):

	a=find(json['media']['milestones']['items'],"statsEventId",str(event))[0]
	
	return {
		"action": a['title'],
		"event":  int(a['statsEventId']),
		"time":   a['periodTime'],
		"player": "/api/v1/people/{}".format(a['playerId']),
		"title":  a['highlight']['title'],
		"teamId": "/api/v1/teams/{}".format(a['teamId']),
		"period": a['ordinalNum'],
		"video":  find(a['highlight']['playbacks'],"name","HTTP_CLOUD_MOBILE")[0]['url']
	}


if (__name__=="__main__"):
	game="2019020629"
	sess=requests.session()
	url='https://statsapi.web.nhl.com/api/v1/game/{}/content'.format(game)
	m=sess.get(url)
	
	
	p=find(m.json()['media']['milestones']['items'],"type","GOAL")
	goals=[]
	goals=findaction(m.json(),74)
	
	print(json.dumps(goals))



#print(json.dumps(vidz))
