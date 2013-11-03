# -*- coding: utf-8 -*-

import markdown
import os.path
import re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import json
import torndb
import tornado.httpclient
import MySQLdb

from tornado.options import define, options
import sys  
reload(sys)  
sys.setdefaultencoding('utf-8')  
# FSM 

keywords='keyword'
tables='datasource'
fields='FIELDS'
conditionkeys='condition'
rightValueHint='RIGHTVALUEHINT'
conditions_list=['LIKE','=']
logic="logic"
logics_list=['AND','OR']

yqltableaddr='http://192.241.238.206/'


define("mysql_host", default="127.0.0.1:3306", help="api database host")
define("mysql_database", default="tornadotest", help="tornado_api database name")
define("mysql_user", default="root", help="tornado_api database user")
define("mysql_password", default="gebookstore2012", help="tornado_api database password")

def getTables(exist_table_list):
    db = torndb.Connection(
            host=options.mysql_host, database='iculture',
            user=options.mysql_user, password=options.mysql_password)
    entries=db.query("show tables")
    resultJSON=[]
    tables=json.loads(json.dumps(entries))
    for table in tables:
        
        if(table['Tables_in_'+'iculture'] in exist_table_list):
            continue;
        tableJson='"'+yqltableaddr+table['Tables_in_'+'iculture']+'.xml" as ' +table['Tables_in_'+'iculture']+';'
        resultJSON.append(tableJson)
    db.close()
    
    return (resultJSON)

def getfields(table_name,if_pre_comma,if_condition,exist_field_list):
    db = torndb.Connection(
            host=options.mysql_host, database='iculture',
            user=options.mysql_user, password=options.mysql_password)
    print exist_field_list

    queryStr= "SHOW COLUMNS FROM %s" % (table_name)
    #print queryStr
    fields=json.loads(json.dumps(db.query(queryStr)))
    resultJson=[]
    if(len(exist_field_list)==0 and if_condition==False):
        resultJson.append("*")
    for field in fields:
            #print field['Field']  
        if('Info.'+field['Field'] in exist_field_list):
            continue;
        if(if_pre_comma):
            fieldJson=','+'Info.'+field['Field']
        else:
            fieldJson='Info.'+field['Field']
        resultJson.append(fieldJson)
    
    #print resultJson
    db.close()
    return ((resultJson))

def appendResult(currList,newRes):
    currList.append(newRes)

def appendType(hints, currList,keyType,previous):

    #{"title:"table_name","type":"table","previous":"anything that was sent to you before","description":"This table is for Govt data"}


    if(keyType in hints):
        result_list=hints[keyType]
        for resultElem in result_list:
            hint={}
            hint['previous']=previous
            hint['value']=resultElem
            hint['id']=resultElem
            hint['type']=keyType
            if(resultElem=='USE'):
                hint['description']='We usually start with the USE keyword to select data source'
            elif(resultElem.find('Protect')!=-1):
                hint['description']='消費者保護'
            elif(resultElem.find('communities')!=-1):
                hint['description']='文化設施-社區'
            elif(resultElem.find('scene')!=-1):
                hint['description']='文化設施-文化景觀'
            elif(resultElem.find('treasure')!=-1):
                hint['description']='文化設施-有形文化資產'
            elif(resultElem=='SELECT'):
                 hint['description']='SELECT is used to choose certain fields from the table you have named'
            elif(resultElem=='*'):
                 hint['description']='* all field'
            elif(keyType==fields):
                 hint['description']='Single Field'
            elif(resultElem=='FROM'):
                 hint['description']="FROM {tablename}"
            elif(resultElem=='FROM'):
                 hint['description']="FROM {tablename}"
            elif(resultElem=='WHERE'):
                 hint['description']="for specifying a condition"   
            elif(keyType== conditionkeys):
                hint['description']="a condition operator"
            elif(keyType== logic):
                hint['description']="Logic operator"
            elif(resultElem=='='):
                hint['description']="a condition operator" 
            elif(resultElem=="''" or resultElem == "'%%'"):
                hint['description']="Rightvalue hint" 
            elif(keyType==rightValueHint):
                 hint['description']="Rightvalue hint" 


            " a condition operator"
            currList.append(hint)
       


