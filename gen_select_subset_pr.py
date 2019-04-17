import os
import sys
from git import *
from sklearn.utils import shuffle

getConsecutivePRPairs_flag = True

# repo_type = 'training'  # 'testing'
repo_type = 'testing'
all_repos = ['mozilla-b2g/gaia', 'twbs/bootstrap', 'scikit-learn/scikit-learn', 'rust-lang/rust', 'servo/servo',
             'pydata/pandas', 'saltstack/salt', 'nodejs/node', 'symfony/symfony-docs', 'zendframework/zf2',
             'symfony/symfony', 'kubernetes/kubernetes', 'cocos2d/cocos2d-x', 'dotnet/corefx', 'django/django',
             'angular/angular.js', 'JuliaLang/julia', 'ceph/ceph', 'joomla/joomla-cms', 'facebook/react',
             'hashicorp/terraform', 'rails/rails', 'docker/docker', 'elastic/elasticsearch', 'emberjs/ember.js',
             'ansible/ansible']

if (repo_type == 'training'):
    print("randomly pick a repo...")
    # repos = ['mozilla-b2g/gaia']
    repos = ['mozilla-b2g/gaia', 'twbs/bootstrap', 'scikit-learn/scikit-learn', 'rust-lang/rust', 'servo/servo',
             'pydata/pandas', 'saltstack/salt', 'nodejs/node', 'symfony/symfony-docs', 'zendframework/zf2',
             'symfony/symfony', 'kubernetes/kubernetes']
else:  # testing repos
    print("randomly pick a repo...")
    # repos = ['cocos2d/cocos2d-x']
    repos = ['cocos2d/cocos2d-x', 'dotnet/corefx', 'django/django', 'angular/angular.js', 'JuliaLang/julia',
             'ceph/ceph',
             'joomla/joomla-cms', 'facebook/react', 'hashicorp/terraform', 'rails/rails', 'docker/docker',
             'elastic/elasticsearch', 'emberjs/ember.js', 'ansible/ansible']

# get Duplicate PR pairs from MSR Dataset
msr_pr_pair = set()
msr_repo_prList_map = {k: [] for k in all_repos}

with open('data/msr_positive_pairs.txt') as f:
    for t in f.readlines():
        #         print(t)
        r, n1, n2 = t.split()
        if r in all_repos:
            msr_pr_pair.add((r, n1, n2))
            msr_repo_prList_map[r].append(n1)
            msr_repo_prList_map[r].append(n2)

gen_num = 0


def getConsecutiveNonDupPRPairs(repo, prID):
    # get all pr
    pull_list = get_repo_info(repo, 'pull')
    pull_list = list(filter(lambda x: (int(x['number']) < int(prID)), pull_list))
    pull_list = sorted(pull_list, key=lambda x: int(x['number']), reverse=True)
    pull_list = pull_list[:10]
    pull_list = [x['number'] for x in pull_list]
    pr_pair_list = []
    for old_pr in pull_list:
        old_pr = str(old_pr)
        if (repo, prID, old_pr) not in msr_pr_pair and (repo, old_pr, prID) not in msr_pr_pair:
            pr_pair_list.append((repo, prID, old_pr))
        else:
            print(repo + ',' + prID + ',' + old_pr + ' is duplicate')
    return pr_pair_list


def work(file):
    add_flag = False

    has = set()
    if os.path.exists(file):
        if not add_flag:
            raise Exception('file already exists!')
        with open(file) as f:
            for t in f.readlines():
                r, n = t.strip().split()
                has.add((r, n))

    for repo in repos:
        print('Generating PRs from', repo)

        for msr_pr in msr_repo_prList_map[repo]:
            print('current pr in MSR:' + msr_pr)
            if getConsecutivePRPairs_flag:
                result = getConsecutiveNonDupPRPairs(repo, msr_pr)
                print(result)
                for pair in result:
                    with open(file, 'a') as f:
                        print("\t".join(pair), file=f)
            else:
                pulls = get_repo_info(repo, 'pull')
                ps = shuffle(pulls)

                cnt = 0
                with open(file, 'a+') as f:
                    for p in ps:
                        if check_large(p):
                            continue
                        if (repo, str(p['number'])) in has:
                            continue
                        cnt += 1
                        print(repo, p['number'], file=f)

                        if cnt == gen_num:
                            break


if __name__ == "__main__":
    if (len(sys.argv) == 1):
        file = 'data/consecutive_NonDupPR_pairs_' + repo_type + '.txt'
        gen_num = 100
    else:
        file = sys.argv[1].strip()
        gen_num = int(sys.argv[2].strip())

    print(file)
    print(gen_num)
    work(file)
