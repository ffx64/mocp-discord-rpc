import pypresence
import time, os
import subprocess

def now_playing_data():
	now_playing = subprocess.run(["mocp", "--info"], universal_newlines=True, stdout=subprocess.PIPE).stdout.splitlines()

	data = dict([
		(k.lower(), v.strip()) for k, v in [line.split(":", 1) for line in now_playing if line]
	])

	if "fatal_error" in data:
		return dict()
	elif "timeout" in data:
		return dict()
	elif data.get("state") == "STOP":
		return dict()

	return data

def main():
	CLIENT_ID = "1289765982872801310"

	rpc = pypresence.Presence(CLIENT_ID)

	connected = False
	music_title = ""

	while True:
		now_playing = now_playing_data()

		if now_playing != None and now_playing.get("state") != "PAUSE":
			if not connected:
				rpc.connect()
				connected = True

			new_music_title = now_playing.get("songtitle") if now_playing.get("songtitle") not in ["Untitled", ""] else os.path.splitext(os.path.basename(now_playing.get('file')))[0]

			if now_playing.get("state") == "PLAY" and connected and music_title != new_music_title:
				music_album = now_playing.get("album") if now_playing.get("album") != "" else "Unknown Album"
				music_title = new_music_title if new_music_title != "" else "Unknown Title"
				music_artist = now_playing.get("artist").replace("/", ", ") if now_playing.get("artist") != "" else "Unknown Artist"

				music_current_sec = now_playing.get("CurrentSec")
				music_total_sec = now_playing.get("TotalSec")

				if music_current_sec is not None:
					music_start_time = time.time() - music_total_sec
				else:
					music_start_time = time.time()

				if music_total_sec is not None and music_current_sec is not None:
					music_end_time = music_start_time + (music_total_sec - music_current_sec)
				else:
					music_end_time = None

				rpc.update(
					large_image="mocp-3",
					large_text=music_album,
					buttons=[{"label": "Now Playing", "url": "https://github.com/jonsafari/mocp"}],
					details=music_title,
					state=music_artist,
					small_image="play",
					small_text="listening to...",
					start=music_start_time,
					end=music_end_time,
	        	)

		elif now_playing.get("state") == "PAUSE" and connected:
			rpc.close()
			connected = False

		time.sleep(3)

if __name__ == "__main__":
	main()
