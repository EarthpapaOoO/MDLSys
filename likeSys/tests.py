from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, Document, Vote_Document

class ModelTests(TestCase):
    def test_create_document(self):
        user = CustomUser.objects.create_user(username='testuser', password='12345')
        doc = Document.objects.create(
            user=user,
            name="测试文档",
            public=True
        )
        self.assertEqual(doc.name, "测试文档")

class ViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.doc = Document.objects.create(user=self.user, name="测试文档")

    def test_document_detail_view(self):
        # 未登录用户访问
        response = self.client.get(reverse('document_detail', args=[self.doc.id]))
        self.assertEqual(response.status_code, 302)  # 应重定向到登录页

        # 登录用户访问
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('document_detail', args=[self.doc.id]))
        self.assertContains(response, "测试文档")

    def test_rating_submission(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('submit_rating', args=[self.doc.id])
        
        # 正常提交
        response = self.client.post(url, {
            'fact': 'positive',
            'style': 'negative',
            'background': 'positive'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vote_Document.objects.exists())

        # 缺失参数提交
        response = self.client.post(url, {'fact': 'positive'})
        self.assertEqual(response.json()['error'], '请完成所有维度的评价')