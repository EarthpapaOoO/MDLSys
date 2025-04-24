# # likeSys/signals.py
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.db import transaction
# from django.db.models import F
# from .models import Vote_Document

# def update_document_stats(vote, created=False, deleted=False):
#     """
#     更新文档统计的核心逻辑
#     :param vote: Vote_Document实例
#     :param created: 是否是新建操作
#     :param deleted: 是否是删除操作
#     """
#     def _update():
#         doc = vote.document
        
#         # 需要处理的维度列表
#         dimensions = ['fact', 'style', 'background']
        
#         # 获取旧值（仅在更新时存在）
#         old_values = getattr(vote, '_old_values', None)
        
#         for dim in dimensions:
#             # 删除操作处理
#             if deleted:
#                 if getattr(vote, f"{dim}_choice"):
#                     setattr(doc, f"{dim}_positive", F(f"{dim}_positive") - 1)
#                 else:
#                     setattr(doc, f"{dim}_negative", F(f"{dim}_negative") - 1)
#                 continue
            
#             # 更新操作处理旧值
#             if old_values:
#                 old_choice = old_values.get(dim)
#                 if old_choice is not None:
#                     if old_choice:
#                         setattr(doc, f"{dim}_positive", F(f"{dim}_positive") - 1)
#                     else:
#                         setattr(doc, f"{dim}_negative", F(f"{dim}_negative") - 1)
            
#             # 处理新值（创建或更新）
#             new_choice = getattr(vote, f"{dim}_choice")
#             if new_choice:
#                 setattr(doc, f"{dim}_positive", F(f"{dim}_positive") + 1)
#             else:
#                 setattr(doc, f"{dim}_negative", F(f"{dim}_negative") + 1)
        
#         # 批量更新字段（避免多次查询）
#         update_fields = [f"{dim}_positive", f"{dim}_negative" for dim in dimensions]
#         doc.save(update_fields=update_fields)
    
#     # 确保在事务提交后执行
#     transaction.on_commit(_update)

# @receiver(post_save, sender=Vote_Document)
# def handle_vote_save(sender, instance, created, **kwargs):
#     """ 处理评价创建/更新 """
#     update_document_stats(instance, created=created)

# @receiver(post_delete, sender=Vote_Document)
# def handle_vote_delete(sender, instance, **kwargs):
#     """ 处理评价删除 """
#     update_document_stats(instance, deleted=True)