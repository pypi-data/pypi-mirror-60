# Copyright 2019 Arie Bregman
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import crayons
import logging

from infraform.list import list_scenarios

LOG = logging.getLogger(__name__)


def main(args):
    """Runner main entry."""
    LOG.info("Listing scenarios...\n")
    list_scenarios()
    LOG.info("\nTo display a scenario use {}\nTo run a scenario use {}".format(
        crayons.yellow("ifr show <scenario_name>"),
        crayons.yellow("ifr run --scenario <scenario_name>")))
