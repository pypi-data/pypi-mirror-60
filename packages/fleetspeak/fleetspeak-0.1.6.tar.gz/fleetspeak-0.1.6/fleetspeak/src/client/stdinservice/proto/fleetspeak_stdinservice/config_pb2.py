# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fleetspeak/src/client/stdinservice/proto/fleetspeak_stdinservice/config.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='fleetspeak/src/client/stdinservice/proto/fleetspeak_stdinservice/config.proto',
  package='fleetspeak.stdinservice',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\nMfleetspeak/src/client/stdinservice/proto/fleetspeak_stdinservice/config.proto\x12\x17\x66leetspeak.stdinservice\"\x15\n\x06\x43onfig\x12\x0b\n\x03\x63md\x18\x01 \x01(\tb\x06proto3')
)




_CONFIG = _descriptor.Descriptor(
  name='Config',
  full_name='fleetspeak.stdinservice.Config',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cmd', full_name='fleetspeak.stdinservice.Config.cmd', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=106,
  serialized_end=127,
)

DESCRIPTOR.message_types_by_name['Config'] = _CONFIG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Config = _reflection.GeneratedProtocolMessageType('Config', (_message.Message,), {
  'DESCRIPTOR' : _CONFIG,
  '__module__' : 'fleetspeak.src.client.stdinservice.proto.fleetspeak_stdinservice.config_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.stdinservice.Config)
  })
_sym_db.RegisterMessage(Config)


# @@protoc_insertion_point(module_scope)
