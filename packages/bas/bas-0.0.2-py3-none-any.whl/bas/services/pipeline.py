import requests
from bas.services.utils import parse_response

def pipeline(lyrics, signal, language, pipe='G2P_MAUS_SUBTITLE', maxlength=0, modus='align', outformat='srt'):
    files = {
        'PIPE': (None, pipe),
        'TEXT': ('file.txt', lyrics),
        'SIGNAL': ('file.wav', signal),
        'LANGUAGE': (None, language),
        'NORM': (None, 'true'),
        'maxlength': (None, maxlength),
        'MODUS': (None, modus),
        'OUTFORMAT': (None, outformat),
        'marker': (None, 'newline'),
    }

    response = requests.post(
        'https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runPipeline',
        files=files)
    return parse_response(response)