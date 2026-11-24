import sys, base64, json, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gem import text
for f in sys.argv[2:]:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f, '-ac', '1', '-ar', '16000', '-b:a', '32k', '/tmp/_h.mp3'])
    print(os.path.basename(f), '->', text(sys.argv[1], [{"text": "Transcribe this Indonesian audio exactly, word for word, and then on a new line describe in one short sentence the speaker's voice, tone and accent."}, {"inlineData": {"mimeType": "audio/mp3", "data": base64.b64encode(open('/tmp/_h.mp3', 'rb').read()).decode()}}]).strip().replace('\n', ' | ')[:500])
