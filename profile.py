#-*- coding: utf-8 -*-
import re
import pickle
import os

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
    if (not recompute) and os.path.isfile(fn + '.pkl'):
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
'''
def test_occupy(ls, th):
    print occupy(ls, th)           
test_occupy([12, 14, 0, 8], 0.8)
'''
def get_trans_fre_mat(tasks_queue):
    """ get 
    """
    all_tasks = list(set(tasks_queue))
    store = {e1: {e2:0 for e2 in all_tasks} for e1 in all_tasks}

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


if __name__ == '__main__':
    import tableprint as tp
    for e1 in os.walk('./dataset'):
        for e2 in e1[2]:
            fn = os.path.join(e1[0], e2)
            data = load_tasks_queque(fn, recompute = False)
            if len(data) < 2: continue
            
            result = get_trans_fre_mat(data)
            if result == None: continue
            print '-' * 60
            tp.banner(fn)
            tp.table([result.values()], result.keys())
            '''
            get_trans_fre_mat(data[:len(data)/2])
            print '---------'
            get_trans_fre_mat(data[len(data)/2:])
            '''
            break # Only watch 1.txt from node 1


