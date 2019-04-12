import os
import sys
from git import *
from sklearn.utils import shuffle



print("randomly pick a repo...")
training_repos = ['mozilla-b2g/gaia', 'twbs/bootstrap', 'scikit-learn/scikit-learn', 'rust-lang/rust', 'servo/servo', 'pydata/pandas', 'saltstack/salt', 'nodejs/node', 'symfony/symfony-docs', 'zendframework/zf2', 'symfony/symfony', 'kubernetes/kubernetes']

# testing repos
print("randomly pick a repo...")
testing_repos = ['cocos2d/cocos2d-x', 'dotnet/corefx', 'django/django', 'angular/angular.js', 'JuliaLang/julia', 'ceph/ceph',
         'joomla/joomla-cms', 'facebook/react', 'hashicorp/terraform', 'rails/rails', 'docker/docker',
         'elastic/elasticsearch', 'emberjs/ember.js', 'ansible/ansible']

# get Duplicate PR pairs from MSR Dataset
msr_pr_pair = set()
msr_repo_prList_map = {k: [] for k in training_repos}


with open('data/msr_positive_pairs.txt') as f:
    for t in f.readlines():
        print(t)
        r, n1, n2 = t.split()
        if r in training_repos:
            msr_pr_pair.add((r, n1, n2))
            msr_repo_prList_map[r].append(n1)
            msr_repo_prList_map[r].append(n2)

gen_num = 0


def f(r, n):
    l = get_repo_info(r, 'pull')
    l = list(filter(lambda x: int(x['number']) < int(n), list))
    l = sorted(l, key=lambda x: n - x['number'], reverse=True)
    l = l[:100]
    l = [x['number'] for x in l]
    return [(n, x) for x in l]


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
    file = sys.argv[1].strip()
    gen_num = int(sys.argv[2].strip())

    work(file)
