# Django 多维度文章评价系统 - 开发文档
## 目录
* [概述](#1-概述)
* [功能特性](#2-功能特性)
* [开发环境](#3-开发环境)
* [技术实现](#3-开发环境)
* [数据库迁移](#4-数据库迁移)
* [部署与配置](#5-部署与配置)
* [常见问题排查](#6-常见问题排查)
## 1. 概述

本项目旨在为一个 Django 应用添加一个可移植的多用户、多维度文章评价系统。用户可以对系统中的“文档”（例如文章、帖子等）从**事实准确性 (Fact)**、**写作风格 (Style)** 和**背景信息 (Background)** 三个维度进行评价，每个维度都可以选择“积极 (Positive)”或“消极 (Negative)”两种倾向。系统会记录每个用户的具体评价，并实时统计每篇文章在各个维度上的总体评价情况。

## 2. 功能特性

* **多维度评价**: 支持对单一文档进行事实、文风、背景三个维度的独立评价。  
* **二元倾向**: 每个维度提供积极/消极两种评价选项。  
* **用户特定评价**: 系统记录每个用户对每篇文档的评价，防止重复评价，并允许用户修改评价。  
* **实时统计**: `Document` 模型实时聚合显示各维度的积极/消极评价总数。  
* **前端交互**: 提供直观的前端界面，用户点击按钮即可选择评价，并通过 AJAX 提交，无需刷新页面。

## 3. 开发环境
Ubuntu/WSL2
示例Django项目所用版本为4.2.11
`python -m pip install django==5.2`
Nginx挂载Django

# 项目目录(以本项目为例)
```
.        #项目当前目录
├── db.sqlite2   # 旧数据库文件（可考虑清理）
├── db.sqlite3   # 当前使用的数据库
├── manage.py
├── likeSys/    #应用根目录
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── media/
│   │   └── user_<id>/
│   │       └── [上传文件若干]
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py     #模型定义文件
│   ├── signals.py    #信号文件
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── documents/
│   │   └── js/
│   │       └── script.js #主要逻辑文件
│   ├── templates/
│   │   └── documents/
│   │       └── detail.html #模板文件
│   ├── tests.py
│   ├── urls.py    #路由文件
│   └── views.py   #视图文件
└── Multi_DLsys/   #项目配置文件目录
    ├── asgi.py
    ├── __init__.py
    ├── settings.py     #主配置文件
    ├── urls.py
    └── wsgi.py


```

## 4. 技术实现

### 基础配置 
#### Multi_DLsys/settings.py

```python
#设置项目根目录变量
BASE_DIR = Path(__file__).resolve().parent.parent

#应用根目录变量
#APP_DIR
APP_DIR = BASE_DIR / "likeSys"

#静态文件和媒体文件的URL前缀
#URL
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
TARGET_URL = '/Django/'#挂载在Nginx的 `servername/Django/` 实现反向代理
#媒体文件和静态文件的本地存储路径
#others
MEDIA_ROOT = APP_DIR / 'media'
STATICFILES_DIRS = [APP_DIR / "static"]
STATIC_ROOT = APP_DIR / "staticfiles"

```

#### Nginx配置示例
###### nginx.conf
```nginx
events {}

http{
    include mime.types;
    include ./conf.d/*.conf;
}

```

###### conf.d/base.conf

```nginx

server{
    listen 80;
    server_name localhost;#your domain
    
    root /var/www/html/;
    location / {
        index base.html;
    }

     location /static/ {
        alias /srv/Multi_dimensionLikes/likeSys/staticfiles/;
    }

    location /Django/{
        proxy_pass http://0.0.0.0:8000/;  # 指向 Django 服务地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme; 
    }
}

```
以上配置可以根据需要自己设定,尤其是注意配置中设定的路径已经存在
### 4.1 后端 (Django)

#### 4.1.1 数据模型 (Models)

**a) 导入和User路径**

为了存储每个文档的评价统计信息，我们在现有的 `Document` 模型中添加了以下字段：

```python  
# models.py  
from django.db import models  
# from accounts.models import CustomUser
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings # 用于获取 AUTH_USER_MODEL,可使用自定义用户模型


def user_directory_path(instance, filename):
    # 文件将上传到 MEDIA_ROOT/user_<id>/<filename> 生成用户文件的上传路径
    return f'user_{instance.user.id}/{filename}'

```


**b) 模型CustomUser**

```python
class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    groups = models.ManyToManyField(
    'auth.Group',
    related_name='customuser_set',
    blank=True,
    verbose_name='groups',
    help_text='The groups this user belongs to. A user will get allpermissions granted to each of their groups.',
)
    user_permissions = models.ManyToManyField(
    'auth.Permission',
    related_name='customuser_set',
    blank=True,
    help_text='Specific permissions for this user.',
    verbose_name='user permissions',
)
    def __str__(self):
        return f"{self.username}"

```
**以下是代码摘要和分析**


```python
related_name='customuser_set',
```
* related_name: 方便从 User 或 Document 反向查询


```python
groups = models.ManyToManyField( ...)
```
采用Django自带的`groups`,实现用户与组的关联，支持权限继承，简化权限管理

```python
def __str__(self):
        return f"{self.username}"
```
为admin模块提供更加方便的反馈

**c) 模型Document**

```python
class Document(models.Model):  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    # file = models.FileField(upload_to=user_directory_path,storage=DocumentStorage())
    file = models.FileField(upload_to=user_directory_path)
    upload_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    public = models.BooleanField(default=False)


   
    fact_positive = models.PositiveIntegerField(default=0, editable=False, help_text="事实积极评价数")  
    fact_negative = models.PositiveIntegerField(default=0, editable=False, help_text="事实消极评价数")

   
    style_positive = models.PositiveIntegerField(default=0, editable=False, help_text="文风积极评价数")  
    style_negative = models.PositiveIntegerField(default=0, editable=False, help_text="文风消极评价数")

    
    background_positive = models.PositiveIntegerField(default=0, editable=False, help_text="背景积极评价数")  
    background_negative = models.PositiveIntegerField(default=0, editable=False, help_text="背景消极评价数")

    def __str__(self):  
        return self.title
```

**以下是代码摘要和分析**


```python
 id = models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
```
对`id`进行主键约束,不可编辑
```python
    # file = models.FileField(upload_to=user_directory_path,storage=DocumentStorage())
    file = models.FileField(upload_to=user_directory_path)
```
可以通过`storage`参数自定义存储位置,或者使用默认位置



```python
    fact_positive = models.PositiveIntegerField(default=0, editable=False, help_text="事实积极评价数")  
    fact_negative = models.PositiveIntegerField(default=0, editable=False, help_text="事实消极评价数")

   
    style_positive = models.PositiveIntegerField(default=0, editable=False, help_text="文风积极评价数")  
    style_negative = models.PositiveIntegerField(default=0, editable=False, help_text="文风消极评价数")

    
    background_positive = models.PositiveIntegerField(default=0, editable=False, help_text="背景积极评价数")  
    background_negative = models.PositiveIntegerField(default=0, editable=False, help_text="背景消极评价数")
```
* 核心属性,用于统计每一个维度的评价数量

```python
public = models.BooleanField(default=False)
```
* 文章默认不公开


```python
  def __str__(self):  
        return self.title
```
* 为admin模块提供更加方便的反馈


**d) Vote_Document 评价模型**

这个模型用于记录每个用户对特定文档的评价信息(一对一)。


```python 
class Vote_Document(models.Model):  
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    fact_choice = models.BooleanField()  # True=积极，False=消极
    style_choice = models.BooleanField()
    background_choice = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ 保存前记录旧值 """
        if self.pk:  # 仅限更新操作
            old_instance = Vote_Document.objects.get(pk=self.pk)
            self._old_values = {
                'fact': old_instance.fact_choice,
                'style': old_instance.style_choice,
                'background': old_instance.background_choice
            }
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'document')  # 确保唯一评价

    def __str__(self):
        return f"Vote by {self.user.username} on {self.document.name}"
```

**以下是代码摘要和分析**


```python
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
```
* 通过外键连接特定的用户和文章实体
* `on_delete=models.CASCADE`来实现绑定,绑定的实体被删除时,自己也被删除


```python
if self.pk:
```
* 检查当前实例是否已经存在（即是否有主键pk）
* 如果存在，说明是更新操作，而不是新建实例


```python
old_instance = Vote_Document.objects.get(pk=self.pk)
```
* 从数据库中获取当前实例的旧值（更新前的值），并将其存储在old_instance变量中


```python
self._old_values = {
                'fact': old_instance.fact_choice,
                'style': old_instance.style_choice,
                'background': old_instance.background_choice
            }
```
* 存储旧值


```python
super().save(*args, **kwargs)
```
* 存储到数据库中
```python
class Meta:  
        # 确保每个用户对同一文档只有一条评价记录  
        unique_together = ('user', 'document')  
        ordering = ['-created_at']
```


```python
    def __str__(self):
        return f"Vote by {self.user.username} on {self.document.name}"
```
* 为admin模块提供遍历



#### **4.1.2 视图逻辑 (Views)**

**a) 显示文档及评价状态 (document_detail)**

此视图负责展示文档内容以及当前登录用户的评价状态（如果已评价）。

```python
# views.py  
from django.shortcuts import render, get_object_or_404  
from django.contrib.auth.decorators import login_required  
from .models import Document, Vote_Document

@login_required # 确保用户已登录  
def document_detail(request, doc_id):  
    document = get_object_or_404(Document, id=doc_id)  
    vote = None # 默认为 None  
    if request.user.is_authenticated:  
        try:  
            # 获取当前用户对该文档的评价记录  
            vote = Vote_Document.objects.get(user=request.user, document=document)  
        except Vote_Document.DoesNotExist:  
            vote = None # 用户未评价

    context = {  
        'document': document,  
        'vote': vote  
    }  
    return render(request, 'documents/detail.html', context)
```

**b) 处理评价提交 (submit_rating)**

此视图处理来自前端的 AJAX POST 请求，用于创建或更新用户的评价，并同步更新 Document 的统计字段。

```python
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

    # 保存评价
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
    #手动更新
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
```

```python
def document_detail(request, doc_id):
```
* 接收HTTP请求和doc_id,返回渲染的模板


```python
def submit_rating(request, doc_id):
```
* 接收POST请求
* 验证是否登录
* 解析三个维度的数据并保存
* 手动更新并返回当前文档的统计信息

```python
@require_http_methods(["POST"])
@transaction.atomic
```
* `@require_http_methods(["POST"])`限制视图函数仅允许POST请求
* `@transaction.atomic`确保数据库操作在事务中执行，保证原子性
*提交评价






#### **4.1.3 URL 配置 (urls.py)**

需要为上述视图配置 URL。
##### 项目级urls.py
```python
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from likeSys import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('likeSys/',include('likeSys.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


```
* 如果需要将该项目植入到你的项目中,需要对该文件做以下配置:

```python
path('likeSys/',include('likeSys.urls')),
```
* 引入likeSys路由,挂载应用

```python
  ##### ⭐ 加上这一行，确保 media 文件可以被访问
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### documents/urls.py (或者你的应用级 urls.py)  

```python
# likeSys/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('documents/<uuid:doc_id>/', views.document_detail, name='document_detail'),
    path('documents/<uuid:doc_id>/submit_rating/', views.submit_rating, name='submit_rating'),
]
```
* 第一个模式匹配documents/<doc_id>/路径，调用views.document_detail函数
* 第二个模式匹配documents/<doc_id>/submit_rating/路径，调用views.submit_rating函数



### **4.2 前端 (HTML, CSS, JavaScript)**

#### **4.2.1 HTML 模板结构 (templates/documents/detail.html)**

```html
<!DOCTYPE html>
<html>
<head>
    <title>文档评价</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <h1>{{ document.name }}</h1>

    <div class="user-info">
        {% if user.is_authenticated %}
            Welcome，{{ user.username }}！
        {% else %}
            Visitor
        {% endif %}
    </div>

    <div class="rating-container">
        <form id="rating-form" method="post" action="{{TARGET_URL}}{% url 'submit_rating' document.id %}">
            {% csrf_token %}
            <input type="hidden" id="vote-submitted" value="{% if user_vote %}true{% else %}false{% endif %}">

            <div class="rating-columns">
                <div class="rating-column fact">
                    <button type="button" data-dimension="fact" data-value="positive"
                        class="btn {% if user_vote and user_vote.fact_choice %}active positive{% endif %}">✓ fact_positive</button>
                    <div class="stats">
                        <span class="positive-count">{{ document.fact_positive }}</span>
                    </div>
                    <button type="button" data-dimension="fact" data-value="negative"
                        class="btn {% if user_vote and not user_vote.fact_choice %}active negative{% endif %}">✗ fact_negative</button>
                    <div class="stats">
                        <span class="negative-count">{{ document.fact_negative }}</span>
                    </div>
                </div>

                <div class="rating-column style">
                    <button type="button" data-dimension="style" data-value="positive"
                        class="btn {% if user_vote and user_vote.style_choice %}active positive{% endif %}">✓ style_positive</button>
                    <div class="stats">
                        <span class="positive-count">{{ document.style_positive }}</span>
                    </div>
                    <button type="button" data-dimension="style" data-value="negative"
                        class="btn {% if user_vote and not user_vote.style_choice %}active negative{% endif %}">✗ style_negative</button>
                    <div class="stats">
                        <span class="negative-count">{{ document.style_negative }}</span>
                    </div>
                </div>

                <div class="rating-column background">
                    <button type="button" data-dimension="background" data-value="positive"
                        class="btn {% if user_vote and user_vote.background_choice %}active positive{% endif %}">✓ background_positive</button>
                    <div class="stats">
                        <span class="positive-count">{{ document.background_positive }}</span>
                    </div>
                    <button type="button" data-dimension="background" data-value="negative"
                        class="btn {% if user_vote and not user_vote.background_choice %}active negative{% endif %}">✗ background_negative</button>
                    <div class="stats">
                        <span class="negative-count">{{ document.background_negative }}</span>
                    </div>
                </div>
            </div>

            <div class="submit-btn-wrapper">
                <button type="submit" class="submit-btn">confirm</button>
            </div>
        </form>
    </div>
