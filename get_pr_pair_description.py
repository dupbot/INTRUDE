import git
import json

#-------- dup PR pairs (from MSR) --------
# file_positive = 'data/msr_positive_pairs.txt'
# out = open(file_positive + '.out', 'w')

# with open(file) as f:
#     for l in f.readlines():
#         repo,num1,num2 = l.split()

#         p1 = git.get_pull(repo, num1)
#         p2 = git.get_pull(repo, num2)

#         data = {}
#         data['dupPR'] = []
#         data['dupPR'].append({
#             'pr1.url': p1["url"],
#             'pr2.url': p2["url"],
#             'pr1.title': p1["title"],
#             'pr1.desc': p1["body"]or '',
#             'pr2.title': p2["title"],
#             'pr2.desc': p2["body"]or '',
#             'isDup': 'true'
#         })
#         with open('data/prPairs_title_desc.txt', 'a') as outfile:
#             json.dump(data, outfile,indent=2)

# out.close()

#-------- Non-dup PR pairs (randomly sampled) --------
file_negative_arr = ['data/trainset_only_merge_neg.txt',"data/clf/first_nondup.txt"]
for file_neg in file_negative_arr:
    out_neg = open(file_neg + '.out', 'w')

    with open(file_neg) as f:
        for l in f.readlines():
            repo,num1,num2 = l.split()
            p1 = git.get_pull(repo, num1)
            p2 = git.get_pull(repo, num2)

            data = {}
            data['dupPR'] = []
            data['dupPR'].append({
                'pr1.url': p1["url"],
                'pr2.url': p2["url"],
                'pr1.title': p1["title"],
                'pr1.desc': p1["body"]or '',
                'pr2.title': p2["title"],
                'pr2.desc': p2["body"]or '',
                'isDup': 'false'
            })
            with open('data/nondup_prPairs_title_desc.txt', 'a') as outfile:
                json.dump(data, outfile,indent=2)

    out_neg.close()