# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: client/version/versionpb/version.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='client/version/versionpb/version.proto',
  package='versionpb',
  syntax='proto3',
  serialized_options=_b('Z;github.com/pachyderm/pachyderm/src/client/version/versionpb'),
  serialized_pb=_b('\n&client/version/versionpb/version.proto\x12\tversionpb\x1a\x1bgoogle/protobuf/empty.proto\"J\n\x07Version\x12\r\n\x05major\x18\x01 \x01(\r\x12\r\n\x05minor\x18\x02 \x01(\r\x12\r\n\x05micro\x18\x03 \x01(\r\x12\x12\n\nadditional\x18\x04 \x01(\t2A\n\x03\x41PI\x12:\n\nGetVersion\x12\x16.google.protobuf.Empty\x1a\x12.versionpb.Version\"\x00\x42=Z;github.com/pachyderm/pachyderm/src/client/version/versionpbb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_VERSION = _descriptor.Descriptor(
  name='Version',
  full_name='versionpb.Version',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='major', full_name='versionpb.Version.major', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='minor', full_name='versionpb.Version.minor', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='micro', full_name='versionpb.Version.micro', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='additional', full_name='versionpb.Version.additional', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  serialized_start=82,
  serialized_end=156,
)

DESCRIPTOR.message_types_by_name['Version'] = _VERSION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Version = _reflection.GeneratedProtocolMessageType('Version', (_message.Message,), {
  'DESCRIPTOR' : _VERSION,
  '__module__' : 'client.version.versionpb.version_pb2'
  # @@protoc_insertion_point(class_scope:versionpb.Version)
  })
_sym_db.RegisterMessage(Version)


DESCRIPTOR._options = None

_API = _descriptor.ServiceDescriptor(
  name='API',
  full_name='versionpb.API',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=158,
  serialized_end=223,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetVersion',
    full_name='versionpb.API.GetVersion',
    index=0,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=_VERSION,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_API)

DESCRIPTOR.services_by_name['API'] = _API

# @@protoc_insertion_point(module_scope)
