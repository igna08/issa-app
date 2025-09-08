import unittest
import os

# Set a dummy environment variable for the access token BEFORE importing the app
os.environ['MERCADOPAGO_ACCESS_TOKEN'] = 'dummy-token-for-testing'

from app import app, db, Usuario, Curso, Administrador, bcrypt

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        self.app = app.test_client()
        db.create_all()
        # Add a test admin user
        hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
        admin = Administrador(nombre='Test Admin', email='admin@test.com', password=hashed_password)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.app.post('/admin/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/admin/logout', follow_redirects=True)

    def test_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_inscription_page(self):
        response = self.app.get('/inscripcion', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_login_logout(self):
        response = self.login('admin@test.com', 'testpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Login', response.data)

    def test_admin_dashboard_unauthorized(self):
        response = self.app.get('/admin/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Login', response.data)

    def test_add_course(self):
        self.login('admin@test.com', 'testpassword')
        response = self.app.post('/admin/course/add', data=dict(
            tipo='otros',
            nombre='Test Course',
            precio='99.99'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Course', response.data)
        with app.app_context():
            course = Curso.query.filter_by(nombre='Test Course').first()
            self.assertIsNotNone(course)


if __name__ == '__main__':
    unittest.main()
