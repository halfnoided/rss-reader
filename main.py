from database import Base, engine
from models import Feed, Article

Base.metadata.create_all(bind=engine)

def main():
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    return 0

if __name__ == "__main__":
    main()