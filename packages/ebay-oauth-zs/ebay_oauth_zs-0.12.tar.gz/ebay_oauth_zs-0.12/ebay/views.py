# from ebay.tasks import ebay_task_executor
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from zonesmart.marketplace.models import Channel
# from zonesmart.marketplace_task.models import MarketplaceTask


# class EbayTaskView(APIView):
#     celery_task = ebay_task_executor
#     action = None
#     handler_args = {}

#     def post(self, request, **kwargs):
#         task_id = self.add_marketplace_task(request, **kwargs)
#         self.celery_task.delay(task_id=task_id)
#         return Response('Задание выполняется', status=status.HTTP_200_OK)

#     def add_marketplace_task(self, request, **kwargs):
#         entity_id = kwargs.pop('id', None)
#         channel_id = kwargs.pop('channel_id', None)
#         if channel_id:
#             channel = Channel.objects.get(id=channel_id)
#         elif entity_id:
#             entity = self.action(entity_id=entity_id).entity
#             channel = Channel.objects.get(id=entity.channel.id)
#         else:
#             channel = None

#         task = MarketplaceTask.objects.create(
#             channel=channel,
#             entity_id=entity_id,
#             action=self.action.description,
#             handler_class_name=self.action.__name__,
#             handler_class_module=self.action.__module__,
#         )
#         task.add_handler_args(**self.handler_args, **kwargs)
#         task.publish()
#         return task.id
