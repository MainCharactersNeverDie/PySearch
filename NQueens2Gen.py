import backtrackPar as search
import copy
 
#N Queens
n=5

def moveQueenDown(board, n):
    board=copy.deepcopy(board)
    index=-1
    for j in range(n):
        if board["board"][j][board['col']]==1:
            index =j
    
    board["board"][index][board['col']]=0
    board["board"][(index+1)%n][board['col']]=1
    return board

def shiftCol(board):
    board=copy.deepcopy(board)
    board['col']=board['col']+1
    return board

def checkCollisions(board,n):
    for i in range(n):
        for j in range(n):
            if board['board'][i][j]==1:
                for k in range(n):
                    if k==j: 
                        continue
                    if board['board'][i][k]==1:
                        return True
                for k in range(n):
                    if k==i:
                        continue
                    if board['board'][k][j]==1:
                        return True
                for k in range(1,n):
                    if i-k<0 or j-k<0 :
                        continue
                    if board['board'][i-k][j-k]==1:
                        return True
                for k in range(1,n):
                    if i-k<0 or j+k>=n :
                        continue
                    if board['board'][i-k][j+k]==1:
                        return True
                for k in range(1,n):
                    if i+k>=n or j+k>=n :
                        continue
                    if board['board'][i+k][j+k]==1:
                        return True
                for k in range(1,n):
                    if i+k>=n or j-k<0 :
                        continue
                    if board['board'][i+k][j-k]==1:
                        return True
    return False

def queenCount(board):
    count=0
    for i in range(n):
        for j in range(n):
            if board["board"][i][j]==1:
                count=count+1
    #if count>2:
   #     print board
    return count

if __name__ =='__main__':
    start={'board':[[0 for x in range(n)] for x in range(n)],'col':0}
    functions={'QueenDown':lambda board:moveQueenDown(board,n),'Col':lambda board:shiftCol(board)}
      
    check=lambda board: (queenCount(board)==n and not checkCollisions(board,n))
    clip=lambda board: (board['col']==n)
    depth=n**2+n
    N=n
    answers= search.backtrack(start, functions, check, clip, ["(QueenDown)^"+str(n)+"=(QueenDown)"], depth,N)

    for answer in answers:
        print(answer["node"]["board"])
    
    boards={}
    for answer in answers:
        boards[str(answer["node"]["board"])]=True

    print len(boards)

    print("done")

