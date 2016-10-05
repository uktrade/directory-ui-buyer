class RemoteError(Exception):
    pass


class DirectoryAPIClient(object):

    RemoteError = RemoteError

    def acknowledge_email_confirmed(self, identifier):
        # todo: raise a RemoteError if acknowledgement fails
        pass


client = DirectoryAPIClient()
