import detect

detect.speed_up = True
detect.filter_larger_number = True
detect.filter_out_too_old_pull_flag = True
detect.filter_already_cite = False
detect.filter_create_after_merge = True
detect.filter_overlap_author = False
detect.filter_out_too_big_pull_flag = False
detect.filter_same_author_and_already_mentioned = True
detect.filter_version_number_diff = True


# For precision
outfile = 'evaluation/random_sample_select_pr_result_0424.txt'
with open(outfile, 'w') as outf:
    pass

cnt = 0

# with open('data/random_sample_select_pr.txt') as f:
with open('evaluation/random_sample_select_pr_result_labeled_by_authors.txt') as f:
    for t in f.readlines():
#         r, n1 = t.split()
        r, n1,n2,prob,result = t.split()
        cnt += 1
#         if (cnt <= 2114):
#             continue

        n2, proba = detect.detect_one(r, n1)        #returns the most similar pair (n1, n2) and probability that they are dups
        with open(outfile, 'a') as outf:
            print(r, n1, n2, proba, sep='\t', file=outf)


# For Recall
outfile = 'evaluation/msr_second_part_result_0424.txt'
with open(outfile, 'w') as outf:
    pass

with open('data/clf/second_msr_pairs.txt') as f:
    for t in f.readlines():
        r, pr1, pr2 = t.split()
        
        n1 = str(max(int(pr1), int(pr2)))
        
        n2, proba = detect.detect_one(r, n1)
        
        with open(outfile, 'a') as outf:
            print(r, n1, n2, proba, sep='\t', file=outf)
