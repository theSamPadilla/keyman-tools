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
import sys

from cli.cli import param_parser
import secret_manager.handler as sm
import web3signer.handler as w3s

if __name__ == "__main__":

    #Parse configs
    configs = param_parser(sys.argv[1:]) #?Pass only the parameters
    if not configs:
       exit(1)
    
    #Unpack configs
    command, command_flags, subcommand, subcommand_flags = configs

    #Route to the appropriate module
    if command == "secret-manager":
        sm.handler(command_flags, subcommand, subcommand_flags)
    elif command == "web3signer":
        w3s.handler(command_flags, subcommand, subcommand_flags)
