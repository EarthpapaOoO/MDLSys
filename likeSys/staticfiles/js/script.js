// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('rating-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    const voteSubmittedInput = document.getElementById('vote-submitted');
    const selected = { fact: null, style: null, background: null };

   
    const hasVote = voteSubmittedInput.value === 'true';
    if (hasVote) {
        submitBtn.textContent = 'committed';
        submitBtn.disabled = true;
    } else {
        submitBtn.textContent = 'confirm your choices';
        submitBtn.disabled = false;
    }


    document.querySelectorAll('.rating-column button').forEach(btn => {
        if (btn.classList.contains('active')) {
            selected[btn.dataset.dimension] = btn.dataset.value;
        }

    
        btn.addEventListener('click', function() {
            const dim = this.dataset.dimension;
            const val = this.dataset.value;

            
            this.closest('.rating-column').querySelectorAll('button').forEach(b => {
                b.classList.remove('active','positive','negative');
            });
            this.classList.add('active', val);

          
            selected[dim] = val;

          
            submitBtn.textContent = 'confirm your choices';
            submitBtn.disabled = false;
            voteSubmittedInput.value = 'false';  
        });
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        if (['fact','style','background'].some(dim => !selected[dim])) {
            alert('Please complete all dimensions！');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'committing...';

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
                updateStatsDisplay(result.stats);
                refreshVoteStatus(result.new_vote);

                submitBtn.textContent = 'committed';
                voteSubmittedInput.value = 'true';  
            } else {
                alert(result.error || 'commit failed');
                submitBtn.textContent = 'confirm your choices';
                submitBtn.disabled = false;
            }
        } catch (err) {
            console.error(err);
            alert('NetWork Error');
            submitBtn.textContent = 'confirm your choices';
            submitBtn.disabled = false;
        }
    });
});

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
