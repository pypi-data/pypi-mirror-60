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
import setuptools

setuptools.setup(
    name='infraform',
    version='0.1',
    description='Creating the infra you need, not the one you want',
    author='Arie Bregman',
    author_email='abregman@redhat.com',
    packages=setuptools.find_packages(),
    python_requires='>3.0.0',
    include_package_data=True,
    entry_points={
        'console_scripts': ['infraform = infraform.cli.main:main',
                            'ifr = infraform.cli.main:main']}
)
