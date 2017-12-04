from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

EVENTS={"100": "External Forms Empty Hand Chuan Fa/Kempo",
        "101": "External Forms Empty Hand Contemporary Chang Chuan",
        "102": "External Forms Empty Hand Contemporary Nan Chuan",
        "103": "External Forms Empty Hand Open",
        "104": "External Forms Empty Hand Traditional Northern",
        "105": "External Forms Empty Hand Traditional Southern Longfist",
        "106": "External Forms Empty Hand Traditional Southern Shorthand",
        "107": "External Forms Empty Hand Two Person External Set",
        "108": "External Forms Weapons Contemporary Flexable / Double",
        "109": "External Forms Weapons Contemporary Long",
        "110": "External Forms Weapons Contemporary Open",
        "111": "External Forms Weapons Contemporary Short",
        "112": "External Forms Weapons Traditional Flexable / Double",
        "113": "External Forms Weapons Traditional Long",
        "114": "External Forms Weapons Traditional Open",
        "115": "External Forms Weapons Traditional Short",
        "116": "Internal Forms Empty Hand Chen Tai Chi",
        "117": "Internal Forms Empty Hand Guang Ping Tai Chi",
        "118": "Internal Forms Empty Hand Hsing-I / Bagua",
        "119": "Internal Forms Empty Hand Open Internal (Not Tai Chi)",
        "120": "Internal Forms Empty Hand Open Tai Chi",
        "121": "Internal Forms Empty Hand Two Person Internal Set",
        "122": "Internal Forms Empty Hand Yang Tai Chi",
        "123": "Internal Forms Weapons Internal Long",
        "124": "Internal Forms Weapons Internal Open",
        "125": "Internal Forms Weapons Internal Short",
        "126": "Internal Forms Weapons Internal Sword",
        "127": "Reaction Skills Chi Sau",
        "128": "Reaction Skills Continuous Sparring",
        "129": "Reaction Skills Fixed Step Push Hands",
        "130": "Reaction Skills Moving Step Push Hands",
        "131": "Reaction Skills Shuai Jiao",
        "132": "External Forms Weapons Two Person Ext. Weapon",
        "133": "Internal Forms Weapons Two Person Int. Weapon"
}

fields = ['name','address','phone','email','gender','age','experience',
          'school_name','school_master','school_address','school_phone','school_email',
          'payment_type','payment_amount','payment_memo',
          'events']
EXP_DIVISIONS={ 'novice': 'Novice',
                'beginner': 'Beginner',
                'intermediate': 'Intermediate',
                'advanced': 'Advanced',
                'advanced_plus': 'Advanced Plus'
}
AGE_DIVISIONS=[ ('Youth 5-7',(5,7)),
                ('Youth 8-10',(8,10)),
                ('Youth 11-13',(11,13)),
                ('Youth 13-17',(14,17)),
                ('Adult 18-35',(18,35)),
                ('Adult 36+',(36,1000))
]
GENDERS=['M','F']


app= Flask(__name__)
app.config.from_object(__name__)

mongo = PyMongo(app)
def process_event_data(docs):
  event_data=dict()
  for doc in docs:
    age_div = filter(lambda x: int(doc['age']) in range(x[1][0],x[1][1]+1),AGE_DIVISIONS)[0]
    if not doc.has_key('events'):
      doc['events']=list()
    for event in doc['events']:
      key = ( (event,EVENTS[event]),age_div,doc['experience'])
      if event_data.has_key(key):
        event_data[key].append(doc)
      else:
        event_data[key] = [doc]
  return event_data


@app.route('/')
def index():
  return redirect(url_for('competitors'))

@app.route('/registration_form')
def registration_form():
  doc = { key:"" for key in fields }
  doc['events']=[]
  doc['uid']=""
  return render_template('register.html', doc=doc)

@app.route('/register', methods=['POST'])
def register():
  competitor = mongo.db.competitors
  data = { key:request.form[key] for key in request.form.keys() if key in fields}
  if 'events' in data.keys():
    data['events'] = request.form.getlist('events')
  competitor_id = None
  if request.form['uid'] == '':
    competitor_id = competitor.insert(data)
  else:
    competitor_id = request.form['uid']
    competitor.replace_one({'_id':ObjectId(request.form['uid'])},data)
  print competitor_id
  return redirect(url_for('competitor', uid=competitor_id))

@app.route('/unregister', methods=['POST'])
def unregister():
  uid = request.form['uid']
  mongo.db.competitors.remove(ObjectId(uid))
  return redirect(url_for('competitors'))
  
@app.route('/edit/<uid>')
def edit(uid=None):
  competitor = mongo.db.competitors.find_one(ObjectId(uid))
  competitor['uid']=uid
  return render_template('register.html', doc=competitor)
  

@app.route('/competitors')
def competitors():
  competitors = mongo.db.competitors.find()
  return render_template('competitors.html', docs=competitors)


@app.route('/competitor/<uid>')
def competitor(uid=None):
  competitor = mongo.db.competitors.find_one(ObjectId(uid))
  return render_template('competitor.html', doc=competitor, events=EVENTS)


@app.route('/ringsheets')
def ringsheets():
  competitors = mongo.db.competitors.find()
  event_data = process_event_data(competitors)
  return render_template('ringsheets.html', event_data=event_data, AGE_DIVISIONS=AGE_DIVISIONS, EXP_DIVISIONS=EXP_DIVISIONS)


@app.route('/ringsheet/<eid>')
def ringsheet(eid):
  age = request.args.get('age','')
  exp = request.args.get('exp','')
  competitors = mongo.db.competitors.find()
  event_data = process_event_data(competitors)
  key = ((eid,EVENTS[eid]),AGE_DIVISIONS[int(age)],exp)
  competitors = event_data[key]
  return render_template('ringsheet.html', competitors=competitors,event_key=key,EXP_DIVISIONS=EXP_DIVISIONS)
