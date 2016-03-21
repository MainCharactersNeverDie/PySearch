from multiprocessing import Process,Queue
import dill
import re
from math import *

dill.settings["recurse"]=True


#pass functions as dictionary of strings to lamdas(T)->T
#pass equation string of the form a^1b^3c^2=a^2

#pass check/clip functions of the form lamda(T)->bool
def backtrack(start, functions, check, clip, structure, depth,N):
    structure=_removeWeirdEquations(structure)
    
    if len(structure)==0:
        return _backtrackFull(start, functions,check,clip,depth,N)
    
    searchPlan=_getPlan(functions,structure)
    return _exicute(searchPlan, start, check, clip, depth, N)
 
#Ignores any equations that are more complex than linear
#result that is returned is the equations parsed into hash maps

#linear equations, ((y)=(x)^m)  are in hash maps of the form 	
#   {"type":"linear","x":x,"y":y,"m":LeftExponenet}

#constant equations (0=a^m) or ((a)=(a)^m) are in hash maps of the form
#   {"type":"constant","base":m,"var":a}

#replacement equations (x=y) are of the form
#   {"type":"replace","x":LeftVar,"y":RightVar}
def _removeWeirdEquations(structure):
    result=[]
    for eq in structure:
        sides=eq.split("=");
        LeftTerms=re.findall("\(\w*\)",sides[0])
        RightTerms=re.findall("\(\w*\)",sides[1])

        if len(LeftTerms)>1 or len(RightTerms)>1:
            continue

        if len(LeftTerms)==0 and len(RightTerms)==0:
            continue
        
        if len(LeftTerms)==0 or len(RightTerms)==0:
            swaped=False
            if len(LeftTerms)==0:
                temp=RightTerms
                RightTerms=LeftTerms
                LeftTerms=temp
                swaped=True

            if len(LeftTerms)==0:
                continue
            
            if swaped:
                LeftExponentString=re.split("\(\w*\)",sides[1])[1]
            else:
                LeftExponentString=re.split("\(\w*\)",sides[0])[1]

    
            if LeftExponentString=="":
                LeftExponent=1
            else:
                LeftExponent=int(LeftExponentString[1:])


            if len(RightTerms)==0:
                result=result+[{"type":"constant","base":LeftExponent,
                                        "var":LeftTerms[0][1:-1]}]
                continue

        LeftExponentString=re.split("\(\w*\)",sides[0])[1]

        RightExponentString=re.split("\(\w*\)",sides[1])[1]
    
        if LeftExponentString=="":
            LeftExponent=1
        else:
            LeftExponent=int(LeftExponentString[1:])

        if RightExponentString=="":
            RightExponent=1
        else:
            RightExponent=int(RightExponentString[1:])

        LeftVar=LeftTerms[0]
        RightVar=RightTerms[0]

        if LeftVar==RightVar:
            if LeftExponent==RightExponent:
                continue
            result=result+[{"type":"constant",
                "base":max(LeftExponent,RightExponent),"var":LeftVar[1:-1]}]
        elif LeftExponent==1 and RightExponent==1:
            result=result+[{"type":"replace","x":LeftVar,"y":RightVar}]
        elif LeftExponent==1 or RightExponent==1:
            if LeftExponent==1:
                result=result+[{"type":"linear",
                        "x":LeftVar[1:-1],"y":RightVar[1:-1],"m":RightExponent}]
            else:
                result=result+[{"type":"linear","x":RightVar[1:-1],
                        "y":LeftVar[1:-1],"m":LeftExponenet}]
    return result

#This function makes a plan seperating the functions with constant order
def _getPlan(functions,structure):
    consts=[]
    frees={}

    constantFunctions={}
    
    for s in structure:
        if s["type"]=="constant":
            consts=consts+[{"function":functions[s["var"]],"order":s["base"]}]
            constantFunctions[s["var"]]=True

    for f in functions:
        if f not in constantFunctions:
            frees[f]=functions[f]

    return {"frees": frees, "consts":consts}

