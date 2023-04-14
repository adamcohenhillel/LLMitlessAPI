"""LLMitlessAPI
"""
import uvicorn

from app.api import app

if __name__ == '__main__':
    print('\33[36mAPI Running.\33[0m')
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level="critical")
