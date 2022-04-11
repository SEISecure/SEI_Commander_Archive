#!/usr/bin/env python3

from athena_messages.principal_athena_message_pb2 import Principal_Athena_Message

import unittest
import uuid


class TestPrincipalAthenaMessage(unittest.TestCase):
    def test_create_message(self):
        msg = Principal_Athena_Message()
        msg.sender_uuid = str(uuid.uuid4())
        msg.message_type = "Command"
        msg.destination_id.append('2')
        artemis_msg = msg.artemis.add()
        artemis_msg.uuid = str(uuid.uuid4())

        msg2 = Principal_Athena_Message()
        msg2.ParseFromString(msg.SerializeToString())

        self.assertEqual(msg.sender_uuid, msg2.sender_uuid)
        self.assertEqual(msg.message_type, msg2.message_type)
        self.assertEqual(1, len(msg2.destination_id))
        self.assertEqual('2', msg2.destination_id[0])
        self.assertEqual(1, len(msg2.artemis))
        self.assertEqual(msg.artemis[0].uuid, msg2.artemis[0].uuid)


if __name__ == '__main__':
    unittest.main()
