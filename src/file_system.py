import os
from mcp.server import FastMCP

app = FastMCP("filesystem")


@app.tool()
def list_dir(path: str):
    # check sensitive folders
    if not os.path.exists(path):
        return {"error": "Path does not exist"}
    if not os.path.isdir(path):
        return {"error": "Not a directory"}

    # list files and sub directories
    files = os.listdir(path)
    return {"files": files}


if __name__ == "__main__":
    app.run(transport="stdio")  # local running
