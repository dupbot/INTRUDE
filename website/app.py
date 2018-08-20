import sys
import os

sys.path.append('/home/luyao/PR_get/INTRUDE')
import git

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/intrude_db"
app.config["SECRET_KEY"] = "build_the_intrude_tool"

mongo = PyMongo(app)

debug_flag = False
read_only_mode = False

def load_new_dup(data):
    _id = data['repo'] + '/' + data['num']

    ori = mongo.db.detect.find_one({'_id': _id})

    mongo.db.detect.update({'_id': _id}, {'$set': data}, upsert=True)
    
    new_insert_flag = True
    conflict_flag = False
    
    if ori is not None:
        new_insert_flag = False
    
    if (ori is not None) and (ori.get('mark', '') != ''): # original one has mark
        # 1. dup pairs has changed.
        # 2. ori mark is different from this mark.
        if (ori['num2'] != data['num2']) or (('mark' in data) and (ori.get('mark') != data.get('mark'))):
            conflict_flag = True
            mongo.db.detect.update({'_id': _id},
                                   {'$set': {'mark': '%s_Conflict(%s,%s)' %\
                                                     (data.get('mark', ''), ori['num2'], ori.get('mark', '')), }})
    return (new_insert_flag, conflict_flag)
    

@app.route('/random_add', methods=['GET', 'POST'])
def random_add():
    repo = request.args.get('repo').strip()
    flash('Start analyzing %s! Please load later.' % repo, 'info')
    return jsonify('success')


@app.route('/delete/<path:repo>')
def delete(repo):
    if read_only_mode:
        return 'Can\'t delete. Read Only Mode.'

    mongo.db.detect.remove({'repo': repo})
    return 'done!'


@app.route('/load/<path:repo>')
def load(repo):
    if read_only_mode:
        return 'Can\'t load. Read Only Mode.'

    sheet_path = '/home/luyao/PR_get/INTRUDE/evaluation/' + \
                 repo.replace('/','_') + '_stimulate_top1_sample200_sheet.txt'
    if not os.path.exists(sheet_path):
        return 'not found!'
    
    new_insert_cnt, conflict_cnt = 0, 0
    with open(sheet_path) as f:
        for t in f.readlines():
            l = len(t.strip().split())
            
            if l == 14:
                r, n1, n2, proba, pre, status, s1, s2, s3, s4, s5, s6, l1, l2 = t.strip().split()
            else:
                r, n1, n2, proba, status, s1, s2, s3, s4, s5, s6, l1, l2 = t.strip().split()
            
            data = {
                 'repo': r,
                 'num': n1,
                 'num2': n2,
                 'proba': proba,
                 'type': 'same_repo',
                 'sim': {
                     'title': s1,
                     'desc': s2,
                     'code': s3,
                     'file_list': s4,
                     'location': s5,
                     'pattern': s6,
                 },
                 'sim_vet': [s1, s2, s3, s4, s5, s6]
            }
            
            if status != 'N/A':
                data['mark'] = status
            
            new_insert_flag, conflict_flag = load_new_dup(data)
            if new_insert_flag:
                new_insert_cnt += 1
            if conflict_flag:
                conflict_cnt += 1
    
    flash('Load successfully! New insert %d. Have %d merge conflict(s)!' % (new_insert_cnt, conflict_cnt), 'info')
    return redirect(url_for('prdashboard', repo=repo))


@app.route('/mark', methods=['GET', 'POST'])
def mark():
    repo = request.args.get('repo').strip()
    num = request.args.get('num').strip()
    choice = request.args.get('choice').strip()
    
    if not (repo and num):
        raise Exception('params error!')
    
    _id = repo + '/' + num
    
    if choice == 'C':
        comment = request.args.get('input').strip()
        mongo.db.detect.update({'_id': _id}, {'$set': {'comment': comment,}}, upsert=True)
        return jsonify(mongo.db.detect.find_one({'_id': _id})['comment'])
    else:
        if choice == 'unknown':
            mark = ''
        else:
            mark = choice
        mongo.db.detect.update({'_id': _id}, {'$set': {'mark': mark,}}, upsert=True)
        return jsonify(mongo.db.detect.find_one({'_id': _id})['mark'])



