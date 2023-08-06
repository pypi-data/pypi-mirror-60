# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
from mock import patch, MagicMock
from module_build_service.scheduler.consumer import MBSConsumer
from module_build_service.messaging import KojiTagChange, KojiRepoChange


class TestConsumer:
    def test_get_abstracted_msg_fedmsg(self):
        """
        Test the output of get_abstracted_msg() when using the
        fedmsg backend.
        """
        hub = MagicMock(config={})
        consumer = MBSConsumer(hub)
        msg = {
            "username": "apache",
            "source_name": "datanommer",
            "i": 1,
            "timestamp": 1505492681.0,
            "msg_id": "2017-0627b798-f241-4230-b365-8a8a111a8ec5",
            "crypto": "x509",
            "topic": "org.fedoraproject.prod.buildsys.tag",
            "headers": {},
            "source_version": "0.8.1",
            "msg": {
                "build_id": 962861,
                "name": "python3-virtualenv",
                "tag_id": 263,
                "instance": "primary",
                "tag": "epel7-pending",
                "user": "bodhi",
                "version": "15.1.0",
                "owner": "orion",
                "release": "1.el7",
            },
        }
        msg_obj = consumer.get_abstracted_msg(msg)
        assert isinstance(msg_obj, KojiTagChange)
        assert msg_obj.msg_id == msg["msg_id"]
        assert msg_obj.tag == msg["msg"]["tag"]
        assert msg_obj.artifact == msg["msg"]["name"]

    @patch("module_build_service.scheduler.consumer.models")
    @patch.object(MBSConsumer, "process_message")
    def test_consume_fedmsg(self, process_message, models):
        """
        Test the MBSConsumer.consume() method when using the
        fedmsg backend.
        """
        hub = MagicMock(config={})
        consumer = MBSConsumer(hub)
        msg = {
            "topic": "org.fedoraproject.prod.buildsys.repo.done",
            "headers": {},
            "body": {
                "username": "apache",
                "source_name": "datanommer",
                "i": 1,
                "timestamp": 1405126329.0,
                "msg_id": "2014-adbc33f6-51b0-4fce-aa0d-3c699a9920e4",
                "crypto": "x509",
                "topic": "org.fedoraproject.prod.buildsys.repo.done",
                "headers": {},
                "source_version": "0.6.4",
                "msg": {
                    "instance": "primary",
                    "repo_id": 400859,
                    "tag": "f22-build",
                    "tag_id": 278,
                },
            },
        }
        consumer.consume(msg)
        assert process_message.call_count == 1
        msg_obj = process_message.call_args[0][0]
        assert isinstance(msg_obj, KojiRepoChange)
        assert msg_obj.msg_id == msg["body"]["msg_id"]
        assert msg_obj.repo_tag == msg["body"]["msg"]["tag"]