def getResultJson(hints,previous):
   
    result=[]
    appendType(hints,result,keywords,previous)
    appendType(hints,result,tables,previous)
    appendType(hints,result,fields,previous)
    appendType(hints,result,conditionkeys,previous)
    appendType(hints,result,rightValueHint,previous)
    appendType(hints,result,logic,previous)
    
    

    return result

def putHintDict(dict, hinttype,hintlist):
    dict[hinttype]=hintlist
    return dict

# this checks only string types.
def checkCondition(field, field_list,rightValue):
    if(field in field_list):
        if(len(rightValue)>0):
            return True
    else:
        return False
def getConditionSupport(cond,field_name,tablename):
    words= getSampleWords('SELECT '+field_name+' from '+tablename+' WHERE '+field_name+' IS NOT NULL limit 10',field_name)
    words=set(words)
    words=list(words)
    if(cond=='LIKE'):
        hints=[]
        hints.append("'%%'")
        for word in words:
            hints.append("'%"+word+"%'")
        return hints
    elif(cond=='='):
        return ["''"]
def handleJoinCondition(queryStrs,table_name,table_name2,queryStr):
    num_table=2

    if(num_table==2 ):
        #print 'start join'
        if(queryStrs.endswith('( ')  or queryStrs.endswith('(')):
            print 'start join here'
            print queryStrs
            target=queryStrs.split("(")[1]
            hintdict={}
            fields_list=findJoinFields(table_name,table_name2,False)
           
            return getResultJson(putHintDict(hintdict,fields,fields_list),queryStr)
        elif(queryStrs.endswith(') ')  or queryStrs.endswith(')')):
            print 'hint in'
            hintdict={}
            keywordList=['IN (']
            putHintDict(hintdict,keywords,keywordList)
            return getResultJson(hintdict,queryStr)
        else:
            print 'more '
            hintdict={}
            target=queryStrs.split("(")[1]
            print target
                
            hintdict={}
            keywordList=[')']
            putHintDict(hintdict,keywords,keywordList)
            fields_list=findJoinFields(table_name,table_name2,False)
            exist_fields=[]
            for f in fields_list:
                if(target.find(f)!=-1):
                    print 'exist!'
                    fields_list.remove(f)
            
               
            return getResultJson(putHintDict(hintdict,fields,fields_list),queryStr)


