# likeSys/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from .models import Vote_Document


@receiver(post_save, sender=Vote_Document)
def handle_vote_change(sender, instance, created, **kwargs):

    
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