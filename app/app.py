from flask import Flask, jsonify, send_from_directory, request, send_file, render_template, redirect, Response
from flask_cors import CORS

from beaker.middleware import SessionMiddleware
from cork import FlaskCork, Redirect
from cork.backends import MongoDBBackend


import logging

import os
import datetime
import random
import json

import get_stimuli as gs
import get_codes as gc

import pandas as pd

import pymongo
from bson import json_util

from io import StringIO

# configuration
DEBUG = True



def create_app():
    # instantiate the app
    app = Flask(__name__)
    app.config.from_object(__name__)    
    
    app.config['MONGODB_SETTINGS'] = {
    'db': 'megameta',
    'host': 'localhost',
    'port': 27017
    }
    
    # enable CORS   - IS THIS NEEDED?
    CORS(app, resources={r'/*': {'origins': '*'}})
    

    # setup Cork authentication
    
    try:
        backend = MongoDBBackend(db_name='megameta', initialize=True)
    except:
        backend = None
        print('NO BACKEND')
    
    aaa = FlaskCork('conf', backend=backend)


    
    def post_get(name, default=''):
        v = request.form.get(name, default).strip()
        return str(v)
    
    @app.errorhandler(Redirect)
    def redirect_exception_handler(e):
         return redirect(e)
    
    
    @app.route('/login')
    def login_form():
        """Serve login form"""
        return render_template('login_form.html')


    
    @app.route('/login', methods=['POST'])
    def login():
        """Authenticate users"""
        username = post_get('username')
        password = post_get('password')
        aaa.login(username, password, success_redirect='/', fail_redirect='/login')
    
    
    @app.route('/logout')
    def logout():
        aaa.logout(success_redirect='/login')
    
    
    # Admin-only pages

    @app.route("/admin")
    def show_admin():
        aaa.require(role="admin", fail_redirect="/")
        users = list(aaa.list_users())
        

        user_coded_cnt = { u[0] : db.megameta.codes.count_documents({'uid': u[0]})
                               for u in users }
        
        
        
        return render_template("admin.html", 
                               user=aaa.current_user, 
                               users=users,
                               user_coded_cnt=user_coded_cnt
                              )


    @app.route('/create_user', methods=['POST'])
    def create_user():
        aaa.require(role="admin", fail_redirect="/")
        users = aaa.list_users()
        try:
            aaa.create_user(post_get('username'), post_get('role'),
                post_get('password'), post_get('email'))
            return render_template("admin.html", user=aaa.current_user, users=users)
            
        except Exception as e:
            return jsonify(ok=False, msg=e)


    
    # SETUP ROUTES
    
    @app.route('/')
    def index():
        """Only authenticated users can see this"""
        aaa.require(fail_redirect='/login')
        
        user = aaa.current_user

        cursor=db.megameta.codes.find({'uid': user.username}, {'stim_id': 1}).sort('stim_id', pymongo.ASCENDING)
        coded_cnt = cursor.count()
        coded_stims = {}
        for id in cursor:
            stim_id = id['stim_id']
            project = stim_id.split('-')[0]
            try:
                coded_stims[project].append(stim_id)
            except:
                coded_stims[project]=[stim_id]
        
        # 
        pipeline = [ 
                        {"$group": { "_id": { "stim_id": "$stim_id"} , "count": {"$sum": 1}}},
                        {"$match": { "count": {"$gt": 1}}}
                   ]
        
        cursor=db.megameta.codes.aggregate(pipeline)
        
        completed = [i['_id']['stim_id'] for i in cursor]
        
        filter_ids = []
        for _, v in coded_stims.items():
            filter_ids.extend(v)
        
        to_code = gs.get_stim_ids(filter=filter_ids+completed)
        
        
        sample = []
        for ids in to_code.values():
            sample.extend(ids)
        
        sample_size = min(5, len(sample))
        
        sample5 = random.sample(sample, sample_size)
        
        if len(sample5)<1:
            sample_url = None if len(sample5)==0 else '/codestim/{}?next={}'.format(sample5[0])
        else:
            sample_url = '/codestim/{}?next={}'.format(sample5[0], ','.join(sample5[1:]))
            
        return render_template('main.html',
                              user=user,
                              coded_cnt = coded_cnt,
                              coded_stims = coded_stims,
                              to_code = to_code,
                              random_sample_url = sample_url
                            
                              )

    
    

    @app.route('/codestim/<stim_id>', methods=['GET'])
    def codestim(stim_id):
        
        aaa.require(fail_redirect='/login')      
        
        user = aaa.current_user
        
        next = request.args.get("next",0)

        if next:
            next_list = next.split(',')
            
        
        project, sid = stim_id.split('-')
        
        stim_html = get_stimuli(project, sid)
        
        return render_template('code_stim.html', 
                               stim_id=stim_id, 
                               user=user, next=next,
                               stim_html=stim_html)



    
    

    # serve stimuli
    @app.route('/get_stimuli/<project>-<stim_id>', methods=['GET'])
    def get_stimuli(project, stim_id):
        print(project, ' - ', stim_id)
        return gs.get_stim(project, stim_id)

    


    @app.route('/codes/<project>-<stim_id>', methods=['GET', 'POST'])
    def get_codes(project, stim_id):

        uid = request.args.get("uid")

        full_stim_id = "{}-{}".format(project,stim_id)
        print(full_stim_id)
        codes = db.megameta.codes

        res = codes.find_one({'uid': uid, 'stim_id': full_stim_id})
        print('RESULT', res)

        if not res:
           res={'uid': uid, 'stim_id': full_stim_id, 'data': {}}
        else:
           del(res['_id'])

        if request.method=='POST':
            post_data = request.get_json()
            res['data'] = { k:v for k,v in post_data.items() if k not in ['uid', 'stim_id', 'data', '_id']}
            res['last_modified'] = datetime.datetime.utcnow()
            print('POST data:', res)
            try:
               result = codes.replace_one(
                  {'uid': uid, 'stim_id': full_stim_id},
                  res,
                  upsert=True
               )
               print('UPDATED', result.modified_count)
            except(Exception, e):
               print(e)

            return json_util.dumps(res)
        else:
            return json_util.dumps(res)


    @app.route('/get_codes_for/<uids>', methods=['GET'])
    def get_codes_for_user(uids):

        data = []
        
        log_filename = request.args.get("filename", "log.csv")
        
        log_filename = log_filename if log_filename.endswith('.csv') else log_filename + '.csv'

        for uid in uids.split('|'):
            data.extend(gc.get_codes_for(uid, db))

        try:
            cdf=pd.io.json.json_normalize(data)
            
            # rename columns
            
            cdf.sort_values('stim_id', inplace=True)
            buffer = StringIO()
            csvfile = cdf.to_csv(buffer, encoding='utf-8', index=False) 


            response = Response(buffer.getvalue(), mimetype='text/csv')
            response.headers.set("Content-Disposition", "attachment", 
                                 filename=log_filename)
            return response

        except:
            return None




    # serve media
    @app.route('/media/<path:mpath>', methods=['GET'])
    def serve_static(mpath):
        print(mpath)
        media_path = os.path.join(STATIC_ROOT, mpath)
        if os.path.exists(media_path):
            return send_from_directory(STATIC_ROOT, mpath)
        else:
            return None

    @app.route('/<jpath>_json', methods=['GET'])
    def get_survey2(jpath):
        print(jpath)
        json_mapping = {
            'descriptions': 'code_description',
            'survey': 'survey_items_with_desc'
        }
        
        # combine code_description items into survey JSON
        
        if jpath=='survey':
            survey = json.load(open('survey_items.json'))
            desc = json.load(open('code_description.json'))
            
            table_template = '<table><thead><th>Value</th><th>Description</th></thead><tbody>{}</tbody></table>'
            row_template = '<tr><td>{val}</td><td>{desc}</td></tr>'

            var_dict = {}
            for var in desc:
                html = table_template.format('\n'.join([row_template.format(**d) for d in var['values']]))
                var_dict[var['variable']]=html
            

            for page in survey['pages']:
                for item in page['elements']:
                    name = item['name']
                    if var_dict.get(name):
                        item['popupdescription']=var_dict.get(name)
                            
            return jsonify(survey)
        
        else:
            return send_from_directory('.','{}.json'.format(json_mapping[jpath]))

    
    return app

# --- MAIN ----
    
if __name__ == '__main__':
    
    app = create_app()
    app.secret_key = os.urandom(24)
    
    STATIC_ROOT='../../stimuli'
    
    db = pymongo.MongoClient()
    
    print(db)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

