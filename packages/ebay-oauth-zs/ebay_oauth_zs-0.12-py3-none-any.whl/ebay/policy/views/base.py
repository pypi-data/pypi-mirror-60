from zonesmart import remote_action_views, views


class PolicyViewSet(
    remote_action_views.RemoteDownloadListActionByChannel,
    remote_action_views.RemoteDeleteAction,
    remote_action_views.RemoteCreateAction,
    remote_action_views.RemoteUpdateAction,
    views.GenericSerializerModelViewSet,
):
    """
    Base ViewSet for policy
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(channel__marketplace_user_account__user=self.request.user)
        )
