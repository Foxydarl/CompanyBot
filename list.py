a = []
while True:
    b = input()
    if b == 'end':
        break
    else:
        a.append(input())
for i in sorted(a):
    print(i)