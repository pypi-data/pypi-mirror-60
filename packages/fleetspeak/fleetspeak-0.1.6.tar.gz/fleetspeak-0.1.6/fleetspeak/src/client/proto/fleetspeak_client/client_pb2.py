# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fleetspeak/src/client/proto/fleetspeak_client/client.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='fleetspeak/src/client/proto/fleetspeak_client/client.proto',
  package='fleetspeak.client',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n:fleetspeak/src/client/proto/fleetspeak_client/client.proto\x12\x11\x66leetspeak.client\"\x9f\x01\n\x12\x43ommunicatorConfig\x12\x1e\n\x16max_poll_delay_seconds\x18\x02 \x01(\x05\x12 \n\x18max_buffer_delay_seconds\x18\x03 \x01(\x05\x12!\n\x19min_failure_delay_seconds\x18\x04 \x01(\x05\x12$\n\x1c\x66\x61ilure_suicide_time_seconds\x18\x05 \x01(\x05\"Y\n\x0b\x43lientState\x12\x12\n\nclient_key\x18\x01 \x01(\x0c\x12\x18\n\x10sequencing_nonce\x18\x07 \x01(\x04\x12\x1c\n\x14revoked_cert_serials\x18\x08 \x03(\x0c\x62\x06proto3')
)




_COMMUNICATORCONFIG = _descriptor.Descriptor(
  name='CommunicatorConfig',
  full_name='fleetspeak.client.CommunicatorConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='max_poll_delay_seconds', full_name='fleetspeak.client.CommunicatorConfig.max_poll_delay_seconds', index=0,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_buffer_delay_seconds', full_name='fleetspeak.client.CommunicatorConfig.max_buffer_delay_seconds', index=1,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min_failure_delay_seconds', full_name='fleetspeak.client.CommunicatorConfig.min_failure_delay_seconds', index=2,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='failure_suicide_time_seconds', full_name='fleetspeak.client.CommunicatorConfig.failure_suicide_time_seconds', index=3,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=82,
  serialized_end=241,
)


_CLIENTSTATE = _descriptor.Descriptor(
  name='ClientState',
  full_name='fleetspeak.client.ClientState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_key', full_name='fleetspeak.client.ClientState.client_key', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sequencing_nonce', full_name='fleetspeak.client.ClientState.sequencing_nonce', index=1,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='revoked_cert_serials', full_name='fleetspeak.client.ClientState.revoked_cert_serials', index=2,
      number=8, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=243,
  serialized_end=332,
)

DESCRIPTOR.message_types_by_name['CommunicatorConfig'] = _COMMUNICATORCONFIG
DESCRIPTOR.message_types_by_name['ClientState'] = _CLIENTSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CommunicatorConfig = _reflection.GeneratedProtocolMessageType('CommunicatorConfig', (_message.Message,), {
  'DESCRIPTOR' : _COMMUNICATORCONFIG,
  '__module__' : 'fleetspeak.src.client.proto.fleetspeak_client.client_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.client.CommunicatorConfig)
  })
_sym_db.RegisterMessage(CommunicatorConfig)

ClientState = _reflection.GeneratedProtocolMessageType('ClientState', (_message.Message,), {
  'DESCRIPTOR' : _CLIENTSTATE,
  '__module__' : 'fleetspeak.src.client.proto.fleetspeak_client.client_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.client.ClientState)
  })
_sym_db.RegisterMessage(ClientState)


# @@protoc_insertion_point(module_scope)
