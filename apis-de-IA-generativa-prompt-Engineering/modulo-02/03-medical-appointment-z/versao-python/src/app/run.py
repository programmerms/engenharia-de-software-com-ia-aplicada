import uvicorn


def main() -> None:
    """
    Ponto de entrada para execução da aplicação em desenvolvimento.

    O Uvicorn carrega o objeto FastAPI `app` definido
    em app.app.
    """

    uvicorn.run(
        "app.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()