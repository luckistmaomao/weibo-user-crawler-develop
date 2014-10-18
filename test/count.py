from pymongo import Connection

conn = Connection('localhost')
db = conn.sina

infile = open("famous.txt")
outfile = open("famous_count.txt", 'w')

max_count = 0
max_uid = ''

for line in infile:
    uid = line.split()[0]
    count = db.micro_blog.find({'uid': uid}).count()
    outfile.write(uid + '  ' + str(count) + '\n')
    if count > max_count:
        max_count = count
        max_uid = uid

print "max_uid: ",  max_uid
print "max_count: ", max_count

infile.close()
outfile.close()

