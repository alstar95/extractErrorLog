import os
import shutil
import re
from nltk.corpus import wordnet as wn

re_module = {"Yum":ur"error",
             "Httpd":ur"[\[]\d+[\]][:]",
             "MySQL":ur"\d\d[:]\d\d[:]\d\d",
             "PostgreSQL":ur"[\[]\d+[\]][:]"
            }
 
# "(+)" is for extra log
# "(-)" is for missing log
# "($)" is for similar but modified log
ErrorInfo = ["(+)", "(-)", "($)"]

theta = 0.8

def readfile(filepath):
    fp = open(filepath, 'r')
    fileread = fp.read()
    fp.close()
    return fileread

def writefile(content, filepath, di):
    fp = open(filepath, di)
    fp.write(content)
    return fp.close()

def containTime(sentence):
    result = 0
    words = sentence.split(' ')

    for word in words:
        regex=ur"\d\d[:]\d\d[:]\d\d" 
        if re.search(regex, word):
            result = 1
            
    return result

def readLog(path, software):
    content = readfile(path)
    sentences = content.split('\n')

    #sentencelist = []
    #for sen in sentences:
    #    if containTime(sen) == 1:
    #        sentencelist.append(sen)

    loglist = []
    for sen in sentences:
        regex = re_module[software]
        ha = re.split(regex, sen)
        if len(ha) > 1:
            loglist.append(ha[1])

    return loglist

def clearAddress(senten):
    res = []
    regex = ur"([/][a-zA-Z0-9])+"
    for s in senten:
        if re.search(regex, s):
            boring = True
        else:
            res.append(s)
    res = [s.lower() for s in res if len(s) > 0]

    splitter = re.compile("\\W")
    senten = []
    for word in res:
        ts = [s.lower() for s in splitter.split(word) if len(s) > 1]
        for s in ts:
            senten.append(s)
    
    return senten

def clearNumber(senten):
    res = []
    regex = ur"([0-9])+"
    for s in senten:
        if re.search(regex, s):
            boring = True
        else:
            res.append(s)
    res = [s.lower() for s in res if len(s) > 1]

    return res

def wordSimilar(word1, word2):

    if word1 == word2:
        return 1
    else:
        return 0
    
    myset = set("")

    for synset in wn.synsets(word1):
        for tn in synset.lemma_names():
            myset.add(tn.encode("utf-8"))

    myset.add(word1.lower())

    if word2.lower() in myset:
        return 1
    else:
        return 0

def getSimilar(senten1, senten2):
    numerator   = 0
    denominator = len(senten1)

    for word1 in senten1:
        for word2 in senten2:
            if wordSimilar(word1, word2) == 1:
                numerator = numerator + 1
                break

    return numerator/denominator

def getMatchDegree(senten1, senten2):
    #print senten1
    senten1 = senten1.split(' ')
    senten1 = clearAddress(senten1)
    senten1 = clearNumber(senten1)
    #print senten1

    #print senten2
    senten2 = senten2.split(' ')
    senten2 = clearAddress(senten2)
    senten2 = clearNumber(senten2)
    #print senten2

    value = 0.5 * getSimilar(senten1, senten2) + 0.5 * getSimilar(senten1, senten2)
    return value

def formatSentence(senten):
    senten = senten.split(' ')
    senten = clearAddress(senten)
    senten = clearNumber(senten)
    res = ""
    for word in senten:
        res = res + " " + word
    return res

def formatSentenceList(sentenlist):
    res = []
    for sen in sentenlist:
        sen = formatSentence(sen)
        res.append(sen)
    return res

def extractErrorLog(path, software):
    StandardPath = "./" + software + "_standard"
    StandardSequence = readLog(StandardPath, software)
    CheckSequence = readLog(path, software)

    StandardSequence = formatSentenceList(StandardSequence)
    CheckSequence = formatSentenceList(CheckSequence)

    print "--------- the standard log ---------"
    for llog in StandardSequence:
	print llog

    print "--------- the check log ---------"
    for llog in CheckSequence:
	print llog
    #return 

#get the software errorname
    tpath = path
    tpath = tpath.split('/')
    lev = len(tpath)
    errorname = tpath[lev-1]
    ResultPath = "./Result_" + software + "/" + errorname

##    print StandardSequence
##    print "\n"
    pl = 0
    StandardSequenceLength = len(StandardSequence)
    ExceptionLog = []
    for senten1 in CheckSequence:
        curpl = pl
        findflag = 0
        while(pl < StandardSequenceLength):
            senten2 = StandardSequence[pl]
            MatchDegree = getMatchDegree(senten1, senten2)
            if MatchDegree > theta:
                findflag = 1
                break
            else:
                pl = pl + 1
        print findflag
        if findflag == 0:
            pl = curpl
            newErrorLog = ErrorInfo[0] + senten1
            ExceptionLog.append(newErrorLog)
        else:
            if curpl == pl: continue
            print curpl,pl
            for i in range(curpl,pl):
                newErrorLog = ErrorInfo[1] + StandardSequence[i]
                ExceptionLog.append(newErrorLog)
            pl = pl + 1
    print "############ErrorLog############"

    print "excep len"
    print len(ExceptionLog)
    for ss in ExceptionLog:
        print ss
    return 
        

##extractLog('./PostgreSQL/authentication_timeout_entry_value_number_semantic_0' , 'PostgreSQL')
##extractLog('./Httpd/AcceptPathInfo_entry_value_boolean_semantic_1' , 'Httpd')
extractErrorLog('./MySQL/binlog_format_entry_value_enum_syntactic' , 'MySQL')

