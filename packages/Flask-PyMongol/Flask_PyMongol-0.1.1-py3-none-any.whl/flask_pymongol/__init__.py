# BSD 2-Clause License

# Copyright (c) 2020, Mateo Upegui Borja
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''TODO: Add docstring
'''
import pymongo
from flask import current_app, _app_ctx_stack

class PyMongol(object):
    '''TODO: Add docstring
    '''
    def __init__(self, app=None, database_name=None, **kwargs):
        '''TODO: Add docstring
        '''
        self._config_database_name = database_name
        self._config_kwargs = kwargs

        if app is not None:
            self.init_app(app)

    def init_app(self, app, database_name=None, **kwargs):
        '''TODO: Add docstring
        '''
        self._config_database_name = database_name
        self._config_kwargs = kwargs

        app.teardown_appcontext(self._teardown)

    def _connect_client(self, *args, **kwargs):
        '''TODO: Add docstring and add logic to check app.config for usable parameters
        '''
        return pymongo.MongoClient(*args, **kwargs)

    def _connect_database(self, client, database_name):
        '''TODO: Add docstring and add logic to check app.config for usable parameters
        '''
        return client[database_name]

    def _teardown(self, exception):
        '''TODO: Add docstring
        '''
        context = _app_ctx_stack.top

        if hasattr(context, 'mongo_client'):
            if hasattr(context, 'mongo_database'):
                pass
            context.mongo_client.close()


    @property
    def mongo_client(self):
        '''TODO: Add docstring
        '''
        context = _app_ctx_stack.top

        if context is not None:
            if not hasattr(context, 'mongo_client'):
                context.mongo_client = self._connect_client(**self._config_kwargs)
            return context.mongo_client

    @property
    def mongo_database(self):
        '''TODO: Add docstring
        '''
        context = _app_ctx_stack.top

        if context is not None:
            if hasattr(context, 'mongo_client'):
                if not hasattr(context, 'mongo_database'):
                    context.mongo_database = self._connect_database(context.mongo_client,
                                                                    self._config_database_name)
            else:
                context.mongo_client = self._connect_client(**self._config_kwargs)
                context.mongo_database = self._connect_database(context.mongo_client,
                                                                self._config_database_name)
                pass
            return context.mongo_database
    