# Copyright (c) 2022 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock


from tlab_google import abstract


class Test_build_service(TestCase):

    @mock.patch("googleapiclient.discovery.build")
    def test_api(self, build_mock: mock.Mock) -> None:
        api_mock = mock.Mock(parent=abstract.AbstractAPI)
        service = abstract.build_service(api_mock)
        self.assertEqual(service, build_mock.return_value)
        build_mock.assert_called_once_with(
            serviceName=api_mock.service_name,
            credentials=api_mock.credentials._credentials,
            version=api_mock.version
        )
