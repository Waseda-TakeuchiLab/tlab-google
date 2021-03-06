# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import base64
from email.mime import text
import typing as t

from tlab_google import gmail, credentials


CREDENTIALS_MOCK = mock.Mock(spec_set=credentials.Credentials)


class TestGmailAPI_properties(TestCase):

    def setUp(self) -> None:
        self.api = gmail.GmailAPI(CREDENTIALS_MOCK)

    def test_service_name(self) -> None:
        self.assertEqual(self.api.service_name, "gmail")

    def test__service(self) -> None:
        with mock.patch("tlab_google.abstract.build_service") as build_mock:
            self.assertEqual(
                self.api._service,
                build_mock.return_value
            )
            build_mock.assert_called_once_with(self.api)


class TestGmailAPI_search_email(TestCase):

    def setUp(self) -> None:
        self.api = gmail.GmailAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        query: str = "",
        max_results: int = 0,
        page_token: str | None = None,
        label_ids: list[str] | None = None,
        include_spam_trash: bool = False
    ) -> None:
        with mock.patch("tlab_google.gmail.GmailAPI._service") as service_mock:
            messages = [
                {
                    "id": int(0).to_bytes(1, "little").hex(),
                    "threadId": int(0).to_bytes(1, "little").hex()
                }
            ]
            next_page_token = int(0).to_bytes(1, "little").hex()
            result_size_estimate = 100
            list = service_mock \
                .users.return_value \
                .messages.return_value \
                .list
            list.return_value.execute.return_value = {
                "messages": messages,
                "nextPageToken": next_page_token,
                "resultSizeEstimate": result_size_estimate
            }
            result = self.api.search_email(
                query=query,
                max_results=max_results,
                page_token=page_token,
                label_ids=label_ids,
                include_spam_trash=include_spam_trash
            )
            self.assertListEqual(result[0], messages)
            self.assertEqual(result[1], next_page_token)
            self.assertEqual(result[2], result_size_estimate)
            list.assert_called_once_with(
                userId=self.api.user_id,
                q=query,
                maxResults=max_results,
                pageToken=page_token or "",
                labelIds=label_ids or [],
                includeSpamTrash=include_spam_trash
            )
            list.return_value.execute.assert_called_once_with()

    def test_query(self) -> None:
        queries = [f"subject:(Subject{i})" for i in range(3)]
        for query in queries:
            with self.subTest(query=query):
                self._test(query=query)

    def test_max_results(self) -> None:
        max_results_list = list(range(100, 400, 100))
        for max_results in max_results_list:
            with self.subTest(max_results=max_results):
                self._test(max_results=max_results)

    def test_page_token(self) -> None:
        page_tokens = [f"pagetoken{i}" for i in range(3)]
        for page_token in page_tokens:
            with self.subTest(page_token=page_token):
                self._test(page_token=page_token)

    def test_label_ids(self) -> None:
        label_ids_list = [[f"labelId{i}" for i in range(j)] for j in range(3)]
        for label_ids in label_ids_list:
            with self.subTest(label_ids=label_ids):
                self._test(label_ids=label_ids)

    def test_include_spam_trash(self) -> None:
        for include_spam_trash in {True, False}:
            with self.subTest(include_spam_trash=include_spam_trash):
                self._test(include_spam_trash=include_spam_trash)


class TestGmailAPI_get_email(TestCase):

    def setUp(self) -> None:
        self.api = gmail.GmailAPI(CREDENTIALS_MOCK)

    def _test(
        self,
        id: str = "",
        format: t.Literal["minimal", "full", "raw", "metadata"] = "minimal"
    ) -> None:
        with mock.patch("tlab_google.gmail.GmailAPI._service") as service_mock:
            message = {
                "id": id,
                "threadId": int(0).to_bytes(1, "little").hex()
            }
            get = service_mock \
                .users.return_value \
                .messages.return_value \
                .get
            get.return_value.execute.return_value = message
            self.assertDictEqual(
                self.api.get_email(id, format=format),
                message
            )
            get.assert_called_once_with(
                userId=self.api.user_id,
                id=id,
                format=format
            )
            get.return_value.execute.assert_called_once_with()

    def test_id(self) -> None:
        ids = [f"00000000000000{i.to_bytes(1, 'little').hex()}" for i in range(3)]
        for id in ids:
            with self.subTest(id=id):
                self._test(id=id)

    def test_format(self) -> None:
        formats: list[t.Literal["minimal", "full", "raw", "metadata"]] = [
            "minimal", "full", "raw", "metadata"
        ]
        for format in formats:
            with self.subTest(format=format):
                self._test(format=format)


class TestGmailAPI_send_email(TestCase):

    def setUp(self) -> None:
        self.api = gmail.GmailAPI(CREDENTIALS_MOCK)

    def test_message(self) -> None:
        messages = [f"This is a mail test({i})." for i in range(3)]
        for message in messages:
            msg = text.MIMEText(message)
            with self.subTest(message=message):
                with mock.patch("tlab_google.gmail.GmailAPI._service") as service_mock:
                    self.api.send_email(msg)
                    send = service_mock \
                        .users.return_value \
                        .messages.return_value \
                        .send
                    send.assert_called_once_with(
                        userId=self.api.user_id,
                        body={"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}
                    )
                    send.return_value.execute.assert_called_once_with()


class TestGmailAPI_get_signature(TestCase):

    def setUp(self) -> None:
        self.api = gmail.GmailAPI(CREDENTIALS_MOCK)
        self.sendas_list = [
            {
                "sendAsEmail": f"foo{i}@example.com",
                "displayName": "foo",
                "signature": f"foo{i} bar",
                "isDefault": False
            } for i in range(3)
        ]
        self.default_sendas = {
            "sendAsEmail": "default@example.com",
            "displayName": "dafault user",
            "signature": "default user",
            "isDefault": True
        }
        self.sendas_list.append(self.default_sendas)

    def _test(self, address: str | None = None) -> None:
        with mock.patch("tlab_google.gmail.GmailAPI._service") as service_mock:
            list = service_mock \
                .users.return_value \
                .settings.return_value \
                .sendAs.return_value \
                .list
            list.return_value.execute.return_value = {"sendAs": self.sendas_list}
            addr_to_sendas = {sendas["sendAsEmail"]: sendas for sendas in self.sendas_list}
            if address is None:
                sendas = self.default_sendas
                self.assertEqual(self.api.get_signature(address=address), sendas.get("signature"))
            elif address in addr_to_sendas:
                sendas = addr_to_sendas[address]
                self.assertEqual(self.api.get_signature(address=address), sendas.get("signature"))
            else:
                with self.assertRaises(ValueError):
                    self.api.get_signature(address=address)
            list.assert_called_once_with(userId=self.api.user_id)
            list.return_value.execute.assert_called_once_with()

    def test_address(self) -> None:
        addresses: list[str | None] = [None, str(self.sendas_list[0].get("sendAsEmail")), "unexist@example.com"]
        for address in addresses:
            with self.subTest(address=address):
                self._test(address=address)
