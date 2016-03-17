from django.contrib.auth.models import Group
from django.test import TestCase, RequestFactory

from .forms import CollectionForm, SeedSetForm
from .views import CollectionUpdateView
from .models import User, Collection, Credential


def create_group(name):
    return Group.objects.create(name=name)


class CollectionFormTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@example.com',
                                             password='password')
        self.request.user = self.user
        self.group = create_group(name='testgroup1')
        self.user.groups.add(self.group)
        create_group(name='testgroup2')

    def test_form_has_correct_groups(self):
        form = CollectionForm(request=self.request)
        self.assertListEqual([self.group,], list(form.fields['group'].queryset))

    def test_valid_data(self):
        groupno = Group.objects.filter(name='testgroup1')
        form = CollectionForm({
            'name': 'my test collection',
            'description': 'my description',
            'group': groupno
        }, request=self.request)
        self.assertTrue(form.is_valid())

    # In my view, these are testing configuration, not code.
    # They don't hurt, but aren't necessary.
    def test_invalid_data_blank_name(self):
        groupno = Group.objects.filter(name='testgroup1')
        form = CollectionForm({
            'name': '',
            'description': 'my description',
            'group': groupno
        }, request=self.request)
        self.assertFalse(form.is_valid())

    def test_invalid_data_blank_group(self):
        form = CollectionForm({
            'name': 'my test collection',
            'description': 'my description',
            'group': ''
        }, request=self.request)
        self.assertFalse(form.is_valid())


# I don't think these are necessary.
class CollectionUpdateFormTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@example.com',
                                             password='password')
        group = create_group(name='testgroup1')
        self.user.groups.add(group)
        self.collection = Collection.objects.create(name='Test Collection One',
                                                    group=group)
        self.path = '/ui/collections/' + str(self.collection.pk) + '/update/'

    def test_valid_data(self):
        request = self.factory.get(self.path)
        request.user = self.user
        groupno = Group.objects.filter(name='testgroup1')
        response = CollectionUpdateView.as_view()(request,
                                                  pk=self.collection.pk)
        form = CollectionForm({
            'name': 'my test collection updated name',
            'description': 'my updated description',
            'group': groupno
        }, request=request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(form.is_valid())

    def test_group_choices_correct(self):
        request = self.factory.get(self.path)
        request.user = self.user
        response = CollectionUpdateView.as_view()(request,
                                                  pk=self.collection.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'testgroup2')

    def test_invalid_data_blank_name(self):
        request = self.factory.get(self.path)
        request.user = self.user
        groupno = Group.objects.filter(name='testgroup1')
        response = CollectionUpdateView.as_view()(request,
                                                  pk=self.collection.pk)
        form = CollectionForm({
            'name': '',
            'description': 'my description',
            'group': groupno
        }, request=request)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())

class SeedSetFormTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        user = User.objects.create_superuser(username="test_user", email="test_user@test.com",
                                             password="test_password")
        group = Group.objects.create(name="test_group")
        self.collection = Collection.objects.create(group=group, name="test_collection")
        self.credential = Credential.objects.create(user=user, platform="test_platform",
                                               token="{}")
        self.data = {
            'collection': self.collection.pk,
            'credential': self.credential.pk,
            'harvest_type': 'twitter_search',
            'name': 'my test seedset',
            'start_date': '01/01/2100',
            'end_date': '01/01/2200',
            'date_added': '03/16/2016',
            'schedule_minutes': '60'
        }

    def test_valid_form(self):
        form = SeedSetForm(self.data, coll=self.collection.pk)
        self.assertTrue(form.is_valid())


    def test_start_date_after_now(self):
        self.data['start_date'] = "01/01/2000"
        form = SeedSetForm(self.data, coll=self.collection.pk)
        self.assertFalse(form.is_valid())

    def test_end_date_after_now(self):
        self.data['end_date'] = "01/01/2000"
        form = SeedSetForm(self.data, coll=self.collection.pk)
        self.assertFalse(form.is_valid())

    def test_end_date_after_start_date(self):
        self.data['end_date'] = "01/01/2100"
        self.data['start_date'] = "01/01/2200"
        form = SeedSetForm(self.data, coll=self.collection.pk)
        self.assertFalse(form.is_valid())
