#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009-2010, Nicolas Clairon
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest

from mongokit import *

class MapReduceTestCase(unittest.TestCase):
    def setUp(self):
        self.connection = Connection()
        self.col = self.connection['test']['mongokit']
        
    def tearDown(self):
        self.connection.drop_database('test')

    def test_simple_mapreduce(self):
        class MyDoc(Document):
            structure = {
                'user_id': int,
            }
        self.connection.register([MyDoc])

        for i in range(20):
            self.col.MyDoc({'user_id':i}).save()

        class MapDoc(Document):
            """
            document which handle result of map/reduce
            """
            structure = {
                'value':float,
            }
        self.connection.register([MapDoc])   

        m = 'function() { emit(this.user_id, 1); }'
        r = 'function(k,vals) { return 1; }'
        mapcol = self.col.map_reduce(m,r)
        mapdoc = mapcol.MapDoc.find_one()
        assert mapdoc == {u'_id': 0.0, u'value': 1.0}, mapdoc
        assert isinstance(mapdoc, MapDoc)


    def test_mapreduce_with_dbref(self):
        class MyDoc(Document):
            structure = {
                'user_id': int,
            }
        self.connection.register([MyDoc])

        for i in range(20):
            self.col.MyDoc({'_id':'bla'+str(i), 'user_id':i}).save()

        m = 'function() { emit(this.user_id, 1); }'
        r = 'function(k,vals) { return {"embed":{"$db":"test", "$ref":"mongokit", "$id":"bla"+k}}; }'

        class MapDoc(Document):
            use_autorefs = True
            structure = {
                'value':{
                    "embed":MyDoc,
                }
            }
        self.connection.register([MapDoc])   

        mapcol = self.col.map_reduce(m,r)
        mapdoc = mapcol.MapDoc.find_one()
        assert mapdoc == {u'_id': 0.0, u'value': {u'embed': {u'_id': u'bla0', u'user_id': 0}}}
        assert isinstance(mapdoc, MapDoc)

    def test_mapreduce_with_dbref_force_autorefs_current_db(self):
        class MyDoc(Document):
            structure = {
                'user_id': int,
            }
        self.connection.register([MyDoc])

        for i in range(20):
            self.col.MyDoc({'_id':'bla'+str(i), 'user_id':i}).save()

        m = 'function() { emit(this.user_id, 1); }'
        r = 'function(k,vals) { return {"embed":{"$ref":"mongokit", "$id":"bla"+k}}; }'

        class MapDoc(Document):
            use_autorefs = True
            force_autorefs_current_db = True
            structure = {
                'value':{
                    "embed":MyDoc,
                }
            }
        self.connection.register([MapDoc])   

        mapcol = self.col.map_reduce(m,r)
        mapdoc = mapcol.MapDoc.find_one()
        assert mapdoc == {u'_id': 0.0, u'value': {u'embed': {u'_id': u'bla0', u'user_id': 0}}}
        assert isinstance(mapdoc, MapDoc)


