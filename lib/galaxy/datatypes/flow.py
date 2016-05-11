# -*- coding: utf-8 -*-
""" Clearing house for generic text datatypes that are not XML or tabular.
"""

import gzip
import json
import logging
import os
import re
import subprocess
import tempfile

from galaxy.datatypes.binary import Binary
from galaxy.datatypes.tabular import Tabular
from galaxy.datatypes.data import get_file_peek, Text
from galaxy.datatypes.metadata import MetadataElement
from galaxy.util import nice_size, string_as_bool
from . import data

log = logging.getLogger(__name__)
class FCS( Binary ):
    """Class describing an FCS binary sequence file"""
    file_ext = "fcs"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Binary FCS file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Binary FCSfile (%s)" % ( data.nice_size( dataset.get_size() ) )

Binary.register_unsniffable_binary_ext("fcs")

class FlowText( Tabular ):
    """Class describing an Flow Text file"""
    file_ext = "flowtext"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Text Flow file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Text Flow file (%s)" % ( data.nice_size( dataset.get_size() ) )

#Binary.register_unsniffable_binary_ext("flowtext")

class FlowClustered( Tabular ):
    """Class describing an Flow Text that has been clustered file"""
    file_ext = "flowclr"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Text Flow Clustered file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Text Flow Clustered file (%s)" % ( data.nice_size( dataset.get_size() ) )

#Binary.register_unsniffable_binary_ext("flowclr")

class FlowMFI( Tabular ):
    """Class describing an Flow MFI file"""
    file_ext = "flowmfi"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "MFI Flow file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "MFI Flow file (%s)" % ( data.nice_size( dataset.get_size() ) )

#Binary.register_unsniffable_binary_ext("flowmfi")

class FlowStats1( Tabular ):
    """Class describing a Flow Stats file"""
    file_ext = "flowstat1"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Flow Stats1 file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Flow Stats1 file (%s)" % ( data.nice_size( dataset.get_size() ) )

#Binary.register_unsniffable_binary_ext("flowstat1")

class FlowStats2( Tabular ):
    """Class describing a Flow Stats file"""
    file_ext = "flowstat2"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Flow Stats2 file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Flow Stats2 file (%s)" % ( data.nice_size( dataset.get_size() ) )

#Binary.register_unsniffable_binary_ext("flowstat2")

class FlowStats3( Tabular ):
    """Class describing a Flow Stats file"""
    file_ext = "flowstat3"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Flow Stats3 file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Flow Stats3 file (%s)" % ( data.nice_size( dataset.get_size() ) )

#Binary.register_unsniffable_binary_ext("flowstat3")


