from app import app
from models import db, Employee, Idea
from werkzeug.security import generate_password_hash

# Dummy data for different roles
dummy_accounts = [
    {
        "id":0,
        "name": "John Employee",
        "email": "employee@example.com",
        "role": "employee",
        "password": "testpassword"
    },
    {
        id:1,
        "name": "Jane Manager",
        "email": "manager@example.com",
        "role": "manager",
        "password": "testpassword"
    },
    {
        id:2,
        "name": "Sam Admin",
        "email": "admin@example.com",
        "role": "admin",
        "password": "testpassword"
    }
]

# Example ideas for testing
dummy_ideas = [
    {
        "title": "Renewable Energy Solution",
        "description": "A proposal for implementing solar panels in all regional offices.",
        "status": "approved" , 
         "votes": 10,
         "author_id": 0
    },
    {
        "title": "AI-Driven Idea Filtering",
        "description": "Using AI to prioritize submitted ideas based on keywords and voting.",
        "status": "pending",
        "votes": 2,
        "author_id": 0
    }

]

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Dummy accounts with hashed passwords
        for account in dummy_accounts:
            hashed_password = generate_password_hash(account["password"])
            employee = Employee(
                name=account["name"],
                email=account["email"],
                role=account["role"],
                password_hash=hashed_password
            )
            db.session.add(employee)

        # Add dummy ideas
        for idea_data in dummy_ideas:
            author = Employee.query.get(idea_data["author_id"])
            if author:
                idea = Idea(
                    title=idea_data["title"],
                    description=idea_data["description"],
                    author_id=author.id
                )
                db.session.add(idea)

        db.session.commit()
        print("Database seeded successfully with dummy data!")

if __name__ == "__main__":
    seed_database()
