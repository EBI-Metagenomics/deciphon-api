from ._app import app


@app.get("/")
def httpget():
    return {"msg": "Hello World"}
