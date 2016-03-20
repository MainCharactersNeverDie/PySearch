import backtrackPar as search
import copy
 
#N Queens
n=11
def placeQueen(board, n,i):
	board=copy.deepcopy(board)
	board['board'][board['col']][i]=1
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
                    if i-k<0 or j-k<0 :
                        continue
                    if board['board'][i-k][j-k]==1:
                        return True
    return False

if __name__ =='__main__':
    start={'board':[[0 for x in range(n)] for x in range(n)],'col':0}
    functions={}
    listOfLambdas= [lambda board, i=i:placeQueen(board,n,i) for i in range(0,n)]

    for i in range(n):
        functions['QueenAt'+str(i)]=listOfLambdas[i]
    check=lambda board: (board['col']==n)
    clip=lambda board: checkCollisions(board,n)
    depth=n
    N=n

    for answer in search.backtrack(start, functions, check, clip, "", depth,N):
        print(answer["path"])
    print("done")

