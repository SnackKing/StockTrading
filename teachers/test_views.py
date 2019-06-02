from django.test.client import RequestFactory
from django.test import TestCase
from django.test import Client
from . import views
from django.urls import reverse
import pyrebase


config = {
	"apiKey": "AIzaSyAzXh-si71dEDldZkLmbY7l-_NZ8VJTfs4",
	"authDomain": "stocktrader-239615.firebaseapp.com",
	"databaseURL":  "https://stocktrader-239615.firebaseio.com",
	"storageBucket": "stocktrader-239615.appspot.com",
	"serviceAccount": "creds.json"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
tid = 'PzHumqmQqzXDhri03TrDe0nEisB3'
class LandingTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.session = self.client.session
		self.session.save()

	def test_landing_loggedin(self):
		url = reverse('teachers-landing')
		self.session['tid'] = tid
		self.session['name'] = 'TestTeacher'
		self.session.save()
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

	def test_landing_notloggedin(self):
		url = reverse('teachers-landing')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)

class LoginTest(TestCase):
	def setUp(self):
		self.client = Client()
		session = self.client.session
		session['tid'] = tid
		session['name'] = 'TestTeacher'
		session.save()

	def testLoginValid(self):
		url = reverse('teachers-login')
		data = {'email': 'test@teacher.com', 'password': 'password'}
		# Create an instance of a POST request.
		self.response = self.client.post(url, data)
		self.assertRedirects(self.response, reverse('teachers-dashboard'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

	def testLoginInvalid(self):
		url = reverse('teachers-login')
		data = {'email': 'notarealemail@gmail.com', 'password': 'password'}
		# Create an instance of a POST request.
		self.response = self.client.post(url, data)
		self.assertRedirects(self.response, reverse('teachers-login'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

class DashboardTest(TestCase):
	@classmethod
	def setUpTestData(self):
		self.client = Client()
		session = self.client.session
		session['tid'] = tid
		session['name'] = 'TestTeacher'
		session.save()
		self.teacher = db.child('teachers').child(session['tid']).get().val()
		url = reverse('teachers-dashboard')
		self.response = self.client.get(url)

	def test_dashboard_statusCode(self):
		self.assertEqual(self.response.status_code, 200)

	def test_dashboard_data(self):
		self.assertEqual(self.response.context['user'], self.teacher)
	def test_dashboard_name(self):
		self.assertEqual(self.response.context['name'], 'TestTeacher')

class ViewStudentsTest(TestCase):
	@classmethod
	def setUpTestData(self):
		self.client = Client()
		session = self.client.session
		session['tid'] = tid
		session['name'] = 'TestTeacher'
		session.save()
		self.teacher = db.child('teachers').child(session['tid']).get().val()
		url = reverse('teachers-class',  kwargs={'joinCode':"SRUP49G1N4"})
		self.response = self.client.get(url)

	def test_studentlist_statuscode(self):
		assertEqual(self.response.status_code, 200)

	def test_studentlist_data(self):
		classData = db.child('teachers').child(tid).child('classes').child(joinCode).get().val()
		assertEquals(classData, self.response.context['classData'])

class AddClassTest(TestCase):
	def setUp(self):
		self.client = Client()
		session = self.client.session
		session['tid'] = tid
		session['name'] = 'TestTeacher'
		session.save()
		self.teacher = db.child('teachers').child(tid).get().val()
		self.codes = db.child('codes_tid').get().val()
		self.classes =db.child('teachers').child(tid).child('classes').get().val()


	def test_addclass_formstatus(self):
		url = reverse('teachers-newclass')
		response = self.client.get(url)
		self.assertEqual(response.status_code,200)

	def test_addclass_valid(self):
		url = reverse('teachers-newclass')
		data = {'name': 'NewTestClass', 'startingCash': 2000}
		response = self.client.post(url, data)
		newClasses = len(db.child('teachers').child(tid).child('classes').get().val())
		newCodes = len(db.child('codes_tid').get().val())
		self.assertRedirects(response, reverse('teachers-dashboard'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
		self.assertEqual(newClasses, len(self.classes)+1)
		self.assertEqual(newCodes, len(self.codes)+1)

	def test_addclass_decimal_cash(self):
		url = reverse('teachers-newclass')
		data = {'name': 'NewTestClass', 'startingCash': 500.5}
		response = self.client.post(url, data)
		newClasses = len(db.child('teachers').child(tid).child('classes').get().val())
		newCodes = len(db.child('codes_tid').get().val())
		self.assertRedirects(response, reverse('teachers-newclass'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
		self.assertEqual(newClasses, len(self.classes))
		self.assertEqual(newCodes, len(self.codes))

	def test_addclass_blank(self):
		url = reverse('teachers-newclass')
		data = {'name': '', 'startingCash': ''}
		response = self.client.post(url, data)
		newClasses = len(db.child('teachers').child(tid).child('classes').get().val())
		newCodes = len(db.child('codes_tid').get().val())
		self.assertRedirects(response, reverse('teachers-newclass'), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
		self.assertEqual(newClasses, len(self.classes))
		self.assertEqual(newCodes, len(self.codes))

	def tearDown(self):
		db.child('teachers').child(tid).set(self.teacher)
		db.child('codes_tid').set(self.codes)

class RemoveStudentTest(TestCase):
	def setUp(self):
		self.client = Client()
		session = self.client.session
		session['tid'] = tid
		session['name'] = 'TestTeacher'
		session.save()
		self.oldClass =db.child('teachers').child(tid).child('classes').child('SRUP49G1N4').get().val()

	def test_removestudent_singleStudent(self):
		url = reverse('teachers-removeStudent', kwargs = {'joinCode': 'SRUP49G1N4', 'studentId':'RuGvmBrRlVRIHjC4k7EhGvwMpJQ2'})
		response = self.client.get(url)
		self.assertRedirects(response, reverse('teachers-class', kwargs = {'joinCode': 'SRUP49G1N4'}), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
		newClass =db.child('teachers').child(tid).child('classes').child('SRUP49G1N4').get().val()
		self.assertFalse('students' in newClass )

	def test_removestudent_invalid(self):
		url = reverse('teachers-removeStudent', kwargs = {'joinCode': 'SRUP49G1N4', 'studentId':'notarealid'})
		response = self.client.get(url)
		self.assertRedirects(response, reverse('teachers-class', kwargs = {'joinCode': 'SRUP49G1N4'}), status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
		newClass =db.child('teachers').child(tid).child('classes').child('SRUP49G1N4').get().val()
		self.assertEquals(newClass, self.oldClass)

	def tearDown(self):
		db.child('teachers').child(tid).child('classes').child('SRUP49G1N4').set(self.oldClass)







