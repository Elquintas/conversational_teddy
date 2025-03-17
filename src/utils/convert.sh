mkdir -p converted
for f in *.mp3 *.flac *.wav; do
    ffmpeg -i "$f" -ac 1 -ar 44100 -sample_fmt s16 "converted/${f%.*}.wav"
done
