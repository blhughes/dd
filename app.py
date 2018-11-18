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
        "133": "Internal Forms Weapons Two Person Int. Weapon",
        "134": "External Forms Group",
        "135": "External Forms Group Weapons",
        "136": "Internal Forms Group",
        "137": "Internal Forms Group Weapons"
}

fields = ['name','address','phone','email','gender','age','experience',
          'school_name','school_master','school_address','school_phone','school_email',
          'payment_type','payment_amount','payment_memo',
          'events','waiver']
EXP_DIVISIONS={ 'novice': 'Novice',
                'beginner': 'Beginner',
                'intermediate': 'Intermediate',
                'advanced': 'Advanced',
                'advanced_plus': 'Advanced Plus'
}
AGE_DIVISIONS=[ ('Youth 5-8',(5,8)),
                ('Youth 9-10',(9,12)),
                ('Youth 13-17',(13,17)),
                ('Adult 18-35',(18,35)),
                ('Adult 36+',(36,1000))
]
GENDERS=['M','F']


app= Flask(__name__)
app.config['MONGO_CONNECT']=False
app.config['MONGO_URI']="mongodb://localhost:27017/app"
app.config.from_object(__name__)

mongo = PyMongo(app)
def process_event_data(docs):
  event_data=dict()
  for doc in docs:
    age_div = [x for x in AGE_DIVISIONS if int(doc['age']) in range(x[1][0],x[1][1]+1)][0]
    if 'events' not in doc:
      doc['events']=list()
    for event in doc['events']:
      key = ( (event,EVENTS[event]),age_div,doc['experience'])
      if key in event_data:
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
  data = { key:request.form[key] for key in list(request.form.keys()) if key in fields}
  if 'events' in list(data.keys()):
    data['events'] = request.form.getlist('events')
  if 'waiver' in list(data.keys()):
    if data['waiver'] == 'yes':
      data['waiver'] = True
    else:
      data['waiver'] = False
  else:
      data['waiver'] = False

  competitor_id = None
  if request.form['uid'] == '':
    competitor_id = competitor.insert(data)
  else:
    competitor_id = request.form['uid']
    competitor.replace_one({'_id':ObjectId(request.form['uid'])},data)
  print(competitor_id)
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

@app.route('/stats')
def stats():
  competitors = [x for x in mongo.db.competitors.find()]
  entries = len(competitors)
  event_data = process_event_data(competitors)
  recorded_payments = sum( [float(doc['payment_amount']) for doc in competitors if 'payment_amount' in doc and doc['payment_amount']!=""]  )
  events=[doc['events'] for doc in competitors if 'events' in doc]
  esum=0
  for event in events:
    if(len(event) ==1):
      esum = esum+50
    elif(len(event) ==2):
      esum = esum+60
    elif(len(event) >=3):
      esum = esum+70
  payment=esum

  return render_template('stats.html', docs = competitors, entries=entries, recorded_payments=recorded_payments, payment=payment, events=len(event_data))
