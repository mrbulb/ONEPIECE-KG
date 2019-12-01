import random
import sys

track_name   = "<http://kg.course/music/track_%05d> <http://kg.course/music/track_name> \"track_name_%05d\" ."
track_album  = "<http://kg.course/music/track_%05d> <http://kg.course/music/track_album> <http://kg.course/music/album_%04d> ."
album_name   = "<http://kg.course/music/album_%04d> <http://kg.course/music/album_name> \"album_name_%04d\" ."
track_artist = "<http://kg.course/music/track_%05d> <http://kg.course/music/track_artist> <http://kg.course/music/artist_%03d> ."
artist_name  = "<http://kg.course/music/artist_%03d> <http://kg.course/music/artist_name> \"artist_name_%03d\" ."
tag_name     = "<http://kg.course/music/track_%05d> <http://kg.course/music/track_tag> \"tag_name_%02d\" ."

total_sum = 1000
triples_sum = 0
triples = []

if (len(sys.argv) >= 2):
	try:
		total_sum = int(sys.argv[1])
	except:
		total_sum = 1000

for i in range(1, total_sum) :
	track_str = track_name % (i, i)
	s = random.randint(1, 10)
	album_str = track_album % (i, i/s + 1)
	album_name_str = album_name % (i/10 + 1, i/10 + 1)
	t = random.randint(1, 100)
	track_artist_str = track_artist % (i, i % t)
	artist_name_str = artist_name % (i % t, i % t)
	k = random.randint(1, 10)
	tag_name_str = tag_name % (i, i % k + 1)
	triples.append(track_str)
	triples_sum += 1
	if (total_sum <= triples_sum):
		break
	triples.append(album_str)
	triples_sum += 1
	if (total_sum <= triples_sum):
		break
	triples.append(album_name_str)
	triples_sum += 1
	if (total_sum <= triples_sum):
		break
	triples.append(track_artist_str)
	triples_sum += 1
	if (total_sum <= triples_sum):
		break
	triples.append(tag_name_str)
	triples_sum += 1
	if (total_sum <= triples_sum):
		break

filename = ("music_%d_triples.nt") % (total_sum)
with open(filename,"w+") as fd:
	fd.write("\n".join(triples))