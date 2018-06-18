"""
API operations for uploaded files in storage.
"""
import logging
import os
import re

from galaxy.exceptions import MessageException, NotImplemented
from galaxy.web import expose_api_anonymous
from galaxy.web.base.controller import BaseAPIController

log = logging.getLogger(__name__)


class UploadsAPIController(BaseAPIController):

    READ_CHUNK_SIZE = 2 ** 16

    @expose_api_anonymous
    def index(self, trans, **kwd):
        raise NotImplemented("Listing uploads is not implemented.")

    @expose_api_anonymous
    def create(self, trans, payload, **kwd):
        """
        POST /api/uploads/
        """
        session_id = payload.get("session_id")
        session_start = payload.get("session_start")
        session_chunk = payload.get("session_chunk")
        if re.match('^[\w-]+$', session_id) is None:
            raise MessageException("Requires a session id.")
        if session_start is None:
            raise MessageException("Requires a session start.")
        if not hasattr(session_chunk, "file"):
            raise MessageException("Requires a session chunk.")
        target_file = os.path.join(trans.app.config.new_file_path, session_id)
        target_size = 0
        if os.path.exists(target_file):
            target_size = os.path.getsize(target_file)
        if session_start != target_size:
            raise MessageException("Incorrect session start.")
        chunk_size = os.fstat(session_chunk.file.fileno()).st_size
        if chunk_size > trans.app.config.chunk_upload_size:
            raise MessageException("Invalid chunk size.")
        with open(target_file, "a") as f:
            while True:
                read_chunk = session_chunk.file.read(self.READ_CHUNK_SIZE)
                if not read_chunk:
                    break
                f.write(read_chunk)
        session_chunk.file.close()
        return {"message": "Successful."}
