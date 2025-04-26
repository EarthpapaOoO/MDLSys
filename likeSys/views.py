#likeSys/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Document, Vote_Document
from django.db import transaction

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

    # 参数解析（允许空值处理）
    def parse_choice(value):
        return {'positive': True, 'negative': False}.get(value, None)
    
    data = {
        'fact': request.POST.get('fact'),
        'style': request.POST.get('style'),
        'background': request.POST.get('background')
    }

    # 验证必须完成所有选择
    if any(v is None for v in data.values()):
        return JsonResponse({'error': '请完成所有维度的评价'}, status=400)

    # 获取或创建评价记录
    vote, created = Vote_Document.objects.update_or_create(
        user=request.user,
        document=document,
        defaults={
            'fact_choice': parse_choice(data['fact']),
            'style_choice': parse_choice(data['style']),
            'background_choice': parse_choice(data['background'])
            
        }
    )
    # document.refresh_from_db()

    stats = {
        'fact': {
            'positive': Vote_Document.objects.filter(document=document, fact_choice=True).count(),
            'negative': Vote_Document.objects.filter(document=document, fact_choice=False).count()
        },
        'style': {
            'positive': Vote_Document.objects.filter(document=document, style_choice=True).count(),
            'negative': Vote_Document.objects.filter(document=document, style_choice=False).count()
        },
        'background': {
            'positive': Vote_Document.objects.filter(document=document, background_choice=True).count(),
            'negative': Vote_Document.objects.filter(document=document, background_choice=False).count()
        },
    }
    return JsonResponse({
        'success': True,
        'stats':stats,
        'new_vote': {  # 新增当前用户的最新选择
            'fact': vote.fact_choice,
            'style': vote.style_choice,
            'background': vote.background_choice
            } 
 })  # 统计更新交给信号处理
