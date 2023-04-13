"""
"""
from api.app import get_app
import uvicorn


if __name__ == '__main__':
    app = get_app()
    uvicorn.run(app, host='0.0.0.0', port=8000)