#user defined functions
name=input('enter a name: ')
def name_rat():
    for i in range(0,len(name)):
        for j in range(0,i+1):
            print(name[i],end='')
        print()

def name_irat():
    for i in range(len(name),0,-1):
        for j in range(0,i):
            print(name[i-1],end='')
        print()

print('Available choices')
print('-----------------')
print('1. name right angled triangle')
print('2. name inversed right angled triangle')

choice=int(input('enter your choice: '))
if choice==1:
    name_rat()
elif choice==2:
    name_irat()
else:
    print('please enter valid choice')
