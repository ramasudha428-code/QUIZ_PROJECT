/**
 * PARTICLE NETWORK — Animated canvas background
 * Draws floating nodes connected by dynamic lines
 */
(function () {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W, H, particles, animId;
    const MAX_PARTICLES = 65;
    const CONNECTION_DISTANCE = 140;

    const COLORS = ['rgba(139,92,246,', 'rgba(6,182,212,', 'rgba(59,130,246,', 'rgba(236,72,153,'];

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    function randomColor(alpha) {
        return COLORS[Math.floor(Math.random() * COLORS.length)] + alpha + ')';
    }

    function createParticle() {
        return {
            x: Math.random() * W,
            y: Math.random() * H,
            vx: (Math.random() - 0.5) * 0.45,
            vy: (Math.random() - 0.5) * 0.45,
            r: Math.random() * 2 + 1,
            color: randomColor(Math.random() * 0.5 + 0.2),
            pulse: Math.random() * Math.PI * 2
        };
    }

    function init() {
        resize();
        particles = Array.from({ length: MAX_PARTICLES }, createParticle);
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);

        // Update and draw particles
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.pulse += 0.03;

            // Wrap edges
            if (p.x < 0) p.x = W;
            if (p.x > W) p.x = 0;
            if (p.y < 0) p.y = H;
            if (p.y > H) p.y = 0;

            // Draw glowing dot
            const glow = Math.sin(p.pulse) * 0.5 + 1;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r * glow, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = p.color;
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const a = particles[i], b = particles[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECTION_DISTANCE) {
                    const alpha = (1 - dist / CONNECTION_DISTANCE) * 0.25;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.strokeStyle = `rgba(139,92,246,${alpha})`;
                    ctx.lineWidth = 0.7;
                    ctx.stroke();
                }
            }
        }

        animId = requestAnimationFrame(draw);
    }

    window.addEventListener('resize', () => {
        cancelAnimationFrame(animId);
        init();
        draw();
    });

    init();
    draw();
})();
