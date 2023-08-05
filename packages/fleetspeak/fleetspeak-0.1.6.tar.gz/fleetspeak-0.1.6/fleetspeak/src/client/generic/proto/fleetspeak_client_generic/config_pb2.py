# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fleetspeak/src/client/generic/proto/fleetspeak_client_generic/config.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='fleetspeak/src/client/generic/proto/fleetspeak_client_generic/config.proto',
  package='fleetspeak.client.generic',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\nJfleetspeak/src/client/generic/proto/fleetspeak_client_generic/config.proto\x12\x19\x66leetspeak.client.generic\"\x83\x02\n\x06\x43onfig\x12\x15\n\rtrusted_certs\x18\x01 \x01(\t\x12\x0e\n\x06server\x18\x02 \x03(\t\x12\x14\n\x0c\x63lient_label\x18\x03 \x03(\t\x12J\n\x12\x66ilesystem_handler\x18\x04 \x01(\x0b\x32,.fleetspeak.client.generic.FilesystemHandlerH\x00\x12\x46\n\x10registry_handler\x18\x05 \x01(\x0b\x32*.fleetspeak.client.generic.RegistryHandlerH\x00\x12\x11\n\tstreaming\x18\x06 \x01(\x08\x42\x15\n\x13persistence_handler\"H\n\x11\x46ilesystemHandler\x12\x1f\n\x17\x63onfiguration_directory\x18\x01 \x01(\t\x12\x12\n\nstate_file\x18\x02 \x01(\t\",\n\x0fRegistryHandler\x12\x19\n\x11\x63onfiguration_key\x18\x01 \x01(\tb\x06proto3')
)




_CONFIG = _descriptor.Descriptor(
  name='Config',
  full_name='fleetspeak.client.generic.Config',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='trusted_certs', full_name='fleetspeak.client.generic.Config.trusted_certs', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='server', full_name='fleetspeak.client.generic.Config.server', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='client_label', full_name='fleetspeak.client.generic.Config.client_label', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='filesystem_handler', full_name='fleetspeak.client.generic.Config.filesystem_handler', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='registry_handler', full_name='fleetspeak.client.generic.Config.registry_handler', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='streaming', full_name='fleetspeak.client.generic.Config.streaming', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
    _descriptor.OneofDescriptor(
      name='persistence_handler', full_name='fleetspeak.client.generic.Config.persistence_handler',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=106,
  serialized_end=365,
)


_FILESYSTEMHANDLER = _descriptor.Descriptor(
  name='FilesystemHandler',
  full_name='fleetspeak.client.generic.FilesystemHandler',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='configuration_directory', full_name='fleetspeak.client.generic.FilesystemHandler.configuration_directory', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='state_file', full_name='fleetspeak.client.generic.FilesystemHandler.state_file', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=367,
  serialized_end=439,
)


_REGISTRYHANDLER = _descriptor.Descriptor(
  name='RegistryHandler',
  full_name='fleetspeak.client.generic.RegistryHandler',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='configuration_key', full_name='fleetspeak.client.generic.RegistryHandler.configuration_key', index=0,
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
  serialized_start=441,
  serialized_end=485,
)

_CONFIG.fields_by_name['filesystem_handler'].message_type = _FILESYSTEMHANDLER
_CONFIG.fields_by_name['registry_handler'].message_type = _REGISTRYHANDLER
_CONFIG.oneofs_by_name['persistence_handler'].fields.append(
  _CONFIG.fields_by_name['filesystem_handler'])
_CONFIG.fields_by_name['filesystem_handler'].containing_oneof = _CONFIG.oneofs_by_name['persistence_handler']
_CONFIG.oneofs_by_name['persistence_handler'].fields.append(
  _CONFIG.fields_by_name['registry_handler'])
_CONFIG.fields_by_name['registry_handler'].containing_oneof = _CONFIG.oneofs_by_name['persistence_handler']
DESCRIPTOR.message_types_by_name['Config'] = _CONFIG
DESCRIPTOR.message_types_by_name['FilesystemHandler'] = _FILESYSTEMHANDLER
DESCRIPTOR.message_types_by_name['RegistryHandler'] = _REGISTRYHANDLER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Config = _reflection.GeneratedProtocolMessageType('Config', (_message.Message,), {
  'DESCRIPTOR' : _CONFIG,
  '__module__' : 'fleetspeak.src.client.generic.proto.fleetspeak_client_generic.config_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.client.generic.Config)
  })
_sym_db.RegisterMessage(Config)

FilesystemHandler = _reflection.GeneratedProtocolMessageType('FilesystemHandler', (_message.Message,), {
  'DESCRIPTOR' : _FILESYSTEMHANDLER,
  '__module__' : 'fleetspeak.src.client.generic.proto.fleetspeak_client_generic.config_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.client.generic.FilesystemHandler)
  })
_sym_db.RegisterMessage(FilesystemHandler)

RegistryHandler = _reflection.GeneratedProtocolMessageType('RegistryHandler', (_message.Message,), {
  'DESCRIPTOR' : _REGISTRYHANDLER,
  '__module__' : 'fleetspeak.src.client.generic.proto.fleetspeak_client_generic.config_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.client.generic.RegistryHandler)
  })
_sym_db.RegisterMessage(RegistryHandler)


# @@protoc_insertion_point(module_scope)