<script>
    const TARGET_URL = "{{ TARGET_URL }}";
</script>
    <script src="/static/js/script.js"></script>
</body>
</html>


```
* `{% csrf_token %}`: 必须包含，用于 Django 的 `CSRF` 保护。  
* `data-dimension`, `data-value`: 自定义数据属性，方便 JavaScript 获取按钮的维度和值。  
* `{% if vote ... %}`: 根据后端传来的 `vote` 对象，初始化按钮的 `active` 状态。  
* 隐藏的 `input` 字段: 用于在提交时携带选中的值。  
* `submit-rating-btn`: 提交按钮，初始时禁用。  
* `rating-message`: 用于显示 AJAX 提交后的反馈信息。  
* `stats-display`: 用于显示和更新统计数据。
* `TARGET_URL`:在模板中使用` {{ BASE_URL }} `动态插入正确的 URL 前缀
#### **4.2.2 JavaScript 交互逻辑 (static/js/rating_script.js)**


```javascript

// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rating-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const voteSubmittedInput = document.getElementById('vote-submitted');
    const selected = { fact: null, style: null, background: null };

    // 1. 初始化按钮状态
    const hasVote = voteSubmittedInput.value === 'true';
    if (hasVote) {
        submitBtn.textContent = '已提交';
        submitBtn.disabled = true;
    } else {
        submitBtn.textContent = '确认评价';
        submitBtn.disabled = false;
    }

    // 2. 读取初始选中状态
    document.querySelectorAll('.rating-column button').forEach(btn => {
        if (btn.classList.contains('active')) {
            selected[btn.dataset.dimension] = btn.dataset.value;
        }

        // 3. 点击评分按钮：高亮、记录、启用“确认评价”
        btn.addEventListener('click', function() {
            const dim = this.dataset.dimension;
            const val = this.dataset.value;

            // 切换高亮
            this.closest('.rating-column').querySelectorAll('button').forEach(b => {
                b.classList.remove('active','positive','negative');
            });
            this.classList.add('active', val);

            // 记录选择
            selected[dim] = val;

            // 启用提交
            submitBtn.textContent = '确认评价';
            submitBtn.disabled = false;
            voteSubmittedInput.value = 'false';  // 标记为“未提交”
        });
    });

    // 4. 表单提交逻辑
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        // 验证
        if (['fact','style','background'].some(dim => !selected[dim])) {
            alert('请完成所有维度的评价！');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';

        try {
            const payload = new URLSearchParams({
                csrfmiddlewaretoken: form.querySelector('[name=csrfmiddlewaretoken]').value,
                ...selected
            });
            const resp = await fetch(TARGET_URL+form.action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: payload
            });
            const result = await resp.json();

            if (result.success) {
                // 更新统计和按钮状态
                updateStatsDisplay(result.stats);
                refreshVoteStatus(result.new_vote);

                submitBtn.textContent = '已提交';
                voteSubmittedInput.value = 'true';  // 标记为“已提交”
            } else {
                alert(result.error || '提交失败');
                submitBtn.textContent = '确认评价';
                submitBtn.disabled = false;
            }
        } catch (err) {
            console.error(err);
            alert('网络错误，请稍后再试');
            submitBtn.textContent = '确认评价';
            submitBtn.disabled = false;
        }
    });
});

