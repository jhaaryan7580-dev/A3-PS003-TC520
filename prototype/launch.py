"""Serve the packaged static lab locally. No training, uploads or credentials."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
import argparse
import webbrowser


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent / 'dist' / 'public'
    if not (folder / 'index.html').is_file():
        parser.error('Compiled app missing. Restore the complete prototype/dist folder or build:static from source.')
    if not 1024 <= args.port <= 65535:
        parser.error('Choose a local port from 1024 to 65535.')
    handler = partial(SimpleHTTPRequestHandler, directory=str(folder))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError as exc:
        parser.error(f'Cannot listen: {exc}. Try --port 8081; do not disable system security controls.')
    url = f'http://127.0.0.1:{args.port}/'
    print(f'Chauraha Sync local prototype: {url}', flush=True)
    print('Static files only. No dataset uploads or model training. Ctrl+C stops the server.', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
