# likeSys/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from .models import Vote_Document

def update_document_stats(vote, created=False, deleted=False):
    """
    更新文档统计的核心逻辑
    :param vote: Vote_Document实例
    :param created: 是否是新建操作
    :param deleted: 是否是删除操作
    """


@receiver(post_save, sender=Vote_Document)
def handle_vote_save(sender, instance, created, **kwargs):
    """ 处理评价创建/更新 """
    update_document_stats(instance, created=created)

@receiver(post_delete, sender=Vote_Document)
def handle_vote_delete(sender, instance, **kwargs):
    """ 处理评价删除 """
    update_document_stats(instance, deleted=True)

# likeSys/signals.py
@receiver(post_save, sender=Vote_Document)
def handle_vote_change(sender, instance, created, **kwargs):
    """修正后的信号处理"""
    
    def _update():
        doc = instance.document
        old_values = getattr(instance, '_old_values', {})
        
        with transaction.atomic():
            # 处理旧值（更新时）
            if not created:
                for dim in ['fact', 'style', 'background']:
                    if dim in old_values:
                        old_choice = old_values[dim]
                        field = f"{dim}_positive" if old_choice else f"{dim}_negative"
                        doc.__class__.objects.filter(id=doc.id).update(
                            **{field: F(field) - 1}  # 修正为-1
                        )
            
            # 处理新值
            for dim in ['fact', 'style', 'background']:
                new_choice = getattr(instance, f"{dim}_choice")
                if new_choice is not None:
                    field = f"{dim}_positive" if new_choice else f"{dim}_negative"
                    doc.__class__.objects.filter(id=doc.id).update(
                        **{field: F(field) + 1}  # 修正为+1
                    )
    
    transaction.on_commit(_update)