def selectFSM(queryStr):
    print "Input query String:" + queryStr


    # test if init state
    if(len(queryStr)==0):
        print "Current State: Init"
        hintdict={}
        keywordList=['USE']

        return getResultJson(putHintDict(hintdict,keywords,keywordList),queryStr)
    

    # test show_databases state

    if(queryStr=='USE'):
        print "Current State show_databases"
        hintdict={}
        #keywordList=['USE']
        #putHintDict(hintdict,keywords,keywordList)

        tables_result=getTables([]);
        putHintDict(hintdict,tables,tables_result)
      
        # http://192.241.238.206/testiculture.xml
        return getResultJson(hintdict,queryStr)
    
    # test choose_databases state

    queryStrs=queryStr.split(';')
    queryStrs[0]=queryStrs[0].replace('"','')
    table_name=queryStrs[0].split(yqltableaddr)
    table_name=table_name[1].split('.xml')
    table_name=table_name[0].replace(" ","").replace(".xml","")
    table_name2=''
    table_name1_ori=table_name
    # check if two tables
    num_table=1;
    #print queryStrs
    if(len(queryStrs)==3):
        num_table=2;
        table_name2=queryStrs[1].split(yqltableaddr)
        table_name2=table_name2[1].split('.xml')
        table_name2=table_name2[0].replace(" ","").replace(".xml","")


    print table_name
    print table_name2
    if(queryStr.endswith('USE')):
        if(num_table==1):
            hintdict={}

            tables_result=getTables([table_name]);
            final_table_result=[]
            
          
            for table in tables_result:
                print table
                tempTable =table.split('.xml')[0].replace('.xml','').replace(yqltableaddr,'').replace('"','')
                print tempTable
                if(len(findJoinFields(table_name,tempTable,True))!=0):
                    final_table_result.append(table)
            putHintDict(hintdict,tables,final_table_result)
            return getResultJson(hintdict,queryStr)

    if_sub=False;

    if(len(queryStrs)>=2):
        if(num_table==2):
            queryStrs[1]=queryStrs[2].replace('"','')
        else:
            queryStrs[1]=queryStrs[1].replace('"','')

        print "query=" + queryStrs[1]
        if(queryStrs[1].find('IN')!=-1):
            queryStrs[1]=queryStrs[1].split('IN (')[1]
            table_name=table_name2
            if_sub=True;
            print table_name
            
        # check if ends with (

        # only one database
        if queryStrs[1].find("SELECT") == -1:
            #print "no select"
            # Hint = SELECT , List of databases that are not selected yet
            hintdict={}
            
            if(num_table==1 ):
                hintdict={}
                final_table_result=[]
                tables_result=getTables([table_name]);
                print tables_result
                if(table_name=='gov_customerProtect'):
                    keywordList=['SELECT']
                    return getResultJson(putHintDict(hintdict,keywords,keywordList),queryStr)
                if_MORE_TABLE=True
                for table in tables_result:
                    print table
                    tempTable =table.split('.xml')[0].replace('.xml','').replace(yqltableaddr,'').replace('"','')
                    if(len(findJoinFields(table_name,tempTable,True))!=0):
                        if_MORE_TABLE=True
                        break;
                keywordList=[]
                print final_table_result
                if(if_MORE_TABLE):
                    keywordList=['USE','SELECT']
                else:
                    keywordList=['SELECT']
                return getResultJson(putHintDict(hintdict,keywords,keywordList),queryStr)
            else:
                hintdict={}
                keywordList=['SELECT']
                putHintDict(hintdict,keywords,keywordList)
                return getResultJson(hintdict,queryStr)


        elif(queryStrs[1]=='SELECT' or queryStrs[1]==' SELECT' or queryStrs[1]=='\tSELECT'):

            # NO fields have been specified yet.
            print 'field hint'
            hintdict={}
            if(num_table==2 and if_sub==True):
                fields_list=findJoinFields(table_name1_ori,table_name2,False)
            else:
                fields_list=getfields(table_name, False,False,[])
            return getResultJson(putHintDict(hintdict,fields,fields_list),queryStr)


        elif queryStrs[1].find("FROM") == -1:
            # select [* | [field_name]+]
            # choose_field state
            # hint: FROM, more fields

            
            splitstring=queryStrs[1].split("SELECT");
           
            if(len(splitstring)==2):
                print 'Handle adter select'
                query_field_list=splitstring[1]
                query_field_list=query_field_list.replace(' ','');
                # check if ==*
                if(query_field_list=='*'):
                    # return from 
                    hintdict={}
                    keywordList=['FROM']
                    putHintDict(hintdict,keywords,keywordList)
                    return getResultJson(hintdict,queryStr)

                query_field_list=query_field_list.split(',')
                # [field_name,]+
                hintdict={}
                keywordList=['FROM']
                putHintDict(hintdict,keywords,keywordList)
                print query_field_list
                
                fields_list=getfields(table_name, True,False, query_field_list)
                putHintDict(hintdict,fields,fields_list)
                return getResultJson(hintdict,queryStr)
           

        # now there's from
        select1=queryStrs[1].split("FROM")
        #print select1
        if(len(select1[1])==0):
            # suggest tables from use
            
            hintdict={}
            tableList=[table_name]
            putHintDict(hintdict,tables,tableList)
            return getResultJson(hintdict,queryStr)

        # select * | [field] + from table 

        elif select1[1].find('WHERE')== -1:
            # may be valid query now
            hintdict={}
            if(select1[1].endswith(')')):
                keywordList=['WHERE']
            elif(num_table==2 and if_sub==True):
                keywordList=[')','WHERE']
            else:
                keywordList=['WHERE']
            putHintDict(hintdict,keywords,keywordList)
            return getResultJson(hintdict,queryStr)

        else:
            # select * | [field]+ from table where e|[condition]+
            print 'select from where'

            whereclause=select1[1].split("WHERE")[1]
            print whereclause
            if(num_table==2 and (whereclause.find('(')==1 or whereclause.find(')')==1  ) and if_sub==False):
                print 'handle first where'
                return handleJoinCondition(whereclause,table_name,table_name2, queryStr)

            if(len(whereclause.replace(" ",''))==0):
                hintdict={}
                if(num_table==2 and if_sub==False):
                    keywordList=['(']
                    putHintDict(hintdict,keywords,keywordList)
                #print 'Suggest some fields'
                
                fields_list=getfields(table_name, False,True,[])
                return getResultJson(putHintDict(hintdict,fields,fields_list),queryStr)
                # table 2 here, complicated!
            conditions=whereclause.split(',')
            

            print conditions
            if(len(conditions)==1):
                target=conditions[0]
                hintdict={}

                for l in logics_list:
                    if(target.endswith(l+' ') or target.endswith(l)):
                        hintdict={}
                        fields_list=getfields(table_name, False,True,[])
                        exist_fields=[]
                        for f in fields_list:
                            if(target.find(f)!=-1):
                                exist_fields.append(f)
                        fields_list=getfields(table_name, False,True,exist_fields)
                        print 'gest '
                        return getResultJson(putHintDict(hintdict,fields,fields_list),queryStr)


                # check if target end with a field
                fields_list=getfields(table_name, False,True,[])
                for f in fields_list:
                    if(target.endswith(f+' ') or target.endswith(f)):
                       
                        print 'no condition yet'
                        
                        putHintDict(hintdict,conditionkeys,conditions_list)
                        return  getResultJson(hintdict,queryStr)
                        
                for c in conditions_list: 
                    if(target.endswith(c+' ') or target.endswith(c)):
                        splitstring=target.split(c)

                        putHintDict(hintdict,rightValueHint,getConditionSupport(c,splitstring[0].replace('WHERE','').replace('Info.','').replace(' ',''),table_name))
                        return  getResultJson(hintdict,queryStr)
            if(len(conditions[0].replace(' ',''))!=0):
                # and or
                hintdict={}
                print 'logic here'
                if(num_table==2 ):
                    hintdict={}
                    keywordList=[')']
                    putHintDict(hintdict,keywords,keywordList)
                return getResultJson(putHintDict(hintdict,logic,logics_list),queryStr)


            print 'Suggest some fields'
            print whereclause
            hintdict={}
            fields_list=getfields(table_name, False,True,[])
            exist_fields=[]
            for f in fields_list:
                if(whereclause.find(f)!=-1):
                    exist_fields.append(f)
            fields_list=getfields(table_name, False,True,exist_fields)

            return getResultJson(putHintDict(hintdict,fields,fields_list),queryStr)

            # check if valid condition
            # [field in table's field list] [=, like] [String lenth >0]

