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

from tempest.lib.services.network import base


class ExtensionsClient(base.BaseNetworkClient):

    def show_extension(self, ext_alias, **fields):
        """Show extension details.

        For a full list of available parameters, please refer to the official
        API reference:
        https://docs.openstack.org/api-ref/network/v2/index.html#show-extension-details
        """
        uri = '/extensions/%s' % ext_alias
        return self.show_resource(uri, **fields)

    def list_extensions(self, **filters):
        """List extensions.

        For a full list of available parameters, please refer to the official
        API reference:
        https://docs.openstack.org/api-ref/network/v2/index.html#list-extensions
        """
        uri = '/extensions'
        return self.list_resources(uri, **filters)
