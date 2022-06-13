import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=80, reload=True, debug=True, access_log=False)
