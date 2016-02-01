from django.test import TestCase
from ui.models import Harvest, SeedSet, Group, Collection, Credential, User, Seed, Warc
import json
from message_consumer.sfm_ui_consumer import SfmUiConsumer
import iso8601


class ConsumerTest(TestCase):
    def setUp(self):
        # Create harvest model object
        user = User.objects.create_superuser(username="test_user", email="test_user@test.com",
                                             password="test_password")
        group = Group.objects.create(name="test_group")
        collection = Collection.objects.create(group=group, name="test_collection")
        credential = Credential.objects.create(user=user, platform="test_platform",
                                               token=json.dumps({}))
        seedset = SeedSet.objects.create(collection=collection, credential=credential,
                                         harvest_type="test_type", name="test_seedset",
                                         harvest_options=json.dumps({}))
        Seed.objects.create(seed_set=seedset, uid="131866249@N02")
        Seed.objects.create(seed_set=seedset, token="library_of_congress")
        self.harvest = Harvest.objects.create(harvest_id="test:1", seed_set=seedset)
        self.consumer = SfmUiConsumer()

    def test_harvest_status_on_message(self):
        self.consumer.routing_key = "harvest.status.test.test_search"
        self.consumer.message = {
            "id": "test:1",
            "status": "completed success",
            "date_started": "2015-07-28T11:17:36.640044",
            "date_ended": "2015-07-28T11:17:42.539470",
            "infos": [{"code": "test_code_1", "message": "congratulations"}],
            "warnings": [{"code": "test_code_2", "message": "be careful"}],
            "errors": [{"code": "test_code_3", "message": "oops"}],
            "summary": {
                "photo": 12,
                "user": 1
            },
            "token_updates": {
                "131866249@N02": "j.littman"
            },
            "uids": {
                "library_of_congress": "671366249@N03"
            },
            "warcs": {
                "count": 3,
                "bytes": 345234242
            }
        }
        # Trigger on_message
        self.consumer.on_message()

        # Check updated harvest model object
        harvest = Harvest.objects.get(harvest_id="test:1")
        self.assertEqual("completed success", harvest.status)
        self.assertEqual(12, harvest.stats["photo"])
        self.assertDictEqual({
            "131866249@N02": "j.littman"
        }, harvest.token_updates)
        self.assertDictEqual({
            "library_of_congress": "671366249@N03"
        }, harvest.uids)
        self.assertEqual(3, harvest.warcs_count)
        self.assertEqual(345234242, harvest.warcs_bytes)
        self.assertEqual(iso8601.parse_date("2015-07-28T11:17:36.640044"), harvest.date_started)
        self.assertEqual(iso8601.parse_date("2015-07-28T11:17:42.539470"), harvest.date_ended)
        self.assertListEqual([{"code": "test_code_1", "message": "congratulations"}], harvest.infos)
        self.assertListEqual([{"code": "test_code_2", "message": "be careful"}], harvest.warnings)
        self.assertListEqual([{"code": "test_code_3", "message": "oops"}], harvest.errors)

        # Check updated seeds
        seed1 = Seed.objects.get(uid="131866249@N02")
        self.assertEqual("j.littman", seed1.token)
        seed2 = Seed.objects.get(token="library_of_congress")
        self.assertEqual("671366249@N03", seed2.uid)

    def test_on_message_ignores_bad_routing_key(self):
        self.consumer.routing_key = "xharvest.status.test.test_search"

        # Trigger on_message and nothing happens
        self.consumer.on_message()

    def test_on_message_ignores_unknown_harvest(self):
        self.consumer.routing_key = "harvest.status.test.test_search"
        self.consumer.message = {
            "id": "xtest:1"
        }
        # Trigger on_message and nothing happens
        self.consumer.on_message()

    def test_warc_created_on_message(self):
        self.consumer.routing_key = "warc_created"
        self.consumer.message = {
            "warc": {
                "path": "/var/folders/_d/3zzlntjs45nbq1f4dnv48c499mgzyf/T/tmpKwq9NL/test_collection/2015/07/28/11/test_collection-flickr-2015-07-28T11:17:36Z.warc.gz",
                "sha1": "7512e1c227c29332172118f0b79b2ca75cbe8979",
                "bytes": 26146,
                "id": "test_collection-flickr-2015-07-28T11:17:36Z",
                "date_created": "2015-07-28T11:17:36.640178"
            },
            "collection": {
                "path": "/var/folders/_d/3zzlntjs45nbq1f4dnv48c499mgzyf/T/tmpKwq9NL/test_collection",
                "id": "test_collection"
            },
            "harvest": {
                "id": "test:1",
            }
        }
        # Trigger on_message
        self.consumer.on_message()

        # Check created Warc model object
        warc = Warc.objects.get(warc_id="test_collection-flickr-2015-07-28T11:17:36Z")
        self.assertEqual(self.consumer.message["warc"]["path"], warc.path)
        self.assertEqual(self.consumer.message["warc"]["sha1"], warc.sha1)
        self.assertEqual(self.consumer.message["warc"]["bytes"], warc.bytes)
        self.assertEqual(iso8601.parse_date("2015-07-28T11:17:36.640178"), warc.date_created)
        self.assertEqual(self.harvest, warc.harvest)