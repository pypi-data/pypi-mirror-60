# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor laus data."""

from ._us_labor_base_blob_info import UsLaborBaseBlobInfo


class UsLaborLAUSBlobInfo(UsLaborBaseBlobInfo):
    """Blob info of US labor laus Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_laus'
        self.blob_relative_path = "laus/"
