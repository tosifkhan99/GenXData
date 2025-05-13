from utils.date_generator import generate_random_date
from numpy.random import shuffle

def distributed_date(**kwargs):
    
    df = kwargs.get('df')
    col_name = kwargs.get('col_name')
    rows = kwargs.get('rows')
    null_mask = kwargs.get('mask',False) & df[col_name].isnull()

    params = kwargs.get('params')
    total = 0
    for i in params:
        total += i['distribution']

    if total != 100:
        print("Error : Invalid distribution given, distributions sum should be equal to 100, but got {}".format(total))
        return df
    
    else:
        generated = []
        for i in params:
            for _ in range(int(i['distribution']/100*rows)):
                generated.append(generate_random_date(start_date=i['start_date'], end_date=i["end_date"]))
        shuffle(generated)

    if kwargs.get('operation') == "insert":
        df[col_name] = generated
    elif kwargs.get('operation') == 'insert_if_empty':
        # df.loc[null_mask, colName] = generated
        print(len(generated),null_mask.sum())
    return df