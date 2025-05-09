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
        return JsonResponse({'error': 'please login first'}, status=403)

    # parase choice
    def parse_choice(value):
        return {'positive': True, 'negative': False}.get(value, None)
    
    data = {
        'fact': request.POST.get('fact'),
        'style': request.POST.get('style'),
        'background': request.POST.get('background')
    }

    # verify all choices are present
    if any(v is None for v in data.values()):
        return JsonResponse({'error': 'please finish all evaluation'}, status=400)

    # get or create vote
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
        'new_vote': {  
            'fact': vote.fact_choice,
            'style': vote.style_choice,
            'background': vote.background_choice
            } 
 }) 