def getSampleWords(queryStr,fieldName):
    db = torndb.Connection(
            host=options.mysql_host, database='iculture',
            user=options.mysql_user, password=options.mysql_password)
    result=[]
    print 'to mysql:'+queryStr
    dbresult=[]
   
    dbresult=db.query(queryStr)
    for post in dbresult:
        word=post[fieldName]
        result.append(word[:2])
            

    return result

def ifCanJoin(tablename, tablename2):
    db = torndb.Connection(
            host=options.mysql_host, database='iculture',
            user=options.mysql_user, password=options.mysql_password)
    # select count(iculture_scene.cityName) as count from iculture_scene,iculture_treasure where iculture_scene.cityName=iculture_treasure.cityName
    #(table_name,if_pre_comma,if_condition,exist_field_list):
    table1FieldList=getfields(tablename,False,True,[]);
    table2FieldList=getfields(tablename2,False,True,[]);
    print 'SELECT COUNT('+tablename+'.'+table1FieldList[0]+') AS COUNT FROM '+tablename+','+tablename2+' WHERE '+tablename+'.'+table1FieldList[0].replace('Info.','')+'='+tablename2+'.'+table2FieldList[0].replace('Info.','')
    print db.query('SELECT COUNT('+tablename+'.'+table1FieldList[0].replace('Info.','')+')AS COUNT FROM '+tablename+','+tablename2+' WHERE '
        +tablename+'.'+table1FieldList[0].replace('Info.','')+'='+tablename2+'.'+table2FieldList[0].replace('Info.',''))
    result=[]
    for field1 in table1FieldList:
        for field2 in table2FieldList:
            num=db.query('SELECT COUNT('+tablename+'.'+field1.replace('Info.','')+')AS COUNT FROM '+tablename+','+tablename2+' WHERE '
        +tablename+'.'+field1.replace('Info.','')+'='+tablename2+'.'+field2.replace('Info.',''))[0].get('COUNT')
            #print num
            if(num>0):
                #print field1+ " "+field2
                return True
    return False

