"""
Test subjects
"""

from json import dumps as json_dumps
from os import getenv
from unittest import TestCase
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.utils import get_auth

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

DISPLAY_NAME = "Subject display name"
WALLET_PUB_KEYS = [
    (
        "045c4ce14da4a0b393f9e961344aa19a868918c5ca50716e9f48a1ce5d3b6adcd27575"
        "c1c8d53f3c8dba1e32384cfa21b04c2fc89ea56b9490f17db87a44da260b"
    )
]
TESSERA_PUB_KEYS = ["SOvH7mhAbVHK7MSBWXUe96ptpPP3GbWi0M7tsE1jVCc="]


class TestSubjects(TestCase):
    """
    Test Archivist Subjects Create method
    """

    maxDiff = None

    def setUp(self):
        auth = get_auth(
            auth_token_filename=getenv("TEST_AUTHTOKEN_FILENAME"),
            client_id=getenv("TEST_CLIENT_ID"),
            client_secret_filename=getenv("TEST_CLIENT_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("TEST_ARCHIVIST"), auth, verify=False)
        self.display_name = f"{DISPLAY_NAME} {uuid4()}"

    def test_subjects_create(self):
        """
        Test subject creation
        """
        subject = self.arch.subjects.create(
            self.display_name, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
        )
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )

    def test_subjects_update(self):
        """
        Test subject update
        """
        subject = self.arch.subjects.create(
            self.display_name, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
        )
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        subject = self.arch.subjects.update(
            subject["identity"],
            display_name=self.display_name,
            wallet_pub_keys=WALLET_PUB_KEYS,
            tessera_pub_keys=TESSERA_PUB_KEYS,
        )

    def test_subjects_delete(self):
        """
        Test subject delete
        """
        subject = self.arch.subjects.create(
            self.display_name, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
        )
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        subject = self.arch.subjects.delete(
            subject["identity"],
        )
        self.assertEqual(
            subject,
            {},
            msg="Incorrect subject",
        )

    def test_subjects_list(self):
        """
        Test subject list
        """
        subjects = self.arch.subjects.list(display_name=self.display_name)
        for i, subject in enumerate(subjects):
            print(i, ":", json_dumps(subject, indent=4))

        for subject in subjects:
            self.assertEqual(
                subject["display_name"],
                self.display_name,
                msg="Incorrect display name",
            )
            self.assertGreater(
                len(subject["display_name"]),
                0,
                msg="Incorrect display name",
            )

    def test_subjects_count(self):
        """
        Test subject count
        """
        count = self.arch.subjects.count()
        self.assertGreater(
            count,
            0,
            msg="Count is zero",
        )
