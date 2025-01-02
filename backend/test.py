import unittest
from app import app, db
from models import Employee, Idea, Vote, Feedback, Incentive

class APITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Tear down the test environment."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        """Prepare test data."""
        with app.app_context():
            employee = Employee(name="John Doe", email="john@example.com", role="Employee", region="NA")
            db.session.add(employee)
            db.session.commit()

    def tearDown(self):
        """Clean up test data."""
        with app.app_context():
            db.session.query(Employee).delete()
            db.session.query(Idea).delete()
            db.session.query(Vote).delete()
            db.session.query(Feedback).delete()
            db.session.query(Incentive).delete()
            db.session.commit()

    # Test login
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post('/login', json={
            "email": "john@example.com",
            "password": "testpassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.get_json())

    def test_login_failure(self):
        """Test login with invalid credentials."""
        response = self.client.post('/login', json={
            "email": "john@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json().get("message"), "Invalid credentials")

    # Test employee creation
    def test_create_employee(self):
        """Test creating an employee."""
        response = self.client.post('/employees', json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "role": "Manager",
            "region": "EU"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json().get("message"), "Employee created successfully")

    # Test retrieving employees
    def test_get_employees(self):
        """Test fetching employees."""
        response = self.client.get('/employees')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.get_json()) > 0)

    # Test idea creation
    def test_create_idea(self):
        """Test creating an idea."""
        with app.app_context():
            employee = Employee.query.first()
        response = self.client.post('/ideas', json={
            "title": "New Innovation",
            "description": "An innovative idea",
            "author_id": employee.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json().get("message"), "Idea created successfully")

    # Test vote creation
    def test_create_vote(self):
        """Test creating a vote."""
        with app.app_context():
            employee = Employee.query.first()
            idea = Idea(title="New Innovation", description="An innovative idea", author_id=employee.id)
            db.session.add(idea)
            db.session.commit()
        response = self.client.post('/votes', json={
            "idea_id": idea.id,
            "voter_id": employee.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json().get("message"), "Vote added successfully")

    # Test feedback creation
    def test_create_feedback(self):
        """Test creating feedback for an idea."""
        with app.app_context():
            employee = Employee.query.first()
            idea = Idea(title="New Innovation", description="An innovative idea", author_id=employee.id)
            db.session.add(idea)
            db.session.commit()
        response = self.client.post('/feedback', json={
            "idea_id": idea.id,
            "author_id": employee.id,
            "content": "Great idea, needs more detail"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json().get("message"), "Feedback added successfully")

    # Test incentive retrieval
    def test_get_incentives(self):
        """Test retrieving incentives for an employee."""
        with app.app_context():
            employee = Employee.query.first()
            incentive = Incentive(employee_id=employee.id, points=100, reason="Top contributor")
            db.session.add(incentive)
            db.session.commit()
        response = self.client.get(f'/incentives/{employee.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

if __name__ == '__main__':
    unittest.main()
