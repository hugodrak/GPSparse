import sys, time
in_file = open(sys.argv[1], "r")
out_file = open("%s-G.csv"%sys.argv[1][:-4], "w")
out_file.write("Latitude, Longitude, Time\n")

for line in in_file:
    if line[:3] != "log":
        line = line[1:-2]
        a = line.split(", ")
        # print(a)
        if 3 < len(a):
            time = "%s:%s:%s" % (a[0][:2], a[0][2:4], a[0][4:6])
            out_file.write("%s, %s, %s\n" % (a[1], a[2], time))

out_file.close()
in_file.close()
