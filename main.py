#!/usr/bin/python3
############################################
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############################################

"""Batch Secure Upload of Validator Signing Keys to Google Cloud Secret Manager"""
# Built in Imports
import sys

# Module imports
from config.config import config_tool
import create.atomic_secrets as atomic
import create.single_secrets as single

if __name__ == "__main__":
    configs = config_tool(sys.argv)
    if not configs:
        sys.exit(3)
    
    # Unpack configs ans pass to creation functions
    project_id, key_directory_path, google_adc, output_dir, optimistic, skip, p_atomic = configs # pylint: disable=unbalanced-tuple-unpacking
    if configs[-1]:
        atomic.create_atomic_secrets(project_id, key_directory_path, output_dir)
    else:
        single.create_single_secrets(project_id, key_directory_path, output_dir,
                                    optimistic, skip)
