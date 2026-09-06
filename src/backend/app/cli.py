from waitress import serve

from .app import create_app


def main() -> None:
    app = create_app()

    serve(
        app,
        host="127.0.0.1",
        port=5010,
        threads=4,
    )


if __name__ == "__main__":
    main()