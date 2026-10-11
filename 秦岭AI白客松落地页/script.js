/**
 * 秦岭AI白客松 5.0 — 交互脚本
 * 山野手作 × 野生朋克
 */

(function () {
  'use strict';

  /* ── 入场动画（Intersection Observer） ── */
  function initReveal() {
    const els = document.querySelectorAll('.reveal, .reveal-stagger');
    if (!els.length) return;

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    els.forEach((el) => io.observe(el));
  }

  /* ── 告警条打字机效果 ── */
  function initTyping() {
    const el = document.querySelector('[data-typing]');
    if (!el) return;

    const text = el.textContent.trim();
    el.textContent = '';
    let i = 0;

    function type() {
      if (i < text.length) {
        el.textContent += text[i];
        i++;
        setTimeout(type, 45 + Math.random() * 30);
      }
    }

    // 等页面加载完再打
    if (document.readyState === 'complete') {
      setTimeout(type, 800);
    } else {
      window.addEventListener('load', () => setTimeout(type, 800));
    }
  }

  /* ── Header 滚动样式 ── */
  function initHeader() {
    const hdr = document.querySelector('.site-hdr');
    if (!hdr) return;

    let lastY = 0;
    let ticking = false;

    function update() {
      const y = window.scrollY;
      hdr.classList.toggle('is-scrolled', y > 40);
      hdr.classList.toggle('is-hidden', y > lastY + 5 && y > 200);
      hdr.classList.toggle('is-visible', y <= lastY || y < 200);
      lastY = y;
      ticking = false;
    }

    window.addEventListener(
      'scroll',
      () => {
        if (!ticking) {
          requestAnimationFrame(update);
          ticking = true;
        }
      },
      { passive: true }
    );
  }

  /* ── Hero 入场动画 + 背景视差 ── */
  function initHero() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    const bgImg = hero.querySelector('.hero__bg-img');
    const title = hero.querySelector('.hero__title');
    const aside = hero.querySelector('.hero__aside');
    const topbar = hero.querySelector('.hero__topbar');
    const kicker = hero.querySelector('.hero__kicker');
    const lead = hero.querySelector('.hero__lead');
    const actions = hero.querySelector('.hero__actions');
    const stats = hero.querySelector('.hero__stats');

    // 入场动画序列
    const items = [topbar, kicker, title, lead, actions, stats];
    items.forEach((el, i) => {
      if (!el) return;
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s ease, transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
      setTimeout(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
      }, 300 + i * 120);
    });

    if (aside) {
      aside.style.opacity = '0';
      aside.style.transform = 'translateX(20px)';
      aside.style.transition = 'opacity 0.6s ease 0.9s, transform 0.6s ease 0.9s';
      setTimeout(() => {
        aside.style.opacity = '1';
        aside.style.transform = 'translateX(0)';
      }, 900);
    }

    // 背景图视差
    if (bgImg) {
      hero.addEventListener('mousemove', (e) => {
        const dx = (e.clientX / window.innerWidth - 0.5) * 12;
        const dy = (e.clientY / window.innerHeight - 0.5) * 8;
        bgImg.style.transform = `scale(1.05) translate(${dx}px, ${dy}px)`;
      });
      hero.addEventListener('mouseleave', () => {
        bgImg.style.transform = 'scale(1) translate(0, 0)';
      });
    }
  }

  /* ── 滚动时显示/隐藏 Sticky CTA ── */
  function initStickyCta() {
    const sticky = document.querySelector('.sticky-cta');
    if (!sticky) return;

    const joinSection = document.querySelector('#join');
    let lastY = 0;

    function update() {
      const y = window.scrollY;
      const joinTop = joinSection ? joinSection.getBoundingClientRect().top + y : Infinity;

      // 滚动超过一屏才显示
      if (y > window.innerHeight * 0.8) {
        sticky.classList.add('is-visible');
      } else {
        sticky.classList.remove('is-visible');
      }

      // 进入 join 区域隐藏
      if (y >= joinTop - 200) {
        sticky.classList.add('is-near-join');
      } else {
        sticky.classList.remove('is-near-join');
      }
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* ── 导航高亮 ── */
  function initNavHighlight() {
    const links = document.querySelectorAll('.hdr-nav__link');
    if (!links.length) return;

    const sections = Array.from(links)
      .map((l) => document.querySelector(l.getAttribute('href')))
      .filter(Boolean);

    function update() {
      const y = window.scrollY + 80;

      let active = null;
      for (const sec of sections) {
        if (sec.offsetTop <= y) {
          active = sec;
        }
      }

      links.forEach((link) => {
        const href = link.getAttribute('href');
        link.classList.toggle('is-active', active && active.id === href.slice(1));
      });
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* ── Manifesto 卡片 3D 倾斜效果 ── */
  function initCardTilt() {
    const cards = document.querySelectorAll('.m-card, .s-panel, .w-stage, .e-card');

    cards.forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) / (rect.width / 2);
        const dy = (e.clientY - cy) / (rect.height / 2);

        card.style.transform = `
          perspective(800px)
          rotateY(${dx * 4}deg)
          rotateX(${-dy * 3}deg)
          translate(-2px, -2px)
        `;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  }

  /* ── 平滑滚动（以防 CSS scroll-behavior 不够用） ── */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', (e) => {
        const target = document.querySelector(anchor.getAttribute('href'));
        if (!target) return;

        e.preventDefault();
        const top = target.getBoundingClientRect().top + window.scrollY - 38;
        window.scrollTo({ top, behavior: 'smooth' });
      });
    });
  }

  /* ── 初始化 ── */
  function init() {
    initReveal();
    initTyping();
    initHeader();
    initHero();
    initStickyCta();
    initNavHighlight();
    initCardTilt();
    initSmoothScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
