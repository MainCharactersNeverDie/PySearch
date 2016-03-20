import backtrackPar as search

start=''
functions={'AonRight':lambda s: s+'A', 'Reverse':lambda s: s[::-1], 'BonLeft': lambda s: 'B'+s}
clip=lambda s: False
check=lambda s: 'A'==s
depth=6
N=9



if __name__ =='__main__':
    for answer in search.backtrack(start, functions, check, clip, "", depth,N):
        print(answer["path"])
    print("done")

