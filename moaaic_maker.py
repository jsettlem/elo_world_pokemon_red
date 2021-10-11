import itertools
import os
import subprocess
import uuid


def get_length(filename):
	result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
	                         "format=duration", "-of",
	                         "default=noprint_wrappers=1:nokey=1", filename],
	                        stdout=subprocess.PIPE,
	                        stderr=subprocess.STDOUT)
	try:
		return float(result.stdout)
	except ValueError:
		return -1


def main():
	input_dir = "W:\elo_world_output\red_redux\movies\tournament"
	files = [f"{input_dir}/{f}" for f in os.listdir(input_dir) if f.endswith(".mkv")]
	for i in range(16):
		with open(f"mosaic/concat{i}.txt", 'w') as f:
			f.write("ffconcat version 1.0\n")
			next_file = files.pop()
			total_time = get_length(next_file)
			while total_time == -1:
				next_file = files.pop()
				total_time = get_length(next_file)
			go = True
			while total_time < 12 * 60 * 60 - 60 or go:
				f.write("\n")
				f.write(f"file 'file:{next_file}'")
				next_file = files.pop()
				next_length = get_length(next_file)
				while next_length == -1:
					next_file = files.pop()
					next_length = get_length(next_file)
				total_time += next_length
				go = False
	call = ["ffmpeg",
	        "-safe", "0",
	        *[o for i in zip(itertools.repeat("-safe"),
	                         itertools.repeat("0"),
	                         itertools.repeat("-i"),
	                         (f"mosaic/concat{i}.txt" for i in range(16))) for o in i],
	        "-filter_complex",
	        "[0:v] setpts=PTS-STARTPTS [a0]; [1:v] setpts=PTS-STARTPTS [a1]; [2:v] setpts=PTS-STARTPTS [a2]; [3:v] setpts=PTS-STARTPTS [a3]; [4:v] setpts=PTS-STARTPTS [a4]; [5:v] setpts=PTS-STARTPTS [a5]; [6:v] setpts=PTS-STARTPTS [a6]; [7:v] setpts=PTS-STARTPTS [a7]; [8:v] setpts=PTS-STARTPTS [a8]; [9:v] setpts=PTS-STARTPTS [a9]; [10:v] setpts=PTS-STARTPTS [a10]; [11:v] setpts=PTS-STARTPTS [a11]; [12:v] setpts=PTS-STARTPTS [a12]; [13:v] setpts=PTS-STARTPTS [a13]; [14:v] setpts=PTS-STARTPTS [a14]; [15:v] setpts=PTS-STARTPTS [a15]; [a0][a1][a2][a3][a4][a5][a6][a7][a8][a9][a10][a11][a12][a13][a14][a15]xstack=inputs=16:layout=0_0|0_h0|0_h0+h1|0_h0+h1+h2|w0_0|w0_h0|w0_h0+h1|w0_h0+h1+h2|w0+w4_0|w0+w4_h0|w0+w4_h0+h1|w0+w4_h0+h1+h2|w0+w4+w8_0|w0+w4+w8_h0|w0+w4+w8_h0+h1|w0+w4+w8_h0+h1+h2[vout];"
	        "amix=inputs=16[aout]",
	        "-map", "[vout]",
	        "-map", "[aout]",
	        "-c:v", "libx264",
	        "-s",  "1280x1152",
	        "-sws_flags", "neighbor",
	        "-ac", "2",
	        f"mosaic/long_mosaic_{str(uuid.uuid4())}.mp4"
	        ]
	print(call)
	subprocess.call(call)

	pass


if __name__ == '__main__':
	main()
