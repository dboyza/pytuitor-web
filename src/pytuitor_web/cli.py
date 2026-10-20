"""Start the local workbench and open it in the default browser."""

from __future__ import annotations

import argparse
import socket
import threading
import webbrowser
from pathlib import Path


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def main() -> None:
    from pytuitor_web import __version__

    parser = argparse.ArgumentParser(
        prog="pytuitor-web", description="Learn Python in your browser beside a real terminal."
    )
    parser.add_argument("--data-dir", type=Path, help="Use a separate local learning profile")
    parser.add_argument("--port", type=int, help="Serve on this loopback port (default: any)")
    parser.add_argument("--no-browser", action="store_true", help="Print the link only")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args()

    import uvicorn

    from pytuitor_web.service import Tutor
    from pytuitor_web.state import ProfileError
    from pytuitor_web.web import create_app

    try:
        tutor = Tutor(args.data_dir)
    except (ProfileError, OSError) as error:
        parser.exit(1, f"pytuitor-web: {error}\n")
    port = args.port or free_port()
    origin = f"http://127.0.0.1:{port}"
    app, token = create_app(tutor, origin)
    link = f"{origin}/#token={token}"
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", ws="websockets")
    )

    def announce() -> None:
        while not server.started:
            if server.should_exit:
                return
            threading.Event().wait(0.05)
        print(f"\n  Pytuitor is running at {origin}")
        print(f"  Open this one-time link to sign in: {link}")
        print("  Press Ctrl+C to stop. Your progress is saved as you work.\n")
        if not args.no_browser:
            webbrowser.open(link)

    threading.Thread(target=announce, daemon=True).start()
    try:
        server.run()
    finally:
        tutor.close()


if __name__ == "__main__":
    main()
