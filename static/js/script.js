// script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rating-form');
    const selected = {
        fact: null,
        style: null,
        background: null
    };
// alert('9');

    document.querySelectorAll('.rating-column button').forEach(btn => {
        if (btn.classList.contains('active')) {
            const dim = btn.closest('.rating-column').classList[1];
            selected[dim] = btn.dataset.value;
        }
    });

    // 处理按钮点击（添加切换逻辑）
    document.querySelectorAll('.rating-column button').forEach(button => {
        button.addEventListener('click', function() {
            const dimension = this.parentElement.classList[1];
            const value = this.dataset.value;
           this.closest('.rating-column').querySelectorAll('button').forEach(b => {
                b.classList.remove('active', 'positive', 'negative');
            });

            // 更新选择
            this.classList.add('active', value);
            selected[dimension] = value;
        });
    });

// alert('34');
    // 处理表单提交（添加防重复提交）
    let isSubmitting = false;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const dimensions = ['fact', 'style', 'background'];
        if (dimensions.some(dim => !selected[dim])) {
            alert('请完成所有维度的评价！');
            return;
    }
    
        
        // alert('47');
        if (isSubmitting) return;
        isSubmitting = true;
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';


// alert('55');
        try {
            // 构建有效负载（允许空值）
            const payload = new URLSearchParams({
                csrfmiddlewaretoken: form.querySelector('[name=csrfmiddlewaretoken]').value,
                ...selected
            });

            const response = await fetch(form.action, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: payload
            });

            // alert('69');
            const result = await response.json();
            if (result.success) {
                updateStatsDisplay(result.stats); // 新增统计更新
                refreshVoteStatus(result.new_vote); 
                // showSuccessNotification();
            } else {
                alert(result.error || '提交失败');
            }
        } catch (error) {
            console.error('提交错误:', error);
                } finally {
            isSubmitting = false;
            submitBtn.disabled = false;
            submitBtn.textContent = '确认评价';
        }
    });
});
function refreshVoteStatus(new_vote) {
    // 清空所有选择
    document.querySelectorAll('.rating-column button').forEach(btn => {
        btn.classList.remove('active', 'positive', 'negative');
    });

    // 设置新状态
    Object.entries(new_vote).forEach(([dim, choice]) => {
        const value = choice ? 'positive' : 'negative';
        const btn = document.querySelector(`.${dim} button[data-value="${value}"]`);
        if (btn) {
            btn.classList.add('active', value);
        }
    });
}
function updateStatsDisplay(stats) {
    // 更新事实维度
    document.querySelector('.fact .positive-count').textContent = stats.fact.positive;
    document.querySelector('.fact .negative-count').textContent = stats.fact.negative;
    
    // 更新文风维度
    document.querySelector('.style .positive-count').textContent = stats.style.positive;
    document.querySelector('.style .negative-count').textContent = stats.style.negative;
    
    // 更新背景维度
    document.querySelector('.background .positive-count').textContent = stats.background.positive;
    document.querySelector('.background .negative-count').textContent = stats.background.negative;
}