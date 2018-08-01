#-*- coding: utf-8 -*-
import re
import pickle
import os
import statsmodels.tsa.stattools as ts

def load_tasks_queque(fn, recompute = False):
    """ loading tasks log from the fn file, watching log from Cooja.
    and if it is the first load, log file will be store the pickle file for quick reading at next.
    Args:
        fn: str
            name of log file from cooja
        recompute: bool
            if True, this will reload tasks log from log file from cooja, else from pickle file
    Retval:
        data: list
            tasks queue like ['0x0001', '0x0002', '0x000a', ...]
    """

    temp_fn = fn.split('.')
    if temp_fn[-1] == 'pkl':
        fn = '.'.join(temp_fn[:-1])
    
    if (not recompute) and os.path.isfile(fn + '.pkl'):
        print "\t\t\twhat fuck!!!"
        with open(fn+'.pkl', 'rb') as f:
            return pickle.load(f)

        
    with open(fn, 'r') as f:
        data = map(lambda e: re.findall('0x00[0-9a-f]{2}', e)[0], f.readlines())
        with open(fn+'.pkl', 'wb') as f1:
            pickle.dump(data, f1)
    return data


def occupy(ls, th=0.8):
    """ Calculate how many items occupy the number over the total `th`*sum(ls) in `ls`
    Args: 
        ls: list
        th(threshold): folat
    """
    assert len(ls) > 0, 'None of argument'
    assert sum(ls) > 0, 'argument list was error %s' % str(ls)
    ls = sorted(ls, reverse=True)
    total = sum(ls)
    count_sum = 0
    for i in range(len(ls)):
        count_sum += ls[i]
        if float(count_sum) / total > 0.8:
            return (float(i + 1) / len(ls), float(count_sum) / total)

def get_trans_fre_mat(tasks_queue):
    all_tasks = list(set(tasks_queue))
    store = {e1: {e2:0 for e2 in all_tasks} for e1 in all_tasks}

    for i in range(len(tasks_queue)-1):
        store[tasks_queue[i]][tasks_queue[i+1]] += 1
    return store

    
def occupy_feature(tasks_queue):
    """ get 
    """
    all_tasks = list(set(tasks_queue))
    store = get_trans_fre_mat(tasks_queue)

    for i in range(len(tasks_queue)-1):
        store[tasks_queue[i]][tasks_queue[i+1]] += 1
    all_trans = sum(map(lambda e: sum(e.values()), store.values()))
    
    # weight of each task based on the number of execution
    weights = {e: sum(store[e].values()) / float(len(tasks_queue)) for e in all_tasks}

    occupy_data = {e: None for e in all_tasks}
    for k, v in store.items():
        try:
            occupy_data[k] = occupy(v.values())
        except AssertionError:
            print 'assert error'
            return None
            
    #print occupy_data
    task_proportion = sum(map(lambda (kv): kv[1][0] * weights[kv[0]], occupy_data.items()))
    occupy_precentage = sum(map(lambda (kv): kv[1][1] * weights[kv[0]], occupy_data.items()))

    ''' Based on mean value without weight
    task_proportion = sum(map(lambda e: e[0], occupy_data.values())) / len(occupy_data.values())
    occupy_proportion = sum(map(lambda e: e[1], occupy_data.values())) /  len(occupy_data.values())
    '''
    return {'task': task_proportion, 'occupy': occupy_precentage, "tasks num": len(all_tasks)}

def tasks_sequence_split(tasks_sequence, n):
    each_len = int(round(len(tasks_sequence) / float(n)))
    return [tasks_sequence[i:i + each_len]
            for i in range(0, len(tasks_sequence), each_len)]

def choice_most_task(trans_mat, n):
    # get n task pair, the number of trans is most
    # fint hot pot task trans
    temp = []
    for e in trans_mat.values():
        temp += e.values()
    
    temp = sorted(temp, reverse=True)
    retval = []
    for k, v in trans_mat.items():
        for k2, v2 in v.items():
            if v2 in temp[:n]: retval.append((k, k2, v2))
    return retval
    

def check_adf(tasks_queue, pre_task, next_task, block=10):
    all_tasks = list(set(tasks_queue))

    splited_data = tasks_sequence_split(tasks_queue, block)
    stores = map(lambda e: get_trans_fre_mat(e), splited_data)
    #prob_trans = lambda e: float(e[pre_task][next_task])/ sum(e[pre_task].values())
    def prob_trans(e):
        if pre_task in e.keys():
            if next_task in e[pre_task].keys():
                if sum(e[pre_task].values()) > 0:
                    return float(e[pre_task][next_task])/ sum(e[pre_task].values())
        return None
    prob_serise = map(prob_trans, stores)

    # remove to those group(as a item in stores) have no `next_task ` or `pre_task`
    prob_serise = filter(lambda e: e != None, prob_serise)
    if len(prob_serise) > 2:
        print "\t\t\ndebug", prob_serise
        result =  ts.adfuller(prob_serise)
        print result
        return result
    else:
        print 'No data'
        return 'No data'
    

def conclusion(results):
    cnt_1 = 0
    cnt_5 = 0
    cnt_10 = 0
    results = filter(lambda e: e != 'No data', results)
    for e in results:
        print 'debug 12', e[0], e[4]['1%']
        if float(e[0]) < float(e[4]['1%']):
            cnt_1 += 1
    try:
        print '1%: ', float(cnt_1) / len(results), '\ntotal: ', len(results)
    except:
        print 'length of result is 0'

    


if __name__ == '__main__':
    ''' Zhang Te:
    Do not touch anything !!!!
    Only I am able to understand those codes. Contact me by paradoxt@gmail.com
    '''
    import tableprint as tp

    results = []
    for e1 in os.walk('./dataset'):
        for e2 in e1[2]:
            fn = os.path.join(e1[0], e2)
            #if 'RadioCountToLeds1/2.txt' not in fn: continue
            if '.pkl' in fn: continue
            data = load_tasks_queque(fn, recompute = True)
            if len(data) < 2: continue
            
            #result = occupy_feature(data)
            #if result == None: continue
            #print '-' * 60
            #tp.banner(fn)
            #tp.table([result.values()], result.keys())
            print '-' * 15, fn, '-' * 15
            hot_taskl_pair = choice_most_task(get_trans_fre_mat(data), 2)
            print hot_taskl_pair
            results.append(check_adf(data, hot_taskl_pair[0][0], hot_taskl_pair[0][1]))
            #print tasks_sequence_split(range(12), 3)
            print '\n\n'
            
            #break # Only watch 1.txt from node 1
    conclusion(results)
    

        
        


