import pandas as pd
import pymongo
import json

DEBUG=True

def get_codes_for(uid, db):
    '''
    query db.codes for documents
    with uid
    return as JSON
    '''
    
    cursor=db.megameta.codes.find({'uid':uid})

    if DEBUG:
        print(uid,cursor)
    
    data = []
    
    for r in cursor:
        del(r['_id'])
        data.append(r)
    
    if DEBUG:
        print(data)
    return data