// 以下保持不变
function refreshVoteStatus(new_vote) {
    document.querySelectorAll('.rating-column button').forEach(btn => {
        btn.classList.remove('active','positive','negative');
    });
    Object.entries(new_vote).forEach(([dim, choice]) => {
        const val = choice ? 'positive' : 'negative';
        const btn = document.querySelector(`.${dim} button[data-value="${val}"]`);
        if (btn) btn.classList.add('active', val);
    });
}

function animateCountUpdate(span, newValue) {
    if (parseInt(span.textContent) !== newValue) {
        span.textContent = newValue;
        span.classList.add('count-updated');
        setTimeout(() => span.classList.remove('count-updated'), 400);
    }
}

function updateStatsDisplay(stats) {
    animateCountUpdate(document.querySelector('.fact .positive-count'), stats.fact.positive);
    animateCountUpdate(document.querySelector('.fact .negative-count'), stats.fact.negative);
    animateCountUpdate(document.querySelector('.style .positive-count'), stats.style.positive);
    animateCountUpdate(document.querySelector('.style .negative-count'), stats.style.negative);
    animateCountUpdate(document.querySelector('.background .positive-count'), stats.background.positive);
    animateCountUpdate(document.querySelector('.background .negative-count'), stats.background.negative);
}

```

**以下是代码摘要和分析**


```javascript
document.addEventListener('DOMContentLoaded', function() {...
}
```

* **整体功能:** 这是脚本的主入口点。当整个 HTML 页面加载并解析完毕后，这个函数内的代码会执行
* 它负责初始化页面状态、绑定事件监听器到评分按钮和表单。


  ```javascript
  const submitBtn = form.querySelector('button[type="submit"]');
  const voteSubmittedInput = document.getElementById('vote-submitted');
  ```
 **数据接收:**  
  * 读取 DOM 元素：获取表单 (#rating-form)、提交按钮 (button[type="submit"])、隐藏的投票状态输入框 (#vote-submitted) 以及所有评分按钮 (.rating-column button)。  
  * 读取初始状态：从 #vote-submitted 输入框读取用户是否已提交过投票 ('true' 或 'false')。  


  ```javascript
if (btn.classList.contains('active')) {
            selected[btn.dataset.dimension] = btn.dataset.value;
        }
```

* 读取初始选中：检查评分按钮是否有 active 类
* 如果有，则将其 data-dimension 和 data-value 存入 selected 对象。


```javascript
 if (hasVote) {
        submitBtn.textContent = '已提交';
        submitBtn.disabled = true;
    } else {
        submitBtn.textContent = '确认评价';
        submitBtn.disabled = false;
    }
```
  * 初始化按钮状态：根据读取到的 hasVote 状态
  * 设置提交按钮的文本（“确认评价”或“已提交”）和 disabled 属性。


```javascript
 btn.addEventListener('click', function() {
            const dim = this.dataset.dimension;
            const val = this.dataset.value;
```
* **功能:** 当用户点击某个评分按钮（例如，“事实 - 正面”按钮）时触发
* 它负责更新按钮的视觉高亮状态，记录用户的选择，并重置提交按钮的状态，允许用户提交或修改评价。  
* **数据接收:**  
  * 从被点击按钮的 `dataset` 属性中读取维度 `(dimension)` 和评价值 (value, 即 'positive' 或 'negative')。  


```javascript
        this.closest('.rating-column').querySelectorAll('button').forEach(b => {
                b.classList.remove('active','positive','negative');
            });
          this.classList.add('active', val);

            // 记录选择
            selected[dim] = val;
```
**数据处理/返回:**  
  * 更新 DOM：移除同维度下所有按钮的高亮类` (active, positive, negative)`，
  * 然后给被点击的按钮添加 `active` 和对应的评价类 `(positive 或 negative)`。  
  * 更新 `selected JavaScript` 对象：将当前维度 `(dim)` 的值更新为用户新选择的值 (val)。  


```javascript
form.addEventListener('submit', async function(e) {...
}
```
**功能:** 当用户点击“确认评价”按钮提交表单时触发
* 它负责验证用户是否已完成所有维度的评价
* 然后将评价数据异步发送到服务器，并根据服务器的响应更新页面


```javascript
if (['fact','style','background'].some(dim => !selected[dim])) {
            alert('请完成所有维度的评价！');
            return;
        }
```
* **验证:** 检查 selected 对象，确保 'fact', 'style', 'background' 都有值
* 如果没有，显示 alert 提示，阻止提交。


```javascript
  const payload = new URLSearchParams({
                csrfmiddlewaretoken: form.querySelector('[name=csrfmiddlewaretoken]').value,
                ...selected
            });
            const resp = await fetch(TARGET+form.action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: payload
            });
```
  * **准备发送数据:** 创建一个 URLSearchParams 对象` (payload)`
  * 包含 `CSRF` 令牌和 `selected` 对象中的所有评价数据（`fact`, `style`, `background` 及其对应的值 'positive'/'negative'）。  
  * **发送数据 (异步请求):** 使用 Workspace API 向表单的` action URL `发送一个 POST 请求
  * 请求头设置为 application/x-www-form-urlencoded，请求体为 `payload`。
  * `TARGET+form.action `利用该变量拼接请求路径。 
  * **接收服务器响应:** `await` 等待服务器返回响应
  * 并使用` resp.json() `解析返回的 JSON 数据 `(result)`
  * 预期 `result` 包含 `success` (布尔值), `stats` (包含各维度统计数据的对象),
  * `new_vote` (包含刚提交的投票详情的对象), 可能还有 error (字符串)


```javascript
if (result.success) {
                // 更新统计和按钮状态
                updateStatsDisplay(result.stats);
                refreshVoteStatus(result.new_vote);

                submitBtn.textContent = '已提交';
                voteSubmittedInput.value = 'true';  // 标记为“已提交”
            } else {
                alert(result.error || '提交失败');
                submitBtn.textContent = '确认评价';
                submitBtn.disabled = false;
            }
```
 **处理响应 (成功):** 如果 result.success 为 true：  
    * 调用` updateStatsDisplay(result.stats)`，将从服务器接收到的最新统计数据 `(result.stats)` 传递给它，用于更新页面上的统计数字。  
    * 调用 `refreshVoteStatus(result.new_vote)`
    将从服务器接收到的用户最新投票数据 `(result.new_vote)` 传递给它
    用于更新按钮的高亮状态以反映已提交的投票 
    * 更新提交按钮状态为“已提交”并禁用
    * 更新隐藏输入框 #vote-submitted 的值为 'true'
  * **处理响应 (失败):** 如果 `result.success` 为 `false` 或 `Workspace 出错`：  
    * 显示包含错误信息的 alert (优先使用 result.error，否则显示通用错误信息)
    * 将提交按钮重置回“确认评价”状态并启用


```javascript
function refreshVoteStatus(new_vote) {...
}
```
 **功能:** 根据传入的最新投票数据，刷新评分按钮的视觉高亮状态，使其准确反映当前已提交的投票。  
* **数据接收:** 接收一个 `new_vote` 对象作为参数
* 这个对象通常来自服务器响应，格式类似 { fact: true, style: false, background: true }
* **数据处理/返回:**  
  * 清除所有评分按钮的 `active`, `positive`, `negative` 类。  
  * 遍历 `new_vote` 对象
  * 对于每个维度 (`dim`) 和对应的选择 (choice - true/false)，确定值是 'positive' 还是 'negative'。  
  * 找到对应的按钮（例如，.fact button[data-value="positive"]）
  * 并给它添加 `active` 和对应的评价类 ('positive' 或 'negative')。  
  * 此函数不直接返回值，其效果是修改 DOM 中按钮的样式。


```javascript
function animateCountUpdate(span, newValue) {...
}
```
* **功能:** 平滑地更新页面上某个 <span> 元素显示的数字
* 并添加一个短暂的动画效果（通过 CSS 类）。  
* **数据接收:** 接收两个参数：span (需要更新的 DOM 元素) 和 newValue (要显示的新数值)。  
* **数据处理/返回:**  
  * 比较 span 当前显示的文本内容（转换为整数）和 newValue  
  * 如果值不同，则更新 span 的 textContent 为 newValue
  * 给 span 添加 count-updated CSS 类（触发动画），并在 400 毫秒后移除该类 
  * 此函数不直接返回值，其效果是修改 DOM 中 span 的文本内容和类


```javascript
function updateStatsDisplay(stats) {...
}
```
* **功能:** 接收包含所有维度统计数据的对象
* 并调用 `animateCountUpdate` 来更新页面上显示的各个统计数字（正面评价数和负面评价数)
* 此函数不直接返回值，其效果是通过调用 `animateCountUpdate` 来修改 DOM 中多个统计数字 <span> 的显示。
  






#### **4.2.3 CSS 样式设计 (static/css/rating_styles.css)**

将 HTML 中 <style> 标签内的 CSS 规则移到这个单独的文件中，或者根据需要进行扩展和美化。
```css
/* static/css/rating_styles.css */  
.rating-container {
    max-width: 600px;
    margin: 20px auto;
}

.rating-column {
    display: inline-block;
    width: 30%;
    margin: 0 1%;
}

.btn {
    display: block;
    width: 100%;
    padding: 20px;
    margin: 10px 0;
    border: none;
    cursor: pointer;
    border-radius: 5px;
    transition: all 0.3s;
}

/* 默认颜色 */
.fact .btn { background-color: #e0f2e9; }
.style .btn { background-color: #e0f0ff; }
.background .btn { background-color: #e8e0ff; }

/* 选中状态 */
.btn.active.positive {
    background-color: #2ecc71 !important; /* 绿色 */
}
.fact .btn.active.positive { background-color: #27ae60; }
.style .btn.active.positive { background-color: #2980b9; }
.background .btn.active.positive { background-color: #8e44ad; }

.btn.active.negative {
    background-color: #e74c3c !important; /* 红色 */
}

.submit-btn {
    display: block;
    width: 200px;
    margin: 20px auto;
    padding: 20px;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 5px;
}
.btn.cancelled {
    background-color: #f0f0f0 !important;
    color: #666;
}
.user-info {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 10px 15px;
    background: #f8f9fa;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-info a {
    margin-left: 10px;
    color: #007bff;
}
.count {
    transition: all 0.3s ease;
    display: inline-block;
}

.count-updated {
    transform: scale(1.2);
    color: #3498db;
}

```

## **4. 数据库迁移**

在修改 models.py 后，需要运行以下命令来更新数据库结构：
```
python manage.py makemigrations your_app_name  
python manage.py migrate
```
## **5. 部署与配置**

* 确保 Django 项目正确配置了数据库。  
* 确保 settings.AUTH_USER_MODEL 指向正确的用户模型。      
* 确保静态文件 (rating_styles.css, rating_script.js) 正确收集和提供服务。  
* 在生产环境中，考虑使用更健壮的 Web 服务器（如 Nginx + Gunicorn/uWSGI）。

## **6. 常见问题排查**
| 问题 | 原因 | 解决方法 |
| :--- | :--- | :--- |
| 静态文件加载失败 | `STATICFILES_DIRS` 配置错误或未执行 `collectstatic` | 检查 `settings.py` 配置，或执行 `python manage.py collectstatic` |
| 提交评价按钮点击无反应 | JS 脚本未正确加载或发生报错 | 检查浏览器 Console，有无 404 错误或 JavaScript 报错 |
| 上传的文档不显示 | `MEDIA_URL` 未正确处理 | 检查项目级 `urls.py` 是否添加了 `urlpatterns += static(...)` |
| 投票无法保存 | CSRF 验证失败或表单字段异常 | 确保表单中有 `{% csrf_token %}`，并检查前端提交数据格式 |
| 静态文件加载错误（部署后） | Nginx 未正确挂载 `TARGET_URL`，请求未通过代理 | 检查 Nginx 配置中 `/static/` 映射，确认静态资源请求未误走 Django |
| 表单提交显示 "Network Error" | `fetch` 请求的 URL 路径错误，请求未到达 Django 后端 | 检查 JS 中 `submit` 函数是否使用了完整路径，可使用浏览器开发者工具调试 |


