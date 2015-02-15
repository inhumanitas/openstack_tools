# coding: utf-8

from keystoneclient.v2_0 import client

from openstack_tools.helpers import cached_by_args


class KSClient(object):
    u"""Provides keystone user auth mechanism"""

    def __init__(self):
        super(KSClient, self).__init__()
        self._ksclient = None

    def __call__(self, auth_url, username, password, **kwargs):
        u"""Create keystone client instance
        :param auth_url: full url to client
        :param username, password: auth data
        :param kwargs: additional options to keystone client
        Note: if you want to use raw_token provide tenant_name O_o???
        """
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.kwargs = kwargs
        ks_client = self._get_client(
            username=username, password=password, auth_url=auth_url, **kwargs)
        self._ksclient = ks_client
        return self

    def _get_client(self, **kwargs):
        return client.Client(**kwargs)

    def authenticate(self):
        return self.ksclient.authenticate()

    @property
    def ksclient(self):
        u"""Original keystone client"""
        return self._ksclient

    @property
    def token(self):
        u"""Authenticated token"""
        t = None
        if self._ksclient:
            t = self._ksclient.auth_token
        return t

    @property
    def raw_token(self):
        raw_t = None
        if self._ksclient and self.token:
            kwargs = self.kwargs or {}
            kwargs['auth_url'] = self.auth_url
            kwargs['token'] = self.token

            raw_t = self._ksclient.get_raw_token_from_identity_service(
                **kwargs
            )
        return raw_t


ks_client = KSClient()


@cached_by_args
def auth_ks_client_by_pass(auth_dict):
    u"""Authenticate in keystone by login\pass
    :param auth_dict: params needed by keaytone client
        {
            'auth_url' url to keystone. http://host:5000/v2.0
            'username' user name and
            'password' password for client
            'tenant_name' valid tenant name
            ... other args will be passed to client
        }
    :return keystone client instance
    """
    assert isinstance(auth_dict, dict)

    required_keys = ['auth_url', 'username', 'password', 'tenant_name']
    assert_req = lambda kv: kv[1] and kv[0] in required_keys
    assert map(assert_req, auth_dict.iteritems()), (
        "Not enough actual parameters. "
        "You should provide: %s" % '; '.join(required_keys))

    return ks_client(**auth_dict)