response = 'ACCEPTED 7 291693 54565 62468 52116 59646 52602 52603 52604'

responseValues = response.split(' ')

streamPorts = []
for i in range(3, 3+int(responseValues[1])):
    print(f'i: {i}')
    streamPorts.append(int(responseValues[i]))

print(f'response: {response}\nresponseValues: {responseValues}\nstreamPorts: {streamPorts}')