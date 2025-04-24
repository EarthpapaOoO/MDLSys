from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .models import Document, Vote_Document
from django.db import transaction
from django.db import models
from django.contrib.auth import authenticate, login
from django.shortcuts import  redirect
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

def document_detail(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote_Document.objects.filter(
            user=request.user, 
            document=document
        ).first()
    return render(request, 'documents/detail.html', {
        'document': document,
        'user_vote': user_vote
    })

@require_http_methods(["POST"])
@transaction.atomic
def submit_rating(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    if not request.user.is_authenticated:
        return JsonResponse({'error': '请先登录'}, status=403)


    # 获取参数
    data = request.POST
    required_fields = ['fact', 'style', 'background']
    if not all(field in data for field in required_fields):
        return JsonResponse({'error': '请完成所有维度的评价'}, status=400)

    # # 解析选择
    #  # 解析选择（新增null处理）
    # def parse_choice(value):
    #     return {'positive': True, 'negative': False}.get(value, None)

    fact_choice = data['fact'] == 'positive'
    style_choice = data['style'] == 'positive'
    background_choice = data['background'] == 'positive'

# # 删除原有评价（如果有维度取消选择）
#     if any(choice is None for choice in [fact_choice, style_choice]):
#         Vote_Document.objects.filter(
#             user=request.user,
#             document=document
#         ).delete()
#         return JsonResponse({'success': True})
    # 创建或更新评价
    vote, created = Vote_Document.objects.update_or_create(
        user=request.user,
        document=document,
        defaults={
            'fact_choice': fact_choice,
            'style_choice': style_choice,
            'background_choice': background_choice
        }
    )

    # 更新文档统计（需优化为信号处理）
    def update_counter(field, is_positive):
        if is_positive:
            Document.objects.filter(id=document.id).update(
                **{f"{field}_positive": models.F(f"{field}_positive") + 1}
            )
        else:
            Document.objects.filter(id=document.id).update(
                **{f"{field}_negative": models.F(f"{field}_negative") + 1}
            )

    # 这里需要处理旧值的影响（实际项目建议使用信号）
    update_counter('fact', fact_choice)
    update_counter('style', style_choice)
    update_counter('background', background_choice)

    return JsonResponse({'success': True})