@app.route('/db/<path:repo>', methods=['GET', 'POST'])
def prdashboard(repo):
    # pull_list = mongo.db.pull_list.find({'repo_name': repo})
    pull_list = git.get_repo_info(repo, 'pull')
    pull_dict = {}
    for x in pull_list:
        pull_dict[str(x['number'])] = x
        
    dup_list = mongo.db.detect.find({'repo': repo})
    
    '''
    for dup in dup_list:
        num1 = dup['num']
        num2 = dup['num2']
        if (num2 in git.get_another_pull(pull_dict[num1])) or (num1 in git.get_another_pull(pull_dict[num2])):
            pull_dict[num1]['mention'] = 'Yes'
    '''
    
    return render_template('prdashboard.html', repo=repo, dup_list=dup_list, pull_dict=pull_dict)


@app.route('/')
def index():
    repo_list = mongo.db.detect.distinct('repo')
    return render_template('index.html', repo_list=repo_list)


@app.route('/export_mark')
def export_mark():
    mark_list = mongo.db.detect.find({'mark': {'$ne': None}})
    '''
    for x in mark_list:
        try:
            t = (x['repo'], x['num'], x['num2'], x['mark'])
        except:
            mongo.db.detect.remove(x)
            return x
    '''
    ret = [(x['repo'], x['num'], x['num2'], x.get('mark'), x.get('comment')) for x in mark_list]
    return jsonify(ret)


import detect
detect.simulate_mode = False

def get_state(git_pull):
    if git_pull['merged_at'] is not None:
        return 'merged'
    else:
        return git_pull['state']
    
def update_one_openpr(pull):
    if pull and ('repo' in pull) and ('num' in pull):
        num2, proba = detect.detect_one(pull['repo'], pull['num'])
        git_pull = git.get_pull(pull['repo'], num2)
        data = {'num2': num2, 'proba': proba, 'title2': git_pull['title'], 'link2': git_pull['html_url'], 'state2': get_state(git_pull), }
        mongo.db.openpr.update({'_id': pull['_id']}, {'$set': data}, upsert=True)

@app.route('/detect_openpr_all', methods=['GET', 'POST'])
def detect_openpr_all():
    repo = request.args.get('repo').strip()
    if not (repo):
        raise Exception('params error!')

    openpr = mongo.db.openpr.find({'repo': repo})
    for pull in openpr:
        update_one_openpr(pull)
    updated_openpr = list(mongo.db.openpr.find({'repo': repo}))
    return jsonify(updated_openpr)

@app.route('/detect_openpr', methods=['GET', 'POST'])
def detect_openpr():
    repo = request.args.get('repo').strip()
    num = request.args.get('num').strip()
    if not (repo and num):
        raise Exception('params error!')

    pull = mongo.db.openpr.find_one({'repo': repo, 'num': num})
    update_one_openpr(pull)
    updated_pull = dict(mongo.db.openpr.find_one({'repo': repo, 'num': num}))
    return jsonify(updated_pull)

@app.route('/openprdb/<path:repo>')
def openprdb(repo):
    try:
        openpr = git.api.request('GET', 'repos/%s/pulls?state=open' % repo, True)
    except:
        return 'Not Found!'

    for git_pull in openpr:
        num = str(git_pull['number'])
        _id = repo + '/' + num
        data = {'repo': repo, 'num': num, 'title': git_pull['title'], 'link': git_pull['html_url'], 'state': get_state(git_pull), }
        mongo.db.openpr.update({'_id': _id}, {'$set': data}, upsert=True)

    pr_list = mongo.db.openpr.find({'repo': repo})
    return render_template('openpr.html', repo=repo, pr_list=pr_list)

@app.route('/openpr')
def openpr():
    return render_template('openpr_welcome.html')
    
	
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, threaded=True, debug=debug_flag)
