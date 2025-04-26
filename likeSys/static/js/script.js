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
            const resp = await fetch(form.action, {
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
