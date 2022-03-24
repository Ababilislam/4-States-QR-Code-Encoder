import os
import time
import tracemalloc
import init

start_time = time.time()
tracemalloc.start()
"""in time of creating four states QR code you can pass  "data="data", error='L', version=None,
mode=None, encoding=None but the suggestion is that you(user)
 just pass data system will do the best work for you"""
 
# code = init.create('Green University of Bangladesh,city campus')       # string data
# code = init.create('Bangladesh')
# code = init.create('green.edu.bd/wp-content/uploads/2020/10/Umme_Ruman_Madam.png')   
          # web link.
          
# code = init.create('fb8e20fc2e4c3f248c60c39bd652f3c1347298bb977b8b4d5903b85055620603')
"""Use absulute file path of the input file to 100% sure that file is absulately OK"""

file = "/home/ab/Desktop/research/data/new_dataset/Student/test_data_002.txt"

# file reading 
file_data = open(file, "r")
data = file_data.read()
# print(data)

code = init.create(data)

image = code.image_generation()


# For time CHeck
execution_time = time.time() - start_time
"""comment out for future use."""
t=time.strftime("%S",time.gmtime(execution_time))
if int(t)>0:
    print('Execution Time Taken:', time.strftime("%HHours:%MMinutes:%SSeconds",time.gmtime(execution_time)))
else:
    print("Execution Time {:.2f} Milliseconds".format(execution_time*1000))
# comment below 2 line if upper section of code is used.
# print('Execution Time Taken:', time.strftime("%HHours:%MMinutes:%SSeconds",time.gmtime(execution_time)))
# print("Execution Time {:.2f} Milliseconds".format(execution_time*1000))
# For Memory CHeck
current, Maximum = tracemalloc.get_traced_memory()
print(f"Maximum usage of memory is: {Maximum / 10**6} MB")
tracemalloc.stop()

# path = os.path.dirname((os.path.abspath(__file__)))
# print(path)