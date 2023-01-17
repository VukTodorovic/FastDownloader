
file = open('./server/files/gamefile.dll', 'rb')

chunk = file.read(1000)

file.close()

output = str(3).encode() + b' ' + chunk

print(output)