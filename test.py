

outfile = "C:\Users\Hamish St George\Desktop\\test.csv"
split = outfile.split("\\")
splitpath = ""
print (split[len(split) - 1])
split[len(split) - 1] = "flat" + split[len(split)-1]
for line in split:
    splitpath = splitpath + line + "\\"

splitpath = splitpath[:-1]
print (splitpath)