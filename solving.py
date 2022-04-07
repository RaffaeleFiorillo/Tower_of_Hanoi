# source rod
A = []
# middle rod
B = []
# target rod
C = []


def showAll():
    print(A, B, C, '_________________', sep='\n');


def move(n, source, target, bridge):
    if n > 0:
        # move n - 1 disks from source to bridge, so they are out of the way
        move(n - 1, source, bridge, target)

        # move the nth disk from source to target
        target.append(source.pop())

        # Display our progress
        showAll()

        # move the n - 1 disks that we left on bridge onto target
        move(n - 1, bridge, target, source)


discs = int(input("Number of disks: "))
print(discs, '_________________', sep='\n')
A = list(range(1, discs + 1))[::-1]
showAll()
# initiate call from source A to target C with auxiliary B
move(discs, A, C, B)
print("Number of moves:" + str(2 ** discs - 1))