def findJoinFields(tablename, tablename2,if_determine):
    db = torndb.Connection(
            host=options.mysql_host, database='iculture',
            user=options.mysql_user, password=options.mysql_password)
    # select count(iculture_scene.cityName) as count from iculture_scene,iculture_treasure where iculture_scene.cityName=iculture_treasure.cityName
    #(table_name,if_pre_comma,if_condition,exist_field_list):
    table1FieldList=getfields(tablename,False,True,[]);
    table2FieldList=getfields(tablename2,False,True,[]);
    #print 'SELECT COUNT('+tablename+'.'+table1FieldList[0]+') AS COUNT FROM '+tablename+','+tablename2+' WHERE '+tablename+'.'+table1FieldList[0].replace('Info.','')+'='+tablename2+'.'+table2FieldList[0].replace('Info.','')
    db.query('SELECT COUNT('+tablename+'.'+table1FieldList[0].replace('Info.','')+')AS COUNT FROM '+tablename+','+tablename2+' WHERE '
        +tablename+'.'+table1FieldList[0].replace('Info.','')+'='+tablename2+'.'+table2FieldList[0].replace('Info.',''))
    result=[]

    for field1 in table1FieldList:
        for field2 in table2FieldList:
            num=db.query('SELECT COUNT('+tablename+'.'+field1.replace('Info.','')+')AS COUNT FROM '+tablename+','+tablename2+' WHERE '
        +tablename+'.'+field1.replace('Info.','')+'='+tablename2+'.'+field2.replace('Info.',''))[0].get('COUNT')
            #print num
            if(num>0):
                #print field1+ " "+field2
                result.append(field1)
                if(if_determine):
                    break;
    result=set(result)
    result=list(result)
    #print result
    return result;




def testMYSQL(queryStr):


    
    db = torndb.Connection(
            host=options.mysql_host, database='iculture',
            user=options.mysql_user, password=options.mysql_password)
    result=[]
    print 'to mysql:'+queryStr
    dbresult=[]
    if(queryStr.find('LIKE')!=-1):
        queryStr=queryStr.split('LIKE')
        tet=queryStr[1].replace(' ','').replace("'",'')
        dbresult=db.query(queryStr[0]+' LIKE %s',tet,)
           
    else:
        dbresult=db.query(queryStr)
    for post in dbresult:
        result.append(post)
            

    resultJson={}
    resultJson['result']=result
    
    return resultJson


def testQuery(queryStr):
    print 'Test String= '+queryStr
    print selectFSM(queryStr)
    print '-------------------------------'


def testFSM():
    print '-------------------------------'
    print 'Testing FSM...'
    print '-------------------------------'
    test=""
    #testQuery(test)
    test='USE'
    #testQuery(test)

    # test using two tables
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure;'+yqltableaddr+'iculture_scene.xml" as iculture_treasure;'
    #testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure;'+yqltableaddr+'iculture_scene.xml" as iculture_treasure; SELECT'
    #testQuery(test)

    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure;'
    #testQuery(test)
    

    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure;SELECT'
    #testQuery(test)
    
    # select fields from table
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT address'
    #testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT address, cityName'
    #testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT address, cityName FROM'
    #testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT address, cityName FROM iculture_treasure'
    #testQuery(test)

    # test where
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT * FROM iculture_treasure'
    #testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT * FROM iculture_treasure WHERE'
    testQuery(test)


    # select * from table 
    '''
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT *'
    testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT * FROM'
    testQuery(test)
    test='USE "'+yqltableaddr+'iculture_treasure.xml" as iculture_treasure; SELECT * FROM iculture_treasure'
    testQuery(test)
    
    '''
# end FSM