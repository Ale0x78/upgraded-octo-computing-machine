from time import time
from main_planner import Graph

filenum = 1
while True:
    try:
        fileStr = f"input{filenum}.json"
        test = Graph(fileStr)
        start = time()
        test.plan()
        total = time() - start
        print(f"Time (Seconds): {total}")
    except:
        break
    filenum += 1