import json
import unittest
from flask import g
from runner import create_app, db


class TestEventBidder(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        with self.app.app_context():
        # create all tables
            db.create_all()
            db.session.commit()
    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def test_edit_event_bidder_by_id(self):
        # TODO : Replace All Input PUT
        res = self.client().put('/event/event_bidder', headers={'user': g.user}, json={
            "id": "Long",
            "talent_id": "Long",
            "event_id": "Long",
            "bid_amount": "Double",
            "notes": "String",
            "event": "?"
        })
        self.assertIs(res.status_code, 200)

    def test_add_event_bidder(self):
        # TODO : Replace All Input POST
        res = self.client().post('/event/event_bidder', headers={'user': g.user}, json={
            "id": "Long",
            "talent_id": "Long",
            "event_id": "Long",
            "bid_amount": "Double",
            "notes": "String",
            "event": "?"
        })
        self.assertIs(res.status_code, 200)

    def test_find_event_bidder_by_id(self):
        # TODO : Replace All Input GET
        res = self.client().get('/event/event_bidder/<id>', headers={'user': g.user}, params={
            'id': 'Long'
        })
        self.assertIs(res.status_code, 200)