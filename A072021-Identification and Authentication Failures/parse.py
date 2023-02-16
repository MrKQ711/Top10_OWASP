password = 'pass.txt'
brute = open("textParse.txt", 'w')
with open(password) as f:
    line = f.readline()
    while line:
        brute.write("\"")
        brute.write(line.strip())
        brute.write("\",")
        line = f.readline()
brute.close()
