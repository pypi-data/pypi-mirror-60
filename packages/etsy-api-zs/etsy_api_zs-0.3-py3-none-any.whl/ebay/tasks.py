# import importlib
# import sys
# import traceback

# from config import celery_app

# from zonesmart.marketplace_task.models import MarketplaceTask
# from zonesmart.utils.logger import get_logger

# logger = get_logger(__file__)


# @celery_app.task
# def ebay_task_executor(task_id):
#     task_done = False
#     message = 'Не удалось выполнить задание.'
#     try:
#         task = MarketplaceTask.objects.get(id=task_id)
#         module = importlib.import_module(task.handler_class_module)
#         action_class = getattr(module, task.handler_class_name, None)
#         action = action_class(
#             channel_id=task.channel.id,
#             entity_id=task.entity_id,
#         )
#         is_success, message, objects = action(**task.handler_args_dict)
#         if is_success:
#             task_done = True
#     except Exception:
#         logger.error(f'Ошибка при выполнении задания (task ID: {task.id}).')
#         traceback.print_exception(*sys.exc_info())
#     finally:
#         if task_done:
#             task.status = task.DONE
#         else:
#             task.status = task.FAILED
#         task.info = message
#         task.save()
#     return task_done