#This is the main exicuter of the search plan.  It calculates the plan
#distributes it, and collects the results
def _exicute(searchPlan, start, check, clip, depth, N):
    if N<1:
        raise Exception()
   
    disDepth=1
     
    #number of nodes in a k-demnsional tree is (k**(N+1)-1)//(1-k)
    if len(searchPlan["frees"])>1:
        while ((len(searchPlan["frees"])**(disDepth+2)-1)//(len(searchPlan["frees"])))<N:
           # print (len(searchPlan["frees"])**(disDepth+2)-1)//(disDepth)
           # print len(searchPlan["frees"])
            disDepth=disDepth+1
    else:
        disDepth=N

    disDepth=min(disDepth,depth)
    
    if len(searchPlan["frees"])==1:
        numSplit=disDepth
    q=Queue(numSplit)
    
    #We have to pre-pickle since python pickling doesn't do lambdas
    data=["" for i in range(numSplit)]
    for i in range(numSplit):
        data[i]=dill.dumps({"start":start,"check":check,"clip":clip,
                        "depth":depth,"searchPlan":searchPlan,"x":i,"disDepth":disDepth})
    ps=[Process(target=_exicuteHelperStart, args=(data[i],q)) for i in range(numSplit)]

    for i in range(numSplit):
        ps[i].start()

    result=[]
    
    for i in range(numSplit):
        result=result+q.get()

    return result

#un pickles the data, and set up for the revcursive search
def _exicuteHelperStart(dataString,q):
    data=dill.loads(dataString)
    start=data["start"] 
    check=data["check"]
    clip=data["clip"]
    depth=data["depth"]
    searchPlan=data["searchPlan"]
    x=data["x"]
    disDepth=data["disDepth"]
    results=[]
    oppStack=_getFullPath(x,searchPlan["frees"])
    newStart=_applyPath(oppStack,start,searchPlan["frees"],clip,check,results)
    results=results+_exicuteHelper(oppStack,newStart,check,clip,depth-len(oppStack),
                                  searchPlan,_isOuter(x,searchPlan["frees"],disDepth),"")
    q.put(results)

#Returns whether this is the outer most part of the distribution so the threads
#know if they need to search outward or just through the constants
def _isOuter(x,functions,depth):
    d=0
    nodesAtDepth=1
    while x>=nodesAtDepth:
        x=x-nodesAtDepth
        nodesAtDepth=nodesAtDepth*len(functions)
        d=d+1
    return d==depth

#Recursive meathod doing backtracking but with optimizations for the constants
#"bench" is a the last constant uses (if the last thing was a constant)  this 
#reduces redundency
def _exicuteHelper(oppStack,start,check,clip,depth,searchPlan,isOuter,bench):
    
    #handle easy cases
    if clip(start):
        return []
    if check(start):
        return [{"path":oppStack,"node":start}]
    if depth<=0:
        return []

    #go through all the consants and search through their space
    result=[]
    for const in searchPlan["consts"]:
        if const==bench:
            continue
        f=const["function"]
        o=const["order"]
        newNode=start
        newOppStack=oppStack
        for i in range(o):
            newNode=f(newNode)
            newOppStack=oppStack+[newOppStack]
            result=result+_exicuteHelper(newOppStack,newNode,check,
                                            clip,depth-i-1,searchPlan,True,const)
    
    #if we are on the outer ring of the first layer of distribution or are
    #on higher layers
    if isOuter:
        for f in searchPlan["frees"]:
            newNode=functions[f](start)
            newOppStack=oppStack+[f]
            result=result+_exicuteHelper(newOppStack,newNode,check,
                                            clip,depth-1,searchPlan,True,"")
    return result
        

#Traslates the number for this process into a unique node that this
#process is responsible for searching
def _getFullPath(x,functions):
    d=0
    nodesAtDepth=1
    while x>=nodesAtDepth:
        x=x-nodesAtDepth
        nodesAtDepth=nodesAtDepth*len(functions)
        d=d+1

    return _getPath(x,functions,d)



#This backtrack Methods below are called when no other structure exists
#These distribute the load only along the leaf nodes whereas the other
#alogorithm distributes over all nodes.
def _backtrackFull(start, functions,check,clip,depth,N):
    if N<1:
        raise Exception()
            
    disDepth=int(min(floor(log(N,len(functions))),depth))
    numSplit=int(len(functions)**disDepth)
   
    q=Queue(numSplit)
    data=["" for i in range(numSplit)]
    for i in range(numSplit):
        data[i]=dill.dumps({"start":start,"functions":functions,
                  "check":check,"clip":clip,"depth":depth,"x":i,"disDepth":disDepth})
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
    results= results+_backtrackFullHelper(newStart,functions,check,
                                            clip,depth-disDepth,oppStack)
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
    
