from app import create_app
from datetime import datetime

app = create_app()

# Přidání globální proměnné pro šablony
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run(debug=True)
