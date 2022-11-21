from collections import deque

memory = deque(maxlen=3)

# when we append to maximum deque, it will append right and pop left
memory.append([0,1,0,1])
memory.append([0,1,0,1])
memory.append([0,1,0,1])
memory.append([1,1,1,1])
memory.append([0,0,0,0])

print(memory)