from multiprocessing import Process,Queue
import dill
from math import *

dill.settings["recurse"]=True


#pass functions as dictionary of strings to lamdas(T)->T
#pass equation string of the form a^1b^3c^2=a^2

#pass check/clip functions of the form lamda(T)->bool
def backtrack(start, functions, check, clip, structure, depth,N):
	structureType=0
	if structureType==0:
		return _backtrackFull(start, functions,check,clip,depth,N)
		
#def _detect(eq, functions):
    
    
def _backtrackFull(start, functions,check,clip,depth,N):
    if N<1:
        raise Exception()
    
    disDepth=int(min(floor(log(N,len(functions))),depth))
    numSplit=int(len(functions)**disDepth)
   
    q=Queue(numSplit)
    data=["" for i in range(numSplit)]
    for i in range(numSplit):
        data[i]=dill.dumps({"start":start,"functions":functions,"check":check,"clip":clip,"depth":depth,"x":i,"disDepth":disDepth})
    ps=[Process(target=_backtrackFullHelperStart, args=(data[i],q)) for i in range(numSplit)]
    
    for i in range(numSplit):
        ps[i].start()
    
    result=[]    
    for i in range(numSplit):
        result=result+q.get()
          
    return result

def _backtrackFullHelperStart(dataString,q):
    data=dill.loads(dataString)
    start=data["start"]
    functions=data["functions"]
    check=data["check"]
    clip=data["clip"]
    depth=data["depth"]
    x=data["x"]
    disDepth=data["disDepth"]
    oppStack=_getPath(x,functions,disDepth)
    results=[]
    newStart=_applyPath(oppStack,start,functions,clip,check,results)
    results= results+_backtrackFullHelper(newStart,functions,check,clip,depth-disDepth,oppStack)
    q.put(results)
       

def _backtrackFullHelper(start, functions,check,clip,depth,oppstack):
    if clip(start):
        return []
    if check(start):
        return [{"path":oppstack,"node":start}]
    if depth==0:
        return[]
		
    result=[]
    for f in functions:
        newNode=functions[f](start)
        newOppStack=oppstack+[f]
        if clip(newNode):
            continue;
        result=result+_backtrackFullHelper(newNode,functions,check,clip,depth-1,newOppStack)	
    return result
	
def _applyPath(path,start,functions,clip,check,results):
    oppStack=[];
    result=start
    for x in path:	
        if clip(result):
            return ''
        if check(result):
            results=results+[{"path":oppStack,"node":result}]
        result=functions[x](result)
    oppStack=oppStack+[x] 
    return result

def _getPath(n,a,d):
	keys=[x for x in a.keys()]
	
	curr=n
	result=[]
	for i in range(d):
		result=result + [keys[int(curr)%int(len(keys))]]
		curr=curr//len(keys)
	return result
	